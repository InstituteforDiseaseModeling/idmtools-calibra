import json
from emodpy.emod_task import EMODTask
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
import manifest 
from emodpy.emod_task import EMODTask
from settings import Settings

settings = Settings()

# NOTE: Any campaign parameter you want to calibrate must be in the build_camp param list
def get_task( build_camp_fn=None, build_demog_fn=None ):
    def set_param_fn( config ):
        #config.parameters.Simulation_Duration = 730.0
        config.parameters.Enable_Demographics_Reporting = 0 
        config.parameters.Enable_Property_Report = 1 
        #config.parameters.Base_Individual_Sample_Rate = 0.1

        return config

    import emod_generic.bootstrap as dtk
    dtk.setup( manifest.model_dl_dir )
    from idmtools.core.platform_factory import Platform
    print( "Creating COMPS Platform with node_group='idm_48cores', priority='AboveNormal'" )
    platform = Platform(settings.LOCALE, node_group="idm_48cores", priority="AboveNormal")
    import model
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=settings.MODEL_DRIVER,
        campaign_builder=build_camp_fn,
        demog_builder=build_demog_fn,
        schema_path=manifest.schema_file,
        param_custom_cb=model.set_param_fn,
        ep4_path=manifest.ep4
    )

    task.config.parameters.Enable_Property_Output = 1 
    task.set_sif( settings.SIF )
    return task, platform


def test_and_plot():
    # run model with selected params and plot!
    import os
    calibration_output_path = os.path.join( settings.CALIBRATION_NAME, "CalibManager.json" )
    if os.path.exists( calibration_output_path ):
        with open( calibration_output_path ) as results_fp: 
            myjson = json.load( results_fp )
            if "final_samples" in myjson:
                finals = myjson["final_samples"]
                a = finals["a"][0]
                b = finals["b"][0]
                c = finals["c"][0]
                d = finals["d"][0]
                #e = finals["e"][0]
                #f = finals["f"][0]
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
        #simulation.task.config.parameters.Acute_Stage_Infectivity_Multiplier = a
        #simulation.task.config.parameters.Base_Infectivity = b
        #simulation.task.config.parameters.Acute_Duration_In_Months = c
        return {"Run_Number": value}
    builder.add_sweep_definition( update_sim_random_seed, range(10) )

    from functools import partial
    import model
    build_camp_actual = partial( model.build_camp )
    build_demog_actual = partial( model.build_demog, hint_group_a_bi=a, hint_group_b_bi=b, hint_group_c_bi=c, hint_group_d_bi=d )
    task, platform = get_task( build_camp_fn=build_camp_actual, build_demog_fn=build_demog_actual )
    #task, platform = get_task()

    # create experiment from builder
    experiment  = Experiment.from_builder(builder, task, name="calibrating emod-hint") 
    experiment.run(wait_until_done=True, platform=platform)
    task.handle_experiment_completion( experiment )
    task.get_file_from_comps( experiment.uid, "InsetChart.json" )
    EMODTask.cache_experiment_metadata_in_sql( experiment.uid )
    import emod_api.channelreports.plot_icj_means as plotter
    data = plotter.collect( str( experiment.uid ), chan="Infected" )
    plotter.display( data )


if __name__ == "__main__":
    test_and_plot()
