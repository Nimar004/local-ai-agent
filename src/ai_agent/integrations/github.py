"""
GitHub Integration for AI Agent.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import aiohttp

from .base import BaseIntegration, IntegrationConfig


class GitHubIntegration(BaseIntegration):
    """
    GitHub integration for AI Agent.
    
    Features:
    - List repositories
    - Get repository info
    - List issues
    - Create issues
    - List pull requests
    - Get file contents
    """
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        """Initialize GitHub integration."""
        default_config = IntegrationConfig(
            name="github",
            api_url="https://api.github.com"
        )
        super().__init__(config or default_config)
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def _initialize(self) -> bool:
        """Initialize GitHub integration."""
        try:
            # Create HTTP session
            self._session = aiohttp.ClientSession()
            
            # Test connection
            if self._config.api_key:
                headers = {
                    "Authorization": f"token {self._config.api_key}",
                    "Accept": "application/vnd.github.v3+json"
                }
            else:
                headers = {
                    "Accept": "application/vnd.github.v3+json"
                }
                
            async with self._session.get(
                f"{self._config.api_url}/rate_limit",
                headers=headers
            ) as response:
                if response.status == 200:
                    self.logger.info("GitHub API connection successful")
                    return True
                else:
                    self.logger.error(f"GitHub API connection failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"GitHub initialization error: {e}")
            return False
            
    async def _enable(self) -> bool:
        """Enable GitHub integration."""
        return True
        
    async def _disable(self) -> bool:
        """Disable GitHub integration."""
        if self._session:
            await self._session.close()
        return True
        
    async def _execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub action."""
        actions = {
            "list_repos": self._list_repos,
            "get_repo": self._get_repo,
            "list_issues": self._list_issues,
            "create_issue": self._create_issue,
            "list_prs": self._list_prs,
            "get_file": self._get_file
        }
        
        if action not in actions:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
            
        return await actions[action](params)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self._config.api_key:
            headers["Authorization"] = f"token {self._config.api_key}"
            
        return headers
        
    async def _list_repos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List repositories."""
        try:
            username = params.get("username")
            org = params.get("org")
            
            if username:
                url = f"{self._config.api_url}/users/{username}/repos"
            elif org:
                url = f"{self._config.api_url}/orgs/{org}/repos"
            else:
                url = f"{self._config.api_url}/user/repos"
                
            async with self._session.get(
                url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    repos = await response.json()
                    return {
                        "success": True,
                        "repos": [
                            {
                                "name": repo["name"],
                                "full_name": repo["full_name"],
                                "description": repo["description"],
                                "url": repo["html_url"],
                                "stars": repo["stargazers_count"],
                                "forks": repo["forks_count"]
                            }
                            for repo in repos
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to list repos: {response.status}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _get_repo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get repository information."""
        try:
            owner = params.get("owner")
            repo = params.get("repo")
            
            if not owner or not repo:
                return {
                    "success": False,
                    "error": "owner and repo required"
                }
                
            url = f"{self._config.api_url}/repos/{owner}/{repo}"
            
            async with self._session.get(
                url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    repo_data = await response.json()
                    return {
                        "success": True,
                        "repo": {
                            "name": repo_data["name"],
                            "full_name": repo_data["full_name"],
                            "description": repo_data["description"],
                            "url": repo_data["html_url"],
                            "stars": repo_data["stargazers_count"],
                            "forks": repo_data["forks_count"],
                            "language": repo_data["language"],
                            "created_at": repo_data["created_at"],
                            "updated_at": repo_data["updated_at"]
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get repo: {response.status}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _list_issues(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List issues in a repository."""
        try:
            owner = params.get("owner")
            repo = params.get("repo")
            state = params.get("state", "open")
            
            if not owner or not repo:
                return {
                    "success": False,
                    "error": "owner and repo required"
                }
                
            url = f"{self._config.api_url}/repos/{owner}/{repo}/issues"
            
            async with self._session.get(
                url,
                headers=self._get_headers(),
                params={"state": state}
            ) as response:
                if response.status == 200:
                    issues = await response.json()
                    return {
                        "success": True,
                        "issues": [
                            {
                                "number": issue["number"],
                                "title": issue["title"],
                                "state": issue["state"],
                                "url": issue["html_url"],
                                "created_at": issue["created_at"],
                                "user": issue["user"]["login"]
                            }
                            for issue in issues
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to list issues: {response.status}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _create_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an issue in a repository."""
        try:
            owner = params.get("owner")
            repo = params.get("repo")
            title = params.get("title")
            body = params.get("body", "")
            
            if not owner or not repo or not title:
                return {
                    "success": False,
                    "error": "owner, repo, and title required"
                }
                
            url = f"{self._config.api_url}/repos/{owner}/{repo}/issues"
            
            data = {
                "title": title,
                "body": body
            }
            
            async with self._session.post(
                url,
                headers=self._get_headers(),
                json=data
            ) as response:
                if response.status == 201:
                    issue = await response.json()
                    return {
                        "success": True,
                        "issue": {
                            "number": issue["number"],
                            "title": issue["title"],
                            "url": issue["html_url"]
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create issue: {response.status}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _list_prs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List pull requests in a repository."""
        try:
            owner = params.get("owner")
            repo = params.get("repo")
            state = params.get("state", "open")
            
            if not owner or not repo:
                return {
                    "success": False,
                    "error": "owner and repo required"
                }
                
            url = f"{self._config.api_url}/repos/{owner}/{repo}/pulls"
            
            async with self._session.get(
                url,
                headers=self._get_headers(),
                params={"state": state}
            ) as response:
                if response.status == 200:
                    prs = await response.json()
                    return {
                        "success": True,
                        "pull_requests": [
                            {
                                "number": pr["number"],
                                "title": pr["title"],
                                "state": pr["state"],
                                "url": pr["html_url"],
                                "created_at": pr["created_at"],
                                "user": pr["user"]["login"]
                            }
                            for pr in prs
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to list PRs: {response.status}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _get_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get file contents from a repository."""
        try:
            owner = params.get("owner")
            repo = params.get("repo")
            path = params.get("path")
            ref = params.get("ref", "main")
            
            if not owner or not repo or not path:
                return {
                    "success": False,
                    "error": "owner, repo, and path required"
                }
                
            url = f"{self._config.api_url}/repos/{owner}/{repo}/contents/{path}"
            
            async with self._session.get(
                url,
                headers=self._get_headers(),
                params={"ref": ref}
            ) as response:
                if response.status == 200:
                    file_data = await response.json()
                    
                    # Decode content if it's base64 encoded
                    import base64
                    content = base64.b64decode(file_data["content"]).decode("utf-8")
                    
                    return {
                        "success": True,
                        "file": {
                            "name": file_data["name"],
                            "path": file_data["path"],
                            "size": file_data["size"],
                            "content": content,
                            "url": file_data["html_url"]
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get file: {response.status}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}