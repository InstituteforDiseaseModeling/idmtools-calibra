from dataclasses import field, dataclass
from functools import partial
from typing import Optional, Any, Dict

from idmtools.entities import CommandLine
from idmtools.entities.simulation import Simulation
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

# TODO - Move into idmtools?
@dataclass
class SingularityJSONConfiguredPythonTask(JSONConfiguredPythonTask):
    provided_command: Optional[CommandLine] = field(default_factory=lambda: CommandLine(), metadata={"md": True})

    def pre_creation(self, parent, platform):
        super().pre_creation(parent=parent, platform=platform)
        self.command = self.provided_command

    # TODO: once calibra is updated, remove this method and use calib_manager.set_parameter_sweep_callback
    @staticmethod
    def set_parameter_sweep_callback(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        """
        Convenience callback for sweeps

        Args:
            simulation: Simulation we are updating
            param: Parameter
            value: Value

        Returns:
            Tags to set on simulation
        """
        if not hasattr(simulation.task, 'set_parameter'):
            raise ValueError("update_task_with_set_parameter can only be used on tasks with a set_parameter")
        return simulation.task.set_parameter(param, value)

    @classmethod
    def set_param_partial(cls, parameter: str):
        return partial(cls.set_parameter_sweep_callback, param=parameter)

