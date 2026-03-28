"""
Integrations Module for AI Agent
Provides connections to external services and APIs.
"""

from .github import GitHubIntegration
from .slack import SlackIntegration
from .email import EmailIntegration
from .calendar import CalendarIntegration
from .weather import WeatherIntegration
from .news import NewsIntegration

__all__ = [
    "GitHubIntegration",
    "SlackIntegration",
    "EmailIntegration",
    "CalendarIntegration",
    "WeatherIntegration",
    "NewsIntegration"
]