"""
Screen control tool for automating screen interactions.
"""

import asyncio
import logging
import platform
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import pyautogui
    import pygetwindow as gw
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ScreenAction(Enum):
    """Available screen actions."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    PRESS = "press"
    HOTKEY = "hotkey"
    SCROLL = "scroll"
    MOVE = "move"
    DRAG = "drag"
    SCREENSHOT = "screenshot"
    FIND_WINDOW = "find_window"
    ACTIVATE_WINDOW = "activate_window"
    RESIZE_WINDOW = "resize_window"
    MOVE_WINDOW = "move_window"


@dataclass
class ScreenPosition:
    """Represents a position on screen."""
    x: int
    y: int


@dataclass
class WindowInfo:
    """Information about a window."""
    title: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    is_active: bool


class ScreenController:
    """
    Controls screen interactions for automation.
    
    Features:
    - Mouse control (click, move, drag)
    - Keyboard control (type, press, hotkey)
    - Window management
    - Screen capture
    - Cross-platform support (macOS, Windows, Linux)
    """
    
    def __init__(self):
        """Initialize the Screen Controller."""
        self.logger = logging.getLogger("ScreenController")
        self._platform = platform.system()
        
        if not HAS_PYAUTOGUI:
            self.logger.warning(
                "pyautogui not installed. Screen control features will be limited. "
                "Install with: pip install pyautogui pygetwindow pillow"
            )
            
        # Configure pyautogui
        if HAS_PYAUTOGUI:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            
    def is_available(self) -> bool:
        """Check if screen control is available."""
        return HAS_PYAUTOGUI
        
    async def execute_action(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a screen action.
        
        Args:
            action: The action to perform
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Screen control not available. Install pyautogui."
            }
            
        if params is None:
            params = {}
            
        try:
            action_enum = ScreenAction(action)
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
            
        # Execute the action
        if action_enum == ScreenAction.CLICK:
            return await self._click(params)
        elif action_enum == ScreenAction.DOUBLE_CLICK:
            return await self._double_click(params)
        elif action_enum == ScreenAction.RIGHT_CLICK:
            return await self._right_click(params)
        elif action_enum == ScreenAction.TYPE:
            return await self._type(params)
        elif action_enum == ScreenAction.PRESS:
            return await self._press(params)
        elif action_enum == ScreenAction.HOTKEY:
            return await self._hotkey(params)
        elif action_enum == ScreenAction.SCROLL:
            return await self._scroll(params)
        elif action_enum == ScreenAction.MOVE:
            return await self._move(params)
        elif action_enum == ScreenAction.DRAG:
            return await self._drag(params)
        elif action_enum == ScreenAction.SCREENSHOT:
            return await self._screenshot(params)
        elif action_enum == ScreenAction.FIND_WINDOW:
            return await self._find_window(params)
        elif action_enum == ScreenAction.ACTIVATE_WINDOW:
            return await self._activate_window(params)
        elif action_enum == ScreenAction.RESIZE_WINDOW:
            return await self._resize_window(params)
        elif action_enum == ScreenAction.MOVE_WINDOW:
            return await self._move_window(params)
        else:
            return {
                "success": False,
                "error": f"Action not implemented: {action}"
            }
            
    async def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Click at a position."""
        x = params.get("x")
        y = params.get("y")
        button = params.get("button", "left")
        
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
        else:
            pyautogui.click(button=button)
            
        return {"success": True, "action": "click"}
        
    async def _double_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Double click at a position."""
        x = params.get("x")
        y = params.get("y")
        
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
            
        return {"success": True, "action": "double_click"}
        
    async def _right_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Right click at a position."""
        x = params.get("x")
        y = params.get("y")
        
        if x is not None and y is not None:
            pyautogui.rightClick(x, y)
        else:
            pyautogui.rightClick()
            
        return {"success": True, "action": "right_click"}
        
    async def _type(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Type text."""
        text = params.get("text", "")
        interval = params.get("interval", 0.02)
        
        pyautogui.typewrite(text, interval=interval)
        
        return {"success": True, "action": "type", "text": text}
        
    async def _press(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Press a key."""
        key = params.get("key", "")
        
        if not key:
            return {"success": False, "error": "No key specified"}
            
        pyautogui.press(key)
        
        return {"success": True, "action": "press", "key": key}
        
    async def _hotkey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Press a hotkey combination."""
        keys = params.get("keys", [])
        
        if not keys:
            return {"success": False, "error": "No keys specified"}
            
        pyautogui.hotkey(*keys)
        
        return {"success": True, "action": "hotkey", "keys": keys}
        
    async def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scroll the mouse wheel."""
        clicks = params.get("clicks", 1)
        x = params.get("x")
        y = params.get("y")
        
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks)
            
        return {"success": True, "action": "scroll", "clicks": clicks}
        
    async def _move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move the mouse."""
        x = params.get("x")
        y = params.get("y")
        duration = params.get("duration", 0.25)
        
        if x is None or y is None:
            return {"success": False, "error": "x and y required"}
            
        pyautogui.moveTo(x, y, duration=duration)
        
        return {"success": True, "action": "move", "x": x, "y": y}
        
    async def _drag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Drag the mouse."""
        start_x = params.get("start_x")
        start_y = params.get("start_y")
        end_x = params.get("end_x")
        end_y = params.get("end_y")
        duration = params.get("duration", 0.5)
        button = params.get("button", "left")
        
        if None in [start_x, start_y, end_x, end_y]:
            return {"success": False, "error": "start_x, start_y, end_x, end_y required"}
            
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)
        
        return {"success": True, "action": "drag"}
        
    async def _screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot."""
        region = params.get("region")
        save_path = params.get("save_path")
        
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
            
        if save_path:
            screenshot.save(save_path)
            return {
                "success": True,
                "action": "screenshot",
                "path": save_path
            }
        else:
            # Return base64 encoded image
            import io
            import base64
            
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "success": True,
                "action": "screenshot",
                "image_base64": img_str
            }
            
    async def _find_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find a window by title."""
        title = params.get("title", "")
        
        if not title:
            return {"success": False, "error": "No title specified"}
            
        try:
            windows = gw.getWindowsWithTitle(title)
            
            if not windows:
                return {
                    "success": False,
                    "error": f"No window found with title: {title}"
                }
                
            window_list = []
            for win in windows:
                window_list.append({
                    "title": win.title,
                    "position": (win.left, win.top),
                    "size": (win.width, win.height),
                    "is_active": win.isActive
                })
                
            return {
                "success": True,
                "action": "find_window",
                "windows": window_list
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _activate_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a window."""
        title = params.get("title", "")
        
        if not title:
            return {"success": False, "error": "No title specified"}
            
        try:
            windows = gw.getWindowsWithTitle(title)
            
            if not windows:
                return {
                    "success": False,
                    "error": f"No window found with title: {title}"
                }
                
            window = windows[0]
            window.activate()
            
            return {
                "success": True,
                "action": "activate_window",
                "title": window.title
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _resize_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resize a window."""
        title = params.get("title", "")
        width = params.get("width")
        height = params.get("height")
        
        if not title:
            return {"success": False, "error": "No title specified"}
            
        if width is None or height is None:
            return {"success": False, "error": "width and height required"}
            
        try:
            windows = gw.getWindowsWithTitle(title)
            
            if not windows:
                return {
                    "success": False,
                    "error": f"No window found with title: {title}"
                }
                
            window = windows[0]
            window.resizeTo(width, height)
            
            return {
                "success": True,
                "action": "resize_window",
                "title": window.title,
                "size": (width, height)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _move_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move a window."""
        title = params.get("title", "")
        x = params.get("x")
        y = params.get("y")
        
        if not title:
            return {"success": False, "error": "No title specified"}
            
        if x is None or y is None:
            return {"success": False, "error": "x and y required"}
            
        try:
            windows = gw.getWindowsWithTitle(title)
            
            if not windows:
                return {
                    "success": False,
                    "error": f"No window found with title: {title}"
                }
                
            window = windows[0]
            window.moveTo(x, y)
            
            return {
                "success": True,
                "action": "move_window",
                "title": window.title,
                "position": (x, y)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the screen size."""
        if HAS_PYAUTOGUI:
            return pyautogui.size()
        return (0, 0)
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position."""
        if HAS_PYAUTOGUI:
            return pyautogui.position()
        return (0, 0)