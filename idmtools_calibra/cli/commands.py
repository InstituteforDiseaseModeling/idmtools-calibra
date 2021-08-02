import click
from typing import Optional


@click.group(help="[TODO]: Calibration Related Commands")
def calibra():
    pass


@calibra.command(help="[TODO]: Calibration Run")
def run():
    print('To be implemented...')
    exit()


@calibra.command(help="[TODO]: Calibration Cleanup")
def cleanup():
    print('To be implemented...')
    exit()


@calibra.command(help="[TODO]: Calibration Resume")
@click.option('--config_name', required=True, help="Calibration Script")
@click.option('--iteration', default=None, help="Iteration")
@click.option('--iter_step', default=None, help="Iteration Step")
@click.option('--max_iterations', default=None, help="Iteration Top Limit")
@click.option('--loop', default=True, help="Continue Iteration or not")
def resume(config_name: Optional[str], iteration: Optional[int], iter_step: Optional[str],
           max_iterations: Optional[int], loop: Optional[bool]):
    print('To be implemented...')
    exit()
