"""
Web access tool for browsing and interacting with websites.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

try:
    import aiohttp
    from aiohttp import ClientSession
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


class WebAction(Enum):
    """Available web actions."""
    FETCH = "fetch"
    SEARCH = "search"
    CLICK_ELEMENT = "click_element"
    FILL_FORM = "fill_form"
    EXTRACT_TEXT = "extract_text"
    EXTRACT_LINKS = "extract_links"
    SCREENSHOT = "screenshot"
    WAIT_FOR_ELEMENT = "wait_for_element"
    SCROLL = "scroll"


@dataclass
class WebPage:
    """Represents a web page."""
    url: str
    title: str
    content: str
    links: List[Dict[str, str]]
    status_code: int


class WebAccessor:
    """
    Accesses and interacts with websites.
    
    Features:
    - Fetch web pages
    - Extract text and links
    - Fill forms and click elements
    - Take screenshots
    - Support for both simple HTTP requests and browser automation
    """
    
    def __init__(self, use_browser: bool = False):
        """
        Initialize the Web Accessor.
        
        Args:
            use_browser: Whether to use browser automation (Selenium)
        """
        self.logger = logging.getLogger("WebAccessor")
        self._use_browser = use_browser
        self._session: Optional[ClientSession] = None
        self._driver: Optional[Any] = None
        
        if not HAS_AIOHTTP:
            self.logger.warning(
                "aiohttp not installed. Install with: pip install aiohttp"
            )
            
        if use_browser and not HAS_SELENIUM:
            self.logger.warning(
                "Selenium not installed. Browser automation disabled. "
                "Install with: pip install selenium"
            )
            self._use_browser = False
            
    async def initialize(self) -> None:
        """Initialize the web accessor."""
        if HAS_AIOHTTP:
            self._session = aiohttp.ClientSession()
            
        if self._use_browser and HAS_SELENIUM:
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self._driver = webdriver.Chrome(options=options)
                self.logger.info("Browser automation initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize browser: {e}")
                self._use_browser = False
                
    async def execute_action(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a web action.
        
        Args:
            action: The action to perform
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        if params is None:
            params = {}
            
        try:
            action_enum = WebAction(action)
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
            
        # Execute the action
        if action_enum == WebAction.FETCH:
            return await self._fetch(params)
        elif action_enum == WebAction.SEARCH:
            return await self._search(params)
        elif action_enum == WebAction.EXTRACT_TEXT:
            return await self._extract_text(params)
        elif action_enum == WebAction.EXTRACT_LINKS:
            return await self._extract_links(params)
        elif action_enum == WebAction.CLICK_ELEMENT:
            return await self._click_element(params)
        elif action_enum == WebAction.FILL_FORM:
            return await self._fill_form(params)
        elif action_enum == WebAction.SCREENSHOT:
            return await self._screenshot(params)
        elif action_enum == WebAction.WAIT_FOR_ELEMENT:
            return await self._wait_for_element(params)
        elif action_enum == WebAction.SCROLL:
            return await self._scroll(params)
        else:
            return {
                "success": False,
                "error": f"Action not implemented: {action}"
            }
            
    async def _fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch a web page."""
        url = params.get("url", "")
        
        if not url:
            return {"success": False, "error": "No URL specified"}
            
        if not self._session:
            return {"success": False, "error": "Session not initialized"}
            
        try:
            async with self._session.get(url) as response:
                content = await response.text()
                
                # Parse with BeautifulSoup if available
                title = ""
                if HAS_BS4:
                    soup = BeautifulSoup(content, "html.parser")
                    title_tag = soup.find("title")
                    title = title_tag.text if title_tag else ""
                    
                return {
                    "success": True,
                    "action": "fetch",
                    "url": url,
                    "status_code": response.status,
                    "title": title,
                    "content": content[:5000]  # Limit content size
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search the web."""
        query = params.get("query", "")
        engine = params.get("engine", "google")
        
        if not query:
            return {"success": False, "error": "No query specified"}
            
        # Construct search URL
        if engine == "google":
            url = f"https://www.google.com/search?q={query}"
        elif engine == "bing":
            url = f"https://www.bing.com/search?q={query}"
        elif engine == "duckduckgo":
            url = f"https://duckduckgo.com/?q={query}"
        else:
            return {"success": False, "error": f"Unknown search engine: {engine}"}
            
        # Fetch search results
        return await self._fetch({"url": url})
        
    async def _extract_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from a web page."""
        url = params.get("url", "")
        selector = params.get("selector", "body")
        
        if not url:
            return {"success": False, "error": "No URL specified"}
            
        if not HAS_BS4:
            return {"success": False, "error": "BeautifulSoup not installed"}
            
        if not self._session:
            return {"success": False, "error": "Session not initialized"}
            
        try:
            async with self._session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                
                elements = soup.select(selector)
                text = "\n".join([elem.get_text(strip=True) for elem in elements])
                
                return {
                    "success": True,
                    "action": "extract_text",
                    "url": url,
                    "selector": selector,
                    "text": text[:5000]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _extract_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract links from a web page."""
        url = params.get("url", "")
        
        if not url:
            return {"success": False, "error": "No URL specified"}
            
        if not HAS_BS4:
            return {"success": False, "error": "BeautifulSoup not installed"}
            
        if not self._session:
            return {"success": False, "error": "Session not initialized"}
            
        try:
            async with self._session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                
                links = []
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    text = link.get_text(strip=True)
                    
                    # Convert relative URLs to absolute
                    if href.startswith("/"):
                        parsed = urlparse(url)
                        href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        
                    links.append({
                        "url": href,
                        "text": text
                    })
                    
                return {
                    "success": True,
                    "action": "extract_links",
                    "url": url,
                    "links": links[:100]  # Limit number of links
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _click_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Click an element on a web page."""
        if not self._use_browser or not self._driver:
            return {
                "success": False,
                "error": "Browser automation not available"
            }
            
        selector = params.get("selector", "")
        
        if not selector:
            return {"success": False, "error": "No selector specified"}
            
        try:
            element = WebDriverWait(self._driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            
            return {
                "success": True,
                "action": "click_element",
                "selector": selector
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _fill_form(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fill a form on a web page."""
        if not self._use_browser or not self._driver:
            return {
                "success": False,
                "error": "Browser automation not available"
            }
            
        fields = params.get("fields", {})
        
        if not fields:
            return {"success": False, "error": "No fields specified"}
            
        try:
            for selector, value in fields.items():
                element = self._driver.find_element(By.CSS_SELECTOR, selector)
                element.clear()
                element.send_keys(value)
                
            return {
                "success": True,
                "action": "fill_form",
                "fields": list(fields.keys())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot of a web page."""
        if not self._use_browser or not self._driver:
            return {
                "success": False,
                "error": "Browser automation not available"
            }
            
        save_path = params.get("save_path", "screenshot.png")
        
        try:
            self._driver.save_screenshot(save_path)
            
            return {
                "success": True,
                "action": "screenshot",
                "path": save_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _wait_for_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for an element to appear."""
        if not self._use_browser or not self._driver:
            return {
                "success": False,
                "error": "Browser automation not available"
            }
            
        selector = params.get("selector", "")
        timeout = params.get("timeout", 10)
        
        if not selector:
            return {"success": False, "error": "No selector specified"}
            
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            return {
                "success": True,
                "action": "wait_for_element",
                "selector": selector,
                "found": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scroll the page."""
        if not self._use_browser or not self._driver:
            return {
                "success": False,
                "error": "Browser automation not available"
            }
            
        direction = params.get("direction", "down")
        amount = params.get("amount", 500)
        
        try:
            if direction == "down":
                self._driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                self._driver.execute_script(f"window.scrollBy(0, -{amount});")
            else:
                return {"success": False, "error": f"Unknown direction: {direction}"}
                
            return {
                "success": True,
                "action": "scroll",
                "direction": direction,
                "amount": amount
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL using the browser."""
        if not self._use_browser or not self._driver:
            return {
                "success": False,
                "error": "Browser automation not available"
            }
            
        try:
            self._driver.get(url)
            
            return {
                "success": True,
                "action": "navigate",
                "url": url,
                "title": self._driver.title
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def shutdown(self) -> None:
        """Shutdown the web accessor."""
        if self._session:
            await self._session.close()
            
        if self._driver:
            self._driver.quit()
            
        self.logger.info("Web Accessor shutdown complete")