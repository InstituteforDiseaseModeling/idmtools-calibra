import json
import os
from emodpy.emod_task import EMODTask
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
import manifest 
from emodpy.emod_task import EMODTask
from settings import Settings
import model

settings = Settings()

def get_task():
    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    from idmtools.core.platform_factory import Platform
    platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=settings.MODEL_DRIVER,
        campaign_builder=model.build_camp,
        demog_builder=None,
        schema_path=manifest.schema_file,
        param_custom_cb=model.set_param_fn,
        ep4_path=manifest.ep4
    )
    task.set_sif( settings.SIF )
    return task, platform

def test_and_plot():
    # run model with selected params and plot!
    # TBD: parameterize directory.
    with open( os.path.join( settings.CALIBRATION_NAME, "CalibManager.json" ) ) as results_fp: 
        finals = json.load( results_fp )["final_samples"]
        a = finals["a"][0]
        b = finals["b"][0]
        c = finals["c"][0]
        for param in settings.CALIBRATION_PARAMETERS:
            internal_name = param["Name"]
            model_name = param["MapTo"]
            value = finals[internal_name][0]
            format_value = "{:.3f}".format( value )
            print( f"{model_name} = {format_value}" )

    builder = SimulationBuilder()
    def update_sim_random_seed(simulation, value):
        simulation.task.config.parameters.Run_Number = value
        simulation.task.config.parameters.Base_Infectivity_Constant = a
        simulation.task.config.parameters.Infectious_Period_Exponential = b
        simulation.task.config.parameters.Incubation_Period_Constant = c
        return {"Run_Number": value}
    builder.add_sweep_definition( update_sim_random_seed, range(10) )

    task, platform = get_task()
    # create experiment from builder
    experiment  = Experiment.from_builder(builder, task, name="calibrated emod_sir sweep") 
    experiment.run(wait_until_done=True, platform=platform)
    task.handle_experiment_completion( experiment )
    task.get_file_from_comps( experiment.uid, "InsetChart.json" )
    EMODTask.cache_experiment_metadata_in_sql( experiment.uid )
    import emod_api.channelreports.plot_icj_means as plotter
    data = plotter.collect( str( experiment.uid ) )
    plotter.display( data )

if __name__ == "__main__":
    test_and_plot()
