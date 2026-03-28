"""
Main AI Agent class that orchestrates all operations.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .model_manager import ModelManager
from .task_executor import TaskExecutor


class AgentMode(Enum):
    """Agent operation modes."""
    CLI = "cli"
    WEB = "web"
    AUTONOMOUS = "autonomous"


@dataclass
class AgentConfig:
    """Configuration for the AI Agent."""
    mode: AgentMode = AgentMode.CLI
    default_model: str = "llama3.2"
    max_concurrent_tasks: int = 3
    enable_screen_control: bool = True
    enable_web_access: bool = True
    enable_file_access: bool = True
    cache_enabled: bool = True
    log_level: str = "INFO"


class AIAgent:
    """
    Main AI Agent class that provides a unified interface for all AI operations.
    
    This agent can:
    - Use multiple local AI models efficiently
    - Perform code generation and analysis
    - Control screen and windows
    - Access and interact with websites
    - Communicate with other AI applications
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the AI Agent."""
        self.config = config or AgentConfig()
        self.logger = self._setup_logging()
        self.model_manager = ModelManager(self.config)
        self.task_executor = TaskExecutor(self.config, self.model_manager)
        self._active_tasks: Dict[str, Any] = {}
        self._initialized = False
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger("AIAgent")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    async def initialize(self) -> None:
        """Initialize the agent and its components."""
        if self._initialized:
            return
            
        self.logger.info("Initializing AI Agent...")
        
        try:
            await self.model_manager.initialize()
            await self.task_executor.initialize()
            self._initialized = True
            self.logger.info("AI Agent initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Agent: {e}")
            raise
            
    async def execute_task(
        self,
        task: str,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using the most appropriate model.
        
        Args:
            task: The task description or instruction
            model: Specific model to use (optional)
            context: Additional context for the task
            
        Returns:
            Dictionary containing the task result and metadata
        """
        if not self._initialized:
            await self.initialize()
            
        self.logger.info(f"Executing task: {task[:100]}...")
        
        try:
            result = await self.task_executor.execute(task, model, context)
            self.logger.info("Task completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task": task
            }
            
    async def generate_code(
        self,
        description: str,
        language: str = "python",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate code based on a description."""
        task = f"Generate {language} code for: {description}"
        return await self.execute_task(task, model)
        
    async def analyze_file(
        self,
        file_path: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze a file and provide insights."""
        task = f"Analyze the file at {file_path} with focus on {analysis_type}"
        return await self.execute_task(task)
        
    async def control_screen(
        self,
        action: str,
        target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Control screen elements."""
        if not self.config.enable_screen_control:
            return {"success": False, "error": "Screen control is disabled"}
            
        task = f"Perform screen action: {action}"
        if target:
            task += f" on {target}"
        return await self.execute_task(task)
        
    async def access_web(
        self,
        url: str,
        action: str = "fetch"
    ) -> Dict[str, Any]:
        """Access and interact with websites."""
        if not self.config.enable_web_access:
            return {"success": False, "error": "Web access is disabled"}
            
        task = f"Access website {url} and {action}"
        return await self.execute_task(task)
        
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models."""
        return await self.model_manager.list_models()
        
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        return await self.model_manager.get_model_info(model_name)
        
    async def shutdown(self) -> None:
        """Shutdown the agent and cleanup resources."""
        self.logger.info("Shutting down AI Agent...")
        await self.task_executor.shutdown()
        await self.model_manager.shutdown()
        self._initialized = False
        self.logger.info("AI Agent shutdown complete")
        
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"AIAgent(mode={self.config.mode}, model={self.config.default_model})"