from typing import Dict, Type, TYPE_CHECKING
from ..domain.enums import StageName

if TYPE_CHECKING:
    from .base_stage import BaseStage

class StageRegistry:
    """Registry for dynamically looking up and instantiating pipeline stages."""
    
    _registry: Dict[StageName, Type["BaseStage"]] = {}

    @classmethod
    def register(cls, name: StageName):
        """Decorator to register a stage class."""
        def decorator(subclass: Type["BaseStage"]):
            cls._registry[name] = subclass
            return subclass
        return decorator

    @classmethod
    def get_stage(cls, name: StageName) -> Type["BaseStage"]:
        """Retrieve a stage class by enum name."""
        if name not in cls._registry:
            raise ValueError(f"Stage '{name}' not found in registry. Ensure it is imported.")
        return cls._registry[name]

    @classmethod
    def list_stages(cls):
        return list(cls._registry.keys())
