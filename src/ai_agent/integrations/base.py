"""
Base Integration Class for AI Agent Integrations.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class IntegrationConfig:
    """Configuration for an integration."""
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3


class BaseIntegration(ABC):
    """
    Base class for all integrations.
    
    All integrations must inherit from this class and implement the required methods.
    """
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        """Initialize the integration."""
        self.logger = logging.getLogger(f"Integration.{self.__class__.__name__}")
        self._config = config or IntegrationConfig(name=self.__class__.__name__)
        self._enabled = False
        self._initialized = False
        
    @property
    def name(self) -> str:
        """Get integration name."""
        return self._config.name
        
    @property
    def enabled(self) -> bool:
        """Check if integration is enabled."""
        return self._enabled
        
    async def initialize(self) -> bool:
        """
        Initialize the integration.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info(f"Initializing integration: {self.name}")
            result = await self._initialize()
            if result:
                self._initialized = True
                self.logger.info(f"Integration {self.name} initialized successfully")
            else:
                self.logger.error(f"Integration {self.name} initialization failed")
            return result
        except Exception as e:
            self.logger.error(f"Integration {self.name} initialization error: {e}")
            return False
            
    @abstractmethod
    async def _initialize(self) -> bool:
        """Integration-specific initialization logic."""
        pass
        
    async def enable(self) -> bool:
        """
        Enable the integration.
        
        Returns:
            True if enabled successfully, False otherwise
        """
        if not self._initialized:
            self.logger.error(f"Integration {self.name} not initialized")
            return False
            
        try:
            self.logger.info(f"Enabling integration: {self.name}")
            result = await self._enable()
            if result:
                self._enabled = True
                self.logger.info(f"Integration {self.name} enabled successfully")
            else:
                self.logger.error(f"Integration {self.name} enable failed")
            return result
        except Exception as e:
            self.logger.error(f"Integration {self.name} enable error: {e}")
            return False
            
    @abstractmethod
    async def _enable(self) -> bool:
        """Integration-specific enable logic."""
        pass
        
    async def disable(self) -> bool:
        """
        Disable the integration.
        
        Returns:
            True if disabled successfully, False otherwise
        """
        try:
            self.logger.info(f"Disabling integration: {self.name}")
            result = await self._disable()
            if result:
                self._enabled = False
                self.logger.info(f"Integration {self.name} disabled successfully")
            else:
                self.logger.error(f"Integration {self.name} disable failed")
            return result
        except Exception as e:
            self.logger.error(f"Integration {self.name} disable error: {e}")
            return False
            
    @abstractmethod
    async def _disable(self) -> bool:
        """Integration-specific disable logic."""
        pass
        
    async def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an integration action.
        
        Args:
            action: The action to execute
            params: Parameters for the action
            
        Returns:
            Result dictionary
        """
        if not self._enabled:
            return {
                "success": False,
                "error": f"Integration {self.name} is not enabled"
            }
            
        try:
            self.logger.info(f"Executing action {action} on integration {self.name}")
            result = await self._execute(action, params or {})
            return result
        except Exception as e:
            self.logger.error(f"Integration {self.name} execute error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    @abstractmethod
    async def _execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Integration-specific execution logic."""
        pass
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(self._config, key, default)
        
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        setattr(self._config, key, value)
        
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "name": self.name,
            "enabled": self._enabled,
            "initialized": self._initialized
        }