"""
Task Executor for handling AI task execution.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import AgentConfig
    from .model_manager import ModelManager


class TaskType(Enum):
    """Types of tasks the executor can handle."""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    FILE_ANALYSIS = "file_analysis"
    SCREEN_CONTROL = "screen_control"
    WEB_ACCESS = "web_access"
    VIDEO_EDITING = "video_editing"
    GENERAL = "general"


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    response: str
    task_type: TaskType
    model_used: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TaskExecutor:
    """
    Executes tasks using the most appropriate model.
    
    Features:
    - Automatic task type detection
    - Model selection based on task requirements
    - Context management for multi-step tasks
    - Error handling and retry logic
    """
    
    def __init__(self, config: AgentConfig, model_manager: ModelManager):
        """Initialize the Task Executor."""
        self.config = config
        self.model_manager = model_manager
        self.logger = logging.getLogger("TaskExecutor")
        self._task_history: List[Dict[str, Any]] = []
        
    async def initialize(self) -> None:
        """Initialize the task executor."""
        self.logger.info("Initializing Task Executor...")
        self.logger.info("Task Executor initialized")
        
    def _detect_task_type(self, task: str) -> TaskType:
        """Detect the type of task from the description."""
        task_lower = task.lower()
        
        # Code generation patterns
        if any(word in task_lower for word in [
            "generate code", "write code", "create function",
            "implement", "program", "script"
        ]):
            return TaskType.CODE_GENERATION
            
        # Code analysis patterns
        if any(word in task_lower for word in [
            "analyze code", "review code", "explain code",
            "debug", "find bug", "code analysis"
        ]):
            return TaskType.CODE_ANALYSIS
            
        # File analysis patterns
        if any(word in task_lower for word in [
            "analyze file", "read file", "file content",
            "summarize file", "file analysis"
        ]):
            return TaskType.FILE_ANALYSIS
            
        # Screen control patterns
        if any(word in task_lower for word in [
            "click", "type", "press", "screen",
            "window", "screenshot", "control"
        ]):
            return TaskType.SCREEN_CONTROL
            
        # Web access patterns
        if any(word in task_lower for word in [
            "website", "url", "browse", "fetch",
            "download", "web", "http"
        ]):
            return TaskType.WEB_ACCESS
            
        # Video editing patterns
        if any(word in task_lower for word in [
            "video", "edit video", "trim", "merge",
            "convert video", "video processing"
        ]):
            return TaskType.VIDEO_EDITING
            
        return TaskType.GENERAL
        
    def _get_system_prompt(self, task_type: TaskType) -> str:
        """Get the appropriate system prompt for the task type."""
        prompts = {
            TaskType.CODE_GENERATION: (
                "You are an expert programmer. Generate clean, efficient, "
                "and well-documented code. Follow best practices and "
                "include error handling where appropriate."
            ),
            TaskType.CODE_ANALYSIS: (
                "You are a code reviewer. Analyze the code for bugs, "
                "performance issues, and best practices. Provide "
                "constructive feedback and suggestions for improvement."
            ),
            TaskType.FILE_ANALYSIS: (
                "You are a file analyst. Analyze the file content "
                "thoroughly and provide insights, summaries, and "
                "recommendations based on the content."
            ),
            TaskType.SCREEN_CONTROL: (
                "You are a screen automation assistant. Generate "
                "precise commands for screen control actions. "
                "Always confirm before executing destructive actions."
            ),
            TaskType.WEB_ACCESS: (
                "You are a web assistant. Help with web browsing, "
                "data extraction, and online research. Provide "
                "accurate and relevant information."
            ),
            TaskType.VIDEO_EDITING: (
                "You are a video editing assistant. Help with video "
                "processing tasks including trimming, merging, "
                "format conversion, and effects application."
            ),
            TaskType.GENERAL: (
                "You are a helpful AI assistant. Provide accurate, "
                "helpful, and concise responses to user queries."
            )
        }
        return prompts.get(task_type, prompts[TaskType.GENERAL])
        
    def _get_required_capabilities(self, task_type: TaskType) -> List[str]:
        """Get required model capabilities for the task type."""
        capabilities = {
            TaskType.CODE_GENERATION: ["text", "code"],
            TaskType.CODE_ANALYSIS: ["text", "code"],
            TaskType.FILE_ANALYSIS: ["text"],
            TaskType.SCREEN_CONTROL: ["text"],
            TaskType.WEB_ACCESS: ["text"],
            TaskType.VIDEO_EDITING: ["text"],
            TaskType.GENERAL: ["text"]
        }
        return capabilities.get(task_type, ["text"])
        
    async def execute(
        self,
        task: str,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using the most appropriate model.
        
        Args:
            task: The task description
            model: Specific model to use (optional)
            context: Additional context for the task
            
        Returns:
            Task execution result
        """
        # Detect task type
        task_type = self._detect_task_type(task)
        self.logger.info(f"Detected task type: {task_type.value}")
        
        # Get system prompt
        system_prompt = self._get_system_prompt(task_type)
        
        # Select model
        if model:
            selected_model = model
        else:
            required_capabilities = self._get_required_capabilities(task_type)
            selected_model = await self.model_manager.select_model_for_task(
                task,
                required_capabilities
            )
            
        if not selected_model:
            return {
                "success": False,
                "error": "No suitable model available",
                "task_type": task_type.value
            }
            
        self.logger.info(f"Using model: {selected_model}")
        
        # Prepare prompt with context
        full_prompt = task
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask:\n{task}"
            
        # Execute the task
        try:
            result = await self.model_manager.generate(
                selected_model,
                full_prompt,
                system=system_prompt
            )
            
            if result.get("success"):
                # Record in history
                self._task_history.append({
                    "task": task,
                    "task_type": task_type.value,
                    "model": selected_model,
                    "success": True
                })
                
                return {
                    "success": True,
                    "response": result["response"],
                    "task_type": task_type.value,
                    "model_used": selected_model,
                    "backend": result.get("backend", "unknown")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "task_type": task_type.value,
                    "model_used": selected_model
                }
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type.value,
                "model_used": selected_model
            }
            
    async def execute_multi_step(
        self,
        steps: List[str],
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in sequence.
        
        Args:
            steps: List of task descriptions
            model: Specific model to use
            
        Returns:
            List of task results
        """
        results = []
        context = {}
        
        for i, step in enumerate(steps):
            self.logger.info(f"Executing step {i+1}/{len(steps)}")
            
            result = await self.execute(step, model, context)
            results.append(result)
            
            # Update context with previous result
            if result.get("success"):
                context[f"step_{i+1}_result"] = result["response"][:500]
                
        return results
        
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get the task execution history."""
        return self._task_history.copy()
        
    async def shutdown(self) -> None:
        """Shutdown the task executor."""
        self.logger.info("Task Executor shutdown complete")