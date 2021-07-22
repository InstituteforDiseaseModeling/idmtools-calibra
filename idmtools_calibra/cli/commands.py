import click
from typing import Optional, List
from idmtools_calibra.cli.utils import get_calib_manager


@click.group(short_help="Calibration Related Commands")
def calibra():
    pass


@calibra.command()
def run():
    print('calibra run...')


@calibra.command()
def cleanup():
    print('calibra cleanup...')


@calibra.command()
@click.option('--config_name', required=True, help="Calibration Script")
@click.option('--iteration', default=None, help="Iteration")
@click.option('--iter_step', default=None, help="Iteration Step")
@click.option('--max_iterations', default=None, help="Iteration Top Limit")
@click.option('--loop', default=True, help="Continue Iteration or not")
def resume(config_name: Optional[str], iteration: Optional[int], iter_step: Optional[str],
           max_iterations: Optional[int], loop: Optional[bool]):
    print('calibra resume...')
    print("config_name: ", config_name)
    print("iteration: ", iteration)
    print("iter_step: ", iter_step)
    print("max_iterations: ", max_iterations)
    print("loop: ", loop)

    # platform = Platform("BAYESIAN")  # SLURMStage      CALCULON

    calib_manager = get_calib_manager(config_name)
    print(calib_manager)
    calib_manager.resume_calibration(iteration=iteration, iter_step=iter_step, max_iterations=max_iterations, loop=loop)

    # from idmtools_calibra.utilities.resume_manager import ResumeManager
    # resume_manager = ResumeManager(calib_manager, iteration=iteration, iter_step=iter_step,
    #                                max_iterations=max_iterations, loop=loop)
    # resume_manager.resume()
