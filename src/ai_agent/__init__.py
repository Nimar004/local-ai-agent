"""
Local AI Agent System
A powerful local AI agent that can use multiple models efficiently.
"""

__version__ = "1.0.0"
__author__ = "Local AI Agent"

from .core.agent import AIAgent
from .core.model_manager import ModelManager

__all__ = ["AIAgent", "ModelManager"]