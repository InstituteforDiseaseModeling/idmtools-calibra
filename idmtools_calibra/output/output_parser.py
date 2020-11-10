import gc  # for garbage collection
import json  # to read JSON output files
import logging
import os  # mkdir, path, etc.
import threading  # for multi-threaded job submission and monitoring
from io import StringIO, BytesIO
import pandas as pd  # for reading csv files
from COMPS.Data import QueryCriteria, Suite, Experiment
from idmtools.core import ItemType
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.utils.general import get_asset_for_comps_item

logger = logging.getLogger(__name__)
user_logger = logging.getLogger('user')


# TODO Remove this . Its very very very bad
def workdirs_from_simulations(sims):
    return {str(sim.id): sim.hpc_jobs[-1].working_directory for sim in sims if sim.hpc_jobs}


def sims_from_experiment(e):
    return e.get_simulations(QueryCriteria().select(['id', 'state']).select_children('hpc_jobs'))


def sims_from_experiment_id(exp_id):
    return Simulation.get(query_criteria=QueryCriteria().select(['id', 'state']).where('experiment_id=%s' % exp_id))


def workdirs_from_suite_id(suite_id):
    logger.debug('Simulation working directories for SuiteId = %s' % suite_id)
    s = Suite.get(suite_id)
    exps = s.get_experiments(QueryCriteria().select('id'))
    sims = []
    for e in exps:
        sims.extend(sims_from_experiment(e))
    return workdirs_from_simulations(sims)


def workdirs_from_experiment_id(exp_id, experiment=None):
    e = experiment or Experiment.get(exp_id)
    sims = sims_from_experiment(e)
    return workdirs_from_simulations(sims)


# End code to remove


class SimulationOutputParser(threading.Thread):
    def __init__(self, simulation, analyzers, semaphore=None, parse=True):
        threading.Thread.__init__(self)
        self.sim_id = simulation.id
        self._sim_path = None
        self.sim_data = simulation.tags
        self.experiment = simulation.experiment
        self.simulation = simulation
        self.analyzers = analyzers
        self.raw_data = {}
        self.selected_data = {}
        self.semaphore = semaphore
        self.parse = parse

    @property
    def sim_path(self):
        if not self._sim_path:
            self._sim_path = self.simulation.get_path()
        return self._sim_path

    def run(self):
        try:
            # list of output files needed by any analysis
            filenames = set()
            for a in self.analyzers:
                filenames.update(a.filenames)

            # parse output files for analysis
            self.load_all_files(filenames)

            # do sim-specific part of analysis on parsed output data
            for analyzer in self.analyzers:
                self.selected_data[id(analyzer)] = analyzer.apply(self)

            del self.raw_data
            gc.collect()  # clean up after apply()

        finally:
            if self.semaphore:
                self.semaphore.release()

    def get_path(self, filename):
        return os.path.join(self.get_sim_dir(), filename)

    def get_last_megabyte(self, filename):
        with open(self.get_path(filename)) as file:
            # Go to end of file.
            file.seek(0, os.SEEK_END)

            seekDistance = min(file.tell(), 1024 * 1024)
            file.seek(-1 * seekDistance, os.SEEK_END)

            return file.read()

    def load_all_files(self, filenames):
        for filename in filenames:
            self.load_single_file(filename)

    def load_single_file(self, filename, content=None):
        file_extension = os.path.splitext(filename)[1][1:].lower()

        if content is not None:
            content = BytesIO(content)
        else:
            with open(self.get_path(filename), 'rb') as output_file:
                content = BytesIO(output_file.read())

        if not self.parse:
            self.load_raw_file(filename, content)
        elif file_extension == 'json':
            logging.debug('reading JSON')
            self.load_json_file(filename, content)
        elif file_extension == 'csv':
            logging.debug('reading CSV')
            self.load_csv_file(filename, content)
        elif file_extension == 'xlsx':
            logging.debug('reading XLSX')
            self.load_xlsx_file(filename, content)
        elif file_extension == 'txt':
            logging.debug('reading txt')
            self.load_txt_file(filename, content)
        elif file_extension == 'bin' and 'SpatialReport' in filename:
            self.load_bin_file(filename, content)
        else:
            self.load_raw_file(filename, content)

    def load_json_file(self, filename, content):
        self.raw_data[filename] = json.load(content)

    def load_raw_file(self, filename, content):
        self.raw_data[filename] = content

    def load_csv_file(self, filename, content):
        if not isinstance(content, StringIO) and not isinstance(content, BytesIO):
            content = StringIO(content)

        csv_read = pd.read_csv(content, skipinitialspace=True)
        self.raw_data[filename] = csv_read

    def load_xlsx_file(self, filename, content):
        excel_file = pd.ExcelFile(content)
        self.raw_data[filename] = {sheet_name: excel_file.parse(sheet_name)
                                   for sheet_name in excel_file.sheet_names}

    def load_txt_file(self, filename, content):
        self.raw_data[filename] = str(content.getvalue().decode())

    def load_bin_file(self, filename, content):
        from idmtools_calibra.output.spatial_output import SpatialOutput
        if isinstance(content, BytesIO):
            so = SpatialOutput.from_bytes(content.read(), 'Filtered' in filename)
        else:
            so = SpatialOutput.from_bytes(content, 'Filtered' in filename)
        self.raw_data[filename] = so.to_dict()

    def get_sim_dir(self):
        return self.sim_path


