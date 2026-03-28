"""
Plugin Manager for AI Agent Plugin System.
"""

import asyncio
import logging
import importlib
import inspect
import os
import sys
from typing import Dict, List, Optional, Any, Type
from pathlib import Path

from .base import Plugin, PluginType, PluginMetadata


class PluginManager:
    """
    Manages plugins for the AI Agent.
    
    Features:
    - Plugin discovery and loading
    - Plugin lifecycle management
    - Plugin configuration
    - Plugin execution
    """
    
    def __init__(self, plugins_dir: str = "~/ai-agent/plugins"):
        """Initialize the Plugin Manager."""
        self.logger = logging.getLogger("PluginManager")
        self._plugins_dir = Path(os.path.expanduser(plugins_dir))
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Plugin registry
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}
        
        # Add plugins directory to path
        if str(self._plugins_dir) not in sys.path:
            sys.path.insert(0, str(self._plugins_dir))
            
    async def discover_plugins(self) -> List[str]:
        """
        Discover available plugins.
        
        Returns:
            List of discovered plugin names
        """
        discovered = []
        
        # Look for Python files in plugins directory
        for file_path in self._plugins_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            plugin_name = file_path.stem
            discovered.append(plugin_name)
            
        self.logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
        
    async def load_plugin(
        self,
        plugin_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Load a plugin.
        
        Args:
            plugin_name: Name of the plugin to load
            config: Plugin configuration
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Import the plugin module
            module = importlib.import_module(plugin_name)
            
            # Find plugin class in module
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj is not Plugin):
                    plugin_class = obj
                    break
                    
            if not plugin_class:
                self.logger.error(f"No plugin class found in {plugin_name}")
                return False
                
            # Create plugin instance
            plugin = plugin_class(config)
            
            # Initialize plugin
            if not await plugin.initialize():
                self.logger.error(f"Failed to initialize plugin {plugin_name}")
                return False
                
            # Store plugin
            self._plugins[plugin_name] = plugin
            self._plugin_classes[plugin_name] = plugin_class
            
            self.logger.info(f"Loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
            
    async def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            self.logger.warning(f"Plugin {plugin_name} not loaded")
            return False
            
        try:
            plugin = self._plugins[plugin_name]
            
            # Disable plugin if enabled
            if plugin.enabled:
                await plugin.disable()
                
            # Remove from registry
            del self._plugins[plugin_name]
            del self._plugin_classes[plugin_name]
            
            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
            
    async def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
            
        Returns:
            True if enabled successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            self.logger.error(f"Plugin {plugin_name} not loaded")
            return False
            
        plugin = self._plugins[plugin_name]
        return await plugin.enable()
        
    async def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            plugin_name: Name of the plugin to disable
            
        Returns:
            True if disabled successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            self.logger.error(f"Plugin {plugin_name} not loaded")
            return False
            
        plugin = self._plugins[plugin_name]
        return await plugin.disable()
        
    async def execute_plugin_action(
        self,
        plugin_name: str,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an action on a plugin.
        
        Args:
            plugin_name: Name of the plugin
            action: Action to execute
            params: Parameters for the action
            
        Returns:
            Result dictionary
        """
        if plugin_name not in self._plugins:
            return {
                "success": False,
                "error": f"Plugin {plugin_name} not loaded"
            }
            
        plugin = self._plugins[plugin_name]
        return await plugin.execute(action, params)
        
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(plugin_name)
        
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins."""
        return [plugin.get_status() for plugin in self._plugins.values()]
        
    def list_enabled_plugins(self) -> List[Dict[str, Any]]:
        """List all enabled plugins."""
        return [
            plugin.get_status() 
            for plugin in self._plugins.values() 
            if plugin.enabled
        ]
        
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """Get all plugins of a specific type."""
        return [
            plugin for plugin in self._plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]
        
    async def load_all_plugins(self) -> int:
        """
        Load all discovered plugins.
        
        Returns:
            Number of plugins loaded successfully
        """
        discovered = await self.discover_plugins()
        loaded = 0
        
        for plugin_name in discovered:
            if await self.load_plugin(plugin_name):
                loaded += 1
                
        self.logger.info(f"Loaded {loaded}/{len(discovered)} plugins")
        return loaded
        
    async def enable_all_plugins(self) -> int:
        """
        Enable all loaded plugins.
        
        Returns:
            Number of plugins enabled successfully
        """
        enabled = 0
        
        for plugin_name in self._plugins:
            if await self.enable_plugin(plugin_name):
                enabled += 1
                
        self.logger.info(f"Enabled {enabled}/{len(self._plugins)} plugins")
        return enabled
        
    async def shutdown(self) -> None:
        """Shutdown all plugins."""
        for plugin_name in list(self._plugins.keys()):
            await self.unload_plugin(plugin_name)
            
        self.logger.info("All plugins shutdown")