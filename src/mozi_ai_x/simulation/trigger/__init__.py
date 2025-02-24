from .base import CTrigger
from .points import CTriggerPoints
from .random_time import CTriggerRandomTime
from .regular_time import CTriggerRegularTime
from .scenario_loaded import CTriggerScenLoaded
from .time import CTriggerTime
from .unit_damaged import CTriggerUnitDamaged
from .unit_detected import CTriggerUnitDetected
from .unit_destroyed import CTriggerUnitDestroyed
from .unit_remains_in_area import CTriggerUnitRemainsInArea

__all__ = [
    "CTrigger",
    "CTriggerPoints",
    "CTriggerRandomTime",
    "CTriggerRegularTime",
    "CTriggerScenLoaded",
    "CTriggerTime",
    "CTriggerUnitDamaged",
    "CTriggerUnitDetected",
    "CTriggerUnitDestroyed",
    "CTriggerUnitRemainsInArea",
]
