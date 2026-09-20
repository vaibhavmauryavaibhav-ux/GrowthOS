"""
Plugin Manager for Cognitive Growth OS
Discovers, loads, and manages lifecycle hook execution for extensions.
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

from plugins.base_plugin import GrowthOSPlugin

PLUGIN_DIRS = [
    Path(__file__).parent.parent / "plugins",
    Path.home() / ".config" / "growth_os" / "plugins"
]

class PluginManager:
    def __init__(self):
        self.plugins: List[GrowthOSPlugin] = []
        self._discover_and_load_plugins()

    def _discover_and_load_plugins(self):
        """Discovers all .py files in plugin directories and loads subclasses of GrowthOSPlugin."""
        self.plugins.clear()

        for directory in PLUGIN_DIRS:
            if not directory.exists():
                continue
            
            for file_path in directory.glob("*.py"):
                if file_path.name in ["base_plugin.py", "__init__.py"]:
                    continue

                module_name = f"growth_os_plugin_{file_path.stem}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Find GrowthOSPlugin subclasses
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, GrowthOSPlugin) and 
                                attr is not GrowthOSPlugin):
                                instance = attr()
                                instance.on_load()
                                self.plugins.append(instance)
                                print(f"[PluginManager] Loaded extension: '{instance.name}' v{instance.version}")
                except Exception as e:
                    print(f"[PluginManager] Error loading plugin from {file_path.name}: {e}")

    def dispatch(self, hook_name: str, *args, **kwargs):
        """Safely dispatches an event to all loaded plugins."""
        for plugin in self.plugins:
            try:
                hook = getattr(plugin, hook_name, None)
                if callable(hook):
                    hook(*args, **kwargs)
            except Exception as e:
                print(f"[PluginManager] Error in plugin '{plugin.name}' on '{hook_name}': {e}")

# Global singleton
plugin_manager = PluginManager()
