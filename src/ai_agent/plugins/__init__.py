"""
Plugin System for AI Agent
Allows extending agent capabilities with custom plugins.
"""

from .manager import PluginManager
from .base import Plugin, PluginType

__all__ = ["PluginManager", "Plugin", "PluginType"]