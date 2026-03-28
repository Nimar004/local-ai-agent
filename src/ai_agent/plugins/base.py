"""
Base Plugin Class for AI Agent Plugin System.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PluginType(Enum):
    """Types of plugins."""
    TOOL = "tool"           # Adds new tools/capabilities
    INTEGRATION = "integration"  # Integrates with external services
    UI = "ui"              # Adds UI components
    MODEL = "model"        # Adds model support
    AUTOMATION = "automation"  # Adds automation capabilities
    ANALYSIS = "analysis"  # Adds analysis capabilities


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class Plugin(ABC):
    """
    Base class for all plugins.
    
    All plugins must inherit from this class and implement the required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin."""
        self.logger = logging.getLogger(f"Plugin.{self.__class__.__name__}")
        self._config = config or {}
        self._enabled = False
        self._initialized = False
        
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
        
    @property
    def name(self) -> str:
        """Get plugin name."""
        return self.metadata.name
        
    @property
    def version(self) -> str:
        """Get plugin version."""
        return self.metadata.version
        
    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled
        
    async def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info(f"Initializing plugin: {self.name}")
            result = await self._initialize()
            if result:
                self._initialized = True
                self.logger.info(f"Plugin {self.name} initialized successfully")
            else:
                self.logger.error(f"Plugin {self.name} initialization failed")
            return result
        except Exception as e:
            self.logger.error(f"Plugin {self.name} initialization error: {e}")
            return False
            
    @abstractmethod
    async def _initialize(self) -> bool:
        """Plugin-specific initialization logic."""
        pass
        
    async def enable(self) -> bool:
        """
        Enable the plugin.
        
        Returns:
            True if enabled successfully, False otherwise
        """
        if not self._initialized:
            self.logger.error(f"Plugin {self.name} not initialized")
            return False
            
        try:
            self.logger.info(f"Enabling plugin: {self.name}")
            result = await self._enable()
            if result:
                self._enabled = True
                self.logger.info(f"Plugin {self.name} enabled successfully")
            else:
                self.logger.error(f"Plugin {self.name} enable failed")
            return result
        except Exception as e:
            self.logger.error(f"Plugin {self.name} enable error: {e}")
            return False
            
    @abstractmethod
    async def _enable(self) -> bool:
        """Plugin-specific enable logic."""
        pass
        
    async def disable(self) -> bool:
        """
        Disable the plugin.
        
        Returns:
            True if disabled successfully, False otherwise
        """
        try:
            self.logger.info(f"Disabling plugin: {self.name}")
            result = await self._disable()
            if result:
                self._enabled = False
                self.logger.info(f"Plugin {self.name} disabled successfully")
            else:
                self.logger.error(f"Plugin {self.name} disable failed")
            return result
        except Exception as e:
            self.logger.error(f"Plugin {self.name} disable error: {e}")
            return False
            
    @abstractmethod
    async def _disable(self) -> bool:
        """Plugin-specific disable logic."""
        pass
        
    async def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a plugin action.
        
        Args:
            action: The action to execute
            params: Parameters for the action
            
        Returns:
            Result dictionary
        """
        if not self._enabled:
            return {
                "success": False,
                "error": f"Plugin {self.name} is not enabled"
            }
            
        try:
            self.logger.info(f"Executing action {action} on plugin {self.name}")
            result = await self._execute(action, params or {})
            return result
        except Exception as e:
            self.logger.error(f"Plugin {self.name} execute error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    @abstractmethod
    async def _execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Plugin-specific execution logic."""
        pass
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
        
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
        
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self._enabled,
            "initialized": self._initialized,
            "type": self.metadata.plugin_type.value
        }