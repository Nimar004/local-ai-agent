"""
Web server for the AI Agent system.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from aiohttp import web, WSMsgType
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

from ..core.agent import AIAgent, AgentConfig, AgentMode


class WebServer:
    """
    Web server for the AI Agent system.
    
    Features:
    - REST API for task execution
    - WebSocket for real-time communication
    - Web interface for user interaction
    - Model management endpoints
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initialize the Web Server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        self.logger = logging.getLogger("WebServer")
        self._host = host
        self._port = port
        self._app: Optional[web.Application] = None
        self._agent: Optional[AIAgent] = None
        self._websockets: List[web.WebSocketResponse] = []
        
        if not HAS_AIOHTTP:
            self.logger.warning(
                "aiohttp not installed. Web interface will not be available. "
                "Install with: pip install aiohttp"
            )
            
    async def initialize(self) -> None:
        """Initialize the web server."""
        if not HAS_AIOHTTP:
            raise RuntimeError("aiohttp not installed")
            
        # Create agent
        config = AgentConfig(mode=AgentMode.WEB)
        self._agent = AIAgent(config)
        await self._agent.initialize()
        
        # Create web application
        self._app = web.Application()
        self._setup_routes()
        
        self.logger.info(f"Web server initialized on {self._host}:{self._port}")
        
    def _setup_routes(self) -> None:
        """Set up the routes for the web server."""
        # API routes
        self._app.router.add_post("/api/execute", self._handle_execute)
        self._app.router.add_post("/api/generate", self._handle_generate)
        self._app.router.add_post("/api/analyze", self._handle_analyze)
        self._app.router.add_get("/api/models", self._handle_list_models)
        self._app.router.add_get("/api/models/{name}", self._handle_model_info)
        self._app.router.add_get("/api/config", self._handle_get_config)
        
        # WebSocket route
        self._app.router.add_get("/ws", self._handle_websocket)
        
        # Static files
        static_path = Path(__file__).parent / "static"
        if static_path.exists():
            self._app.router.add_static("/", static_path)
            
    async def _handle_execute(self, request: web.Request) -> web.Response:
        """Handle task execution requests."""
        try:
            data = await request.json()
            task = data.get("task", "")
            model = data.get("model")
            context = data.get("context")
            
            if not task:
                return web.json_response(
                    {"success": False, "error": "No task specified"},
                    status=400
                )
                
            result = await self._agent.execute_task(task, model, context)
            return web.json_response(result)
            
        except Exception as e:
            self.logger.error(f"Execute error: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )
            
    async def _handle_generate(self, request: web.Request) -> web.Response:
        """Handle code generation requests."""
        try:
            data = await request.json()
            description = data.get("description", "")
            language = data.get("language", "python")
            model = data.get("model")
            
            if not description:
                return web.json_response(
                    {"success": False, "error": "No description specified"},
                    status=400
                )
                
            result = await self._agent.generate_code(description, language, model)
            return web.json_response(result)
            
        except Exception as e:
            self.logger.error(f"Generate error: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )
            
    async def _handle_analyze(self, request: web.Request) -> web.Response:
        """Handle file analysis requests."""
        try:
            data = await request.json()
            file_path = data.get("file", "")
            analysis_type = data.get("type", "general")
            
            if not file_path:
                return web.json_response(
                    {"success": False, "error": "No file specified"},
                    status=400
                )
                
            result = await self._agent.analyze_file(file_path, analysis_type)
            return web.json_response(result)
            
        except Exception as e:
            self.logger.error(f"Analyze error: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )
            
    async def _handle_list_models(self, request: web.Request) -> web.Response:
        """Handle list models requests."""
        try:
            models = await self._agent.list_available_models()
            return web.json_response({"success": True, "models": models})
            
        except Exception as e:
            self.logger.error(f"List models error: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )
            
    async def _handle_model_info(self, request: web.Request) -> web.Response:
        """Handle model info requests."""
        try:
            model_name = request.match_info["name"]
            info = await self._agent.get_model_info(model_name)
            return web.json_response(info)
            
        except Exception as e:
            self.logger.error(f"Model info error: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )
            
    async def _handle_get_config(self, request: web.Request) -> web.Response:
        """Handle get config requests."""
        try:
            config = {
                "mode": self._agent.config.mode.value,
                "default_model": self._agent.config.default_model,
                "max_concurrent_tasks": self._agent.config.max_concurrent_tasks,
                "enable_screen_control": self._agent.config.enable_screen_control,
                "enable_web_access": self._agent.config.enable_web_access,
                "enable_file_access": self._agent.config.enable_file_access,
                "cache_enabled": self._agent.config.cache_enabled,
                "log_level": self._agent.config.log_level
            }
            return web.json_response({"success": True, "config": config})
            
        except Exception as e:
            self.logger.error(f"Get config error: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )
            
    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self._websockets.append(ws)
        self.logger.info("WebSocket client connected")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_ws_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_json({
                            "success": False,
                            "error": "Invalid JSON"
                        })
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {ws.exception()}")
                    
        finally:
            self._websockets.remove(ws)
            self.logger.info("WebSocket client disconnected")
            
        return ws
        
    async def _handle_ws_message(
        self,
        ws: web.WebSocketResponse,
        data: Dict[str, Any]
    ) -> None:
        """Handle WebSocket messages."""
        action = data.get("action", "")
        
        if action == "execute":
            task = data.get("task", "")
            model = data.get("model")
            context = data.get("context")
            
            if not task:
                await ws.json({
                    "success": False,
                    "error": "No task specified"
                })
                return
                
            result = await self._agent.execute_task(task, model, context)
            await ws.json(result)
            
        elif action == "generate":
            description = data.get("description", "")
            language = data.get("language", "python")
            model = data.get("model")
            
            if not description:
                await ws.json({
                    "success": False,
                    "error": "No description specified"
                })
                return
                
            result = await self._agent.generate_code(description, language, model)
            await ws.json(result)
            
        elif action == "ping":
            await ws.json({"action": "pong"})
            
        else:
            await ws.json({
                "success": False,
                "error": f"Unknown action: {action}"
            })
            
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connected WebSocket clients."""
        for ws in self._websockets:
            try:
                await ws.json(message)
            except Exception as e:
                self.logger.error(f"Broadcast error: {e}")
                
    async def start(self) -> None:
        """Start the web server."""
        if not self._app:
            await self.initialize()
            
        runner = web.AppRunner(self._app)
        await runner.setup()
        
        site = web.TCPSite(runner, self._host, self._port)
        await site.start()
        
        self.logger.info(f"Web server started on http://{self._host}:{self._port}")
        
    async def stop(self) -> None:
        """Stop the web server."""
        # Close all WebSocket connections
        for ws in self._websockets:
            await ws.close()
            
        # Shutdown agent
        if self._agent:
            await self._agent.shutdown()
            
        self.logger.info("Web server stopped")
        
    def run(self) -> None:
        """Run the web server (blocking)."""
        if not HAS_AIOHTTP:
            self.logger.error("Cannot run web server: aiohttp not installed")
            return
            
        loop = asyncio.get_event_loop()
        
        try:
            loop.run_until_complete(self.start())
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(self.stop())