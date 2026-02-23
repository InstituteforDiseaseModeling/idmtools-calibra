import json
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
import manifest 
from emodpy.emod_task import EMODTask
from settings import Settings
import matplotlib
import emod_api.campaign as camp
#matplotlib.use( "TkAgg" )

settings = Settings()

# NOTE: Any campaign parameter you want to calibrate must be in the build_camp param list
def get_task( build_camp_fn=None ):
    def set_param_fn( config ):
        config.parameters.Simulation_Duration = 365.0
        #config.parameters.Simulation_Duration = 730.0
        config.parameters.Base_Infectivity_Constant = 3.5 
        config.parameters.Enable_Demographics_Reporting = 0 
        config.parameters.Incubation_Period_Constant = 0
        config.parameters.Infectious_Period_Exponential = 4.0 
        config.parameters.Base_Individual_Sample_Rate = 0.1
        #config.parameters.Minimum_End_Time = 90

        return config

    def build_camp(camp):
        from emodpy.campaign.individual_intervention import OutbreakIndividual as OutbreakIndividual
        from emodpy.campaign.common import TargetDemographicsConfig
        from emodpy.campaign.distributor import add_intervention_scheduled
        outbreak_event = OutbreakIndividual(campaign=camp, antigen=None)
        target_demographics_config = TargetDemographicsConfig(demographic_coverage=0.4)
        add_intervention_scheduled(camp,
                                   intervention_list=[outbreak_event],
                                   start_day=1,
                                   target_demographics_config=target_demographics_config)

        return camp

    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    from idmtools.core.platform_factory import Platform
    platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    task = EMODTask.from_defaults(eradication_path=settings.MODEL_DRIVER,
                                  campaign_builder=build_camp,
                                  schema_path=manifest.schema_file,
                                  config_builder=set_param_fn,
                                  embedded_python_scripts_path=manifest.ep4,
                                  demographics_builder=None)
    task.set_sif( settings.SIF, platform )
    return task, platform

def test_and_plot():
    # run model with selected params and plot!
    # TBD: parameterize directory.
    with open( "emod-sir/CalibManager.json" ) as results_fp: 
        finals = json.load( results_fp )["final_samples"]
        a = finals["a"][0]
        b = finals["b"][0]
        c = finals["c"][0]
        # print param names and values
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

    # create experiment from builder
    task,platform=get_task()
    experiment  = Experiment.from_builder(builder, task, name="calibrated emod_sir sweep") 
    experiment.run(wait_until_done=True, platform=platform)
    # task.handle_experiment_completion( experiment )
    # task.get_file_from_comps( experiment.uid, "InsetChart.json" )
    # EMODTask.cache_experiment_metadata_in_sql( experiment.uid )
    # import emod_api.channelreports.plot_icj_means as plotter
    # data = plotter.collect( str( experiment.uid ) )
    # plotter.display( data )

if __name__ == "__main__":
    test_and_plot()
