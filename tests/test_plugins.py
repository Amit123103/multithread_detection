"""Unit tests for plugin architecture."""

import numpy as np

from threatvision.models.backend import Detection
from threatvision.plugins.plugin import Plugin, PluginRegistry, register_plugin


class SamplePlugin(Plugin):
    def detect(self, frame: np.ndarray):
        return [Detection(label="custom", confidence=0.99, box=(0, 0, 10, 10))]


def test_plugin_registration():
    plugin = SamplePlugin(name="test_plugin")
    PluginRegistry.register(plugin)

    retrieved = PluginRegistry.get_plugin("test_plugin")
    assert retrieved is not None
    assert retrieved.name == "test_plugin"


def test_plugin_decorator():
    @register_plugin
    class DecoratorPlugin(Plugin):
        def detect(self, frame: np.ndarray):
            return []

    assert "DecoratorPlugin" in PluginRegistry.list_plugins()
