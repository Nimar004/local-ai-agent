"""
File handler tool for reading, writing, and analyzing files.
"""

import asyncio
import logging
import os
import json
import csv
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


class FileAction(Enum):
    """Available file actions."""
    READ = "read"
    WRITE = "write"
    APPEND = "append"
    DELETE = "delete"
    LIST = "list"
    EXISTS = "exists"
    INFO = "info"
    SEARCH = "search"
    COPY = "copy"
    MOVE = "move"
    ANALYZE = "analyze"


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    name: str
    size: int
    extension: str
    is_directory: bool
    modified_time: float


class FileHandler:
    """
    Handles file operations for the AI Agent.
    
    Features:
    - Read and write files
    - File analysis and search
    - Directory listing
    - File information retrieval
    - Support for various file formats
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the File Handler.
        
        Args:
            base_path: Base path for file operations
        """
        self.logger = logging.getLogger("FileHandler")
        self._base_path = Path(base_path).resolve()
        
    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to the base path."""
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj.resolve()
        return (self._base_path / path_obj).resolve()
        
    async def execute_action(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a file action.
        
        Args:
            action: The action to perform
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        if params is None:
            params = {}
            
        try:
            action_enum = FileAction(action)
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
            
        # Execute the action
        if action_enum == FileAction.READ:
            return await self._read(params)
        elif action_enum == FileAction.WRITE:
            return await self._write(params)
        elif action_enum == FileAction.APPEND:
            return await self._append(params)
        elif action_enum == FileAction.DELETE:
            return await self._delete(params)
        elif action_enum == FileAction.LIST:
            return await self._list(params)
        elif action_enum == FileAction.EXISTS:
            return await self._exists(params)
        elif action_enum == FileAction.INFO:
            return await self._info(params)
        elif action_enum == FileAction.SEARCH:
            return await self._search(params)
        elif action_enum == FileAction.COPY:
            return await self._copy(params)
        elif action_enum == FileAction.MOVE:
            return await self._move(params)
        elif action_enum == FileAction.ANALYZE:
            return await self._analyze(params)
        else:
            return {
                "success": False,
                "error": f"Action not implemented: {action}"
            }
            
    async def _read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file."""
        path = params.get("path", "")
        encoding = params.get("encoding", None)
        
        if not path:
            return {"success": False, "error": "No path specified"}
            
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
            
        try:
            # Detect encoding if not specified
            if encoding is None and HAS_CHARDET:
                with open(file_path, "rb") as f:
                    raw_data = f.read()
                    detected = chardet.detect(raw_data)
                    encoding = detected.get("encoding", "utf-8")
            else:
                encoding = encoding or "utf-8"
                
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
                
            return {
                "success": True,
                "action": "read",
                "path": str(file_path),
                "content": content,
                "encoding": encoding
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write to a file."""
        path = params.get("path", "")
        content = params.get("content", "")
        encoding = params.get("encoding", "utf-8")
        
        if not path:
            return {"success": False, "error": "No path specified"}
            
        file_path = self._resolve_path(path)
        
        try:
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
                
            return {
                "success": True,
                "action": "write",
                "path": str(file_path),
                "bytes_written": len(content.encode(encoding))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _append(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Append to a file."""
        path = params.get("path", "")
        content = params.get("content", "")
        encoding = params.get("encoding", "utf-8")
        
        if not path:
            return {"success": False, "error": "No path specified"}
            
        file_path = self._resolve_path(path)
        
        try:
            with open(file_path, "a", encoding=encoding) as f:
                f.write(content)
                
            return {
                "success": True,
                "action": "append",
                "path": str(file_path),
                "bytes_appended": len(content.encode(encoding))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a file."""
        path = params.get("path", "")
        
        if not path:
            return {"success": False, "error": "No path specified"}
            
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
            
        try:
            if file_path.is_dir():
                file_path.rmdir()
            else:
                file_path.unlink()
                
            return {
                "success": True,
                "action": "delete",
                "path": str(file_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List files in a directory."""
        path = params.get("path", ".")
        recursive = params.get("recursive", False)
        
        dir_path = self._resolve_path(path)
        
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
            
        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}
            
        try:
            files = []
            
            if recursive:
                for item in dir_path.rglob("*"):
                    files.append({
                        "name": item.name,
                        "path": str(item.relative_to(self._base_path)),
                        "is_directory": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0
                    })
            else:
                for item in dir_path.iterdir():
                    files.append({
                        "name": item.name,
                        "path": str(item.relative_to(self._base_path)),
                        "is_directory": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0
                    })
                    
            return {
                "success": True,
                "action": "list",
                "path": str(dir_path),
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _exists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a file exists."""
        path = params.get("path", "")
        
        if not path:
            return {"success": False, "error": "No path specified"}
            
        file_path = self._resolve_path(path)
        
        return {
            "success": True,
            "action": "exists",
            "path": str(file_path),
            "exists": file_path.exists(),
            "is_file": file_path.is_file() if file_path.exists() else False,
            "is_directory": file_path.is_dir() if file_path.exists() else False
        }
        
    async def _info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get file information."""
        path = params.get("path", "")
        
        if not path:
            return {"success": False, "error": "No path specified"}
            
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
            
        try:
            stat = file_path.stat()
            
            return {
                "success": True,
                "action": "info",
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "extension": file_path.suffix,
                "is_directory": file_path.is_dir(),
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files matching a pattern."""
        path = params.get("path", ".")
        pattern = params.get("pattern", "*")
        
        dir_path = self._resolve_path(path)
        
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
            
        try:
            matches = []
            
            for item in dir_path.rglob(pattern):
                matches.append({
                    "name": item.name,
                    "path": str(item.relative_to(self._base_path)),
                    "is_directory": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0
                })
                
            return {
                "success": True,
                "action": "search",
                "path": str(dir_path),
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _copy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Copy a file."""
        source = params.get("source", "")
        destination = params.get("destination", "")
        
        if not source or not destination:
            return {"success": False, "error": "Source and destination required"}
            
        source_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)
        
        if not source_path.exists():
            return {"success": False, "error": f"Source not found: {source}"}
            
        try:
            import shutil
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
                
            return {
                "success": True,
                "action": "copy",
                "source": str(source_path),
                "destination": str(dest_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move a file."""
        source = params.get("source", "")
        destination = params.get("destination", "")
        
        if not source or not destination:
            return {"success": False, "error": "Source and destination required"}
            
        source_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)
        
        if not source_path.exists():
            return {"success": False, "error": f"Source not found: {source}"}
            
        try:
            import shutil
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))
            
            return {
                "success": True,
                "action": "move",
                "source": str(source_path),
                "destination": str(dest_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a file."""
        path = params.get("path", "")
        
        if not path:
            return {"success": False, "error": "No path specified"}
            
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
            
        try:
            # Get basic file info
            stat = file_path.stat()
            
            analysis = {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "extension": file_path.suffix,
                "is_directory": file_path.is_dir()
            }
            
            # Analyze content based on file type
            if file_path.is_file():
                extension = file_path.suffix.lower()
                
                if extension in [".txt", ".md", ".log"]:
                    # Text file analysis
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = content.split("\n")
                        analysis["line_count"] = len(lines)
                        analysis["word_count"] = len(content.split())
                        analysis["char_count"] = len(content)
                        
                elif extension == ".json":
                    # JSON file analysis
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        analysis["json_type"] = type(data).__name__
                        if isinstance(data, dict):
                            analysis["key_count"] = len(data.keys())
                        elif isinstance(data, list):
                            analysis["item_count"] = len(data)
                            
                elif extension == ".csv":
                    # CSV file analysis
                    with open(file_path, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        analysis["row_count"] = len(rows)
                        if rows:
                            analysis["column_count"] = len(rows[0])
                            
                elif extension in [".py", ".js", ".java", ".cpp", ".c"]:
                    # Code file analysis
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = content.split("\n")
                        analysis["line_count"] = len(lines)
                        analysis["non_empty_lines"] = len([l for l in lines if l.strip()])
                        
            return {
                "success": True,
                "action": "analyze",
                "analysis": analysis
            }
        except Exception as e:
            return {"success": False, "error": str(e)}