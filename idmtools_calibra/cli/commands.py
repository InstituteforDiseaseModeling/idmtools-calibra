import click
from typing import Optional


@click.group(short_help="Calibration Related Commands")
def calibra():
    pass


@calibra.command()
def run():
    print('To be implemented...')
    exit()


@calibra.command()
def cleanup():
    print('To be implemented...')
    exit()


@calibra.command()
@click.option('--config_name', required=True, help="Calibration Script")
@click.option('--iteration', default=None, help="Iteration")
@click.option('--iter_step', default=None, help="Iteration Step")
@click.option('--max_iterations', default=None, help="Iteration Top Limit")
@click.option('--loop', default=True, help="Continue Iteration or not")
def resume(config_name: Optional[str], iteration: Optional[int], iter_step: Optional[str],
           max_iterations: Optional[int], loop: Optional[bool]):
    print('To be implemented...')
    exit()
