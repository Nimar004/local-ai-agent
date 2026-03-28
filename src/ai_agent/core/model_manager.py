"""
Model Manager for handling multiple AI models efficiently.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import AgentConfig


class ModelBackend(Enum):
    """Supported model backends."""
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    LOCALAI = "localai"


@dataclass
class ModelInfo:
    """Information about a model."""
    name: str
    backend: ModelBackend
    size: str
    loaded: bool = False
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class ModelManager:
    """
    Manages multiple AI models and handles efficient loading/unloading.
    
    Features:
    - Support for multiple backends (Ollama, LM Studio, etc.)
    - Efficient model loading (only loads needed parts)
    - Automatic model selection based on task
    - Resource management for Mac Mini M4
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the Model Manager."""
        self.config = config
        self.logger = logging.getLogger("ModelManager")
        self._models: Dict[str, ModelInfo] = {}
        self._active_model: Optional[str] = None
        self._backend_urls: Dict[ModelBackend, str] = {
            ModelBackend.OLLAMA: "http://localhost:11434",
            ModelBackend.LMSTUDIO: "http://localhost:1234",
            ModelBackend.LOCALAI: "http://localhost:8080"
        }
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self) -> None:
        """Initialize the model manager and discover available models."""
        self.logger.info("Initializing Model Manager...")
        
        # Create HTTP session
        self._session = aiohttp.ClientSession()
        
        # Discover available models from all backends
        await self._discover_models()
        
        self.logger.info(f"Discovered {len(self._models)} models")
        
    async def _discover_models(self) -> None:
        """Discover available models from all backends."""
        for backend, url in self._backend_urls.items():
            try:
                await self._discover_backend_models(backend, url)
            except Exception as e:
                self.logger.warning(f"Could not connect to {backend.value}: {e}")
                
    async def _discover_backend_models(
        self,
        backend: ModelBackend,
        url: str
    ) -> None:
        """Discover models from a specific backend."""
        if backend == ModelBackend.OLLAMA:
            await self._discover_ollama_models(url)
        elif backend == ModelBackend.LMSTUDIO:
            await self._discover_lmstudio_models(url)
        elif backend == ModelBackend.LOCALAI:
            await self._discover_localai_models(url)
            
    async def _discover_ollama_models(self, url: str) -> None:
        """Discover models from Ollama."""
        try:
            async with self._session.get(f"{url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    for model in data.get("models", []):
                        model_info = ModelInfo(
                            name=model["name"],
                            backend=ModelBackend.OLLAMA,
                            size=model.get("size", "unknown"),
                            capabilities=self._infer_capabilities(model["name"])
                        )
                        self._models[model["name"]] = model_info
                        self.logger.info(f"Found Ollama model: {model['name']}")
        except Exception as e:
            self.logger.warning(f"Failed to discover Ollama models: {e}")
            
    async def _discover_lmstudio_models(self, url: str) -> None:
        """Discover models from LM Studio."""
        try:
            async with self._session.get(f"{url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    for model in data.get("data", []):
                        model_info = ModelInfo(
                            name=model["id"],
                            backend=ModelBackend.LMSTUDIO,
                            size="unknown",
                            capabilities=self._infer_capabilities(model["id"])
                        )
                        self._models[model["id"]] = model_info
                        self.logger.info(f"Found LM Studio model: {model['id']}")
        except Exception as e:
            self.logger.warning(f"Failed to discover LM Studio models: {e}")
            
    async def _discover_localai_models(self, url: str) -> None:
        """Discover models from LocalAI."""
        try:
            async with self._session.get(f"{url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    for model in data.get("data", []):
                        model_info = ModelInfo(
                            name=model["id"],
                            backend=ModelBackend.LOCALAI,
                            size="unknown",
                            capabilities=self._infer_capabilities(model["id"])
                        )
                        self._models[model["id"]] = model_info
                        self.logger.info(f"Found LocalAI model: {model['id']}")
        except Exception as e:
            self.logger.warning(f"Failed to discover LocalAI models: {e}")
            
    def _infer_capabilities(self, model_name: str) -> List[str]:
        """Infer model capabilities from its name."""
        capabilities = ["text"]
        name_lower = model_name.lower()
        
        if "code" in name_lower or "coder" in name_lower:
            capabilities.append("code")
        if "vision" in name_lower or "llava" in name_lower:
            capabilities.append("vision")
        if "instruct" in name_lower:
            capabilities.append("instruct")
            
        return capabilities
        
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models."""
        return [
            {
                "name": model.name,
                "backend": model.backend.value,
                "size": model.size,
                "loaded": model.loaded,
                "capabilities": model.capabilities
            }
            for model in self._models.values()
        ]
        
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        if model_name not in self._models:
            return {"error": f"Model {model_name} not found"}
            
        model = self._models[model_name]
        return {
            "name": model.name,
            "backend": model.backend.value,
            "size": model.size,
            "loaded": model.loaded,
            "capabilities": model.capabilities
        }
        
    async def select_model_for_task(
        self,
        task: str,
        required_capabilities: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Select the most appropriate model for a task.
        
        Args:
            task: The task description
            required_capabilities: Required model capabilities
            
        Returns:
            Model name or None if no suitable model found
        """
        if not self._models:
            return None
            
        # Default capabilities
        if required_capabilities is None:
            required_capabilities = ["text"]
            
        # Find models with required capabilities
        suitable_models = []
        for name, model in self._models.items():
            if all(cap in model.capabilities for cap in required_capabilities):
                suitable_models.append((name, model))
                
        if not suitable_models:
            # Fallback to any available model
            return list(self._models.keys())[0] if self._models else None
            
        # Prefer models based on task type
        task_lower = task.lower()
        
        # Check for code-related tasks
        if any(word in task_lower for word in ["code", "program", "function", "script"]):
            for name, model in suitable_models:
                if "code" in model.capabilities:
                    return name
                    
        # Check for vision-related tasks
        if any(word in task_lower for word in ["image", "picture", "video", "screen"]):
            for name, model in suitable_models:
                if "vision" in model.capabilities:
                    return name
                    
        # Return first suitable model
        return suitable_models[0][0]
        
    async def generate(
        self,
        model_name: str,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the specified model.
        
        Args:
            model_name: Name of the model to use
            prompt: The prompt to send
            system: System prompt (optional)
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        if model_name not in self._models:
            return {"error": f"Model {model_name} not found"}
            
        model = self._models[model_name]
        
        if model.backend == ModelBackend.OLLAMA:
            return await self._generate_ollama(model_name, prompt, system, **kwargs)
        elif model.backend == ModelBackend.LMSTUDIO:
            return await self._generate_lmstudio(model_name, prompt, system, **kwargs)
        elif model.backend == ModelBackend.LOCALAI:
            return await self._generate_localai(model_name, prompt, system, **kwargs)
        else:
            return {"error": f"Unsupported backend: {model.backend}"}
            
    async def _generate_ollama(
        self,
        model_name: str,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using Ollama."""
        url = self._backend_urls[ModelBackend.OLLAMA]
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
            
        payload.update(kwargs)
        
        try:
            async with self._session.post(
                f"{url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response": data.get("response", ""),
                        "model": model_name,
                        "backend": "ollama"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Ollama returned status {response.status}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _generate_lmstudio(
        self,
        model_name: str,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using LM Studio."""
        url = self._backend_urls[ModelBackend.LMSTUDIO]
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048)
        }
        
        try:
            async with self._session.post(
                f"{url}/v1/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "response": content,
                        "model": model_name,
                        "backend": "lmstudio"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"LM Studio returned status {response.status}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _generate_localai(
        self,
        model_name: str,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using LocalAI."""
        url = self._backend_urls[ModelBackend.LOCALAI]
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048)
        }
        
        try:
            async with self._session.post(
                f"{url}/v1/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "response": content,
                        "model": model_name,
                        "backend": "localai"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"LocalAI returned status {response.status}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def shutdown(self) -> None:
        """Shutdown the model manager."""
        if self._session:
            await self._session.close()
        self.logger.info("Model Manager shutdown complete")