class CompsOutputParser(SimulationOutputParser):
    sim_dir_map = None
    asset_service = True

    def __init__(self, platform, simulation, analyzers, semaphore=None, parse=True):
        self.platform: IPlatform = platform
        super(CompsOutputParser, self).__init__(simulation, analyzers, semaphore, parse)
        self.simulation: Simulation = platform.get_item(self.sim_id, ItemType.SIMULATION)
        self.COMPS_simulation = self.simulation.get_platform_object()

    @classmethod
    def create_sim_directory_map(cls, exp_id=None, suite_id=None, save=True, comps_experiment=None, verbose=True):
        if suite_id and not exp_id:
            sim_map = workdirs_from_suite_id(suite_id)
        elif exp_id:
            sim_map = workdirs_from_experiment_id(exp_id, comps_experiment)
        else:
            raise Exception('Unable to map COMPS simulations to output directories without Suite or Experiment ID.')

        if verbose:
            logger.info(f'Populated map of {len(sim_map)} simulation IDs to output directories')

        if save:
            cls.sim_dir_map = cls.sim_dir_map or {}
            cls.sim_dir_map.update(sim_map)

        return sim_map

    def load_all_files(self, filenames):
        if not self.asset_service:
            #  we can just open files locally...
            super(CompsOutputParser, self).load_all_files(filenames)
            return

        # Separate the path into asset collection and transient files
        assets = [path for path in filenames if path.lower().startswith("assets")]
        transient = [path for path in filenames if not path.lower().startswith("assets")]

        byte_arrays = {}

        if transient:
            try:
                byte_arrays.update(dict(zip(transient, self.COMPS_simulation.retrieve_output_files(paths=transient))))
            except Exception as e:
                user_logger.error(f"Could not retrieve requested file(s) for simulation {self.sim_id} - "
                                  f"Requested files: {transient}. Parser exiting...")
                user_logger.error(e)
                exit()

        if assets:
            try:
                # TODO verify strip of prefix is working
                data_map = get_asset_for_comps_item(self.platform, self.simulation, assets)
                data_map = {k.replace("Assets", ""): v for k, v in data_map}
                byte_arrays.update(data_map)
            except Exception:
                user_logger.error(f"Could not retrieve requested file(s) for simulation {self.sim_id} - "
                                  f"Requested files: {assets}. Parser exiting...")
                exit()

        for filename, byte_array in byte_arrays.items():
            self.load_single_file(filename, byte_array)

    def get_sim_dir(self):
        return self.sim_dir_map[self.sim_id]
