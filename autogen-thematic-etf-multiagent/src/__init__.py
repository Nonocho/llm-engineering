"""
Thematic ETF Advisor - Multi-Agent AI System
Main package initialization
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Multi-Agent AI System for Thematic ETF Analysis and Marketing"

from .agents import AgentFactory, create_agent_team
from .config import config_manager
from .ui import launch_app

__all__ = [
    "AgentFactory",
    "create_agent_team",
    "config_manager",
    "launch_app",
]
