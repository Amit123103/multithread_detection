"""Plugin architecture allowing custom detectors and action extensions."""

from abc import ABC, abstractmethod
from typing import Dict, List, Type

import numpy as np

from threatvision.models.backend import Detection


class Plugin(ABC):
    """Base class for all ThreatVision custom plugins."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Custom detection logic on video frame."""
        pass


class PluginRegistry:
    """Global registry managing third-party ThreatVision plugins."""

    _plugins: Dict[str, Plugin] = {}

    @classmethod
    def register(cls, plugin: Plugin) -> None:
        cls._plugins[plugin.name] = plugin

    @classmethod
    def get_plugin(cls, name: str) -> Plugin | None:
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls) -> List[str]:
        return list(cls._plugins.keys())


def register_plugin(plugin_cls: Type[Plugin]):
    """Decorator to register a custom plugin class."""
    instance = plugin_cls(name=plugin_cls.__name__)
    PluginRegistry.register(instance)
    return plugin_cls
