"""
LLM Configuration Module
Manages configuration for Anthropic Claude

Based on concepts from Dr. Ryan Ahmed's LLM Engineering course on Multi-Agent AI Systems
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMConfigManager:
    """Manages LLM configurations for multi-model agent systems"""

    def __init__(self):
        """Initialize LLM configuration manager with API keys from environment"""
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Validate that required API keys are present
        self._validate_api_keys()

    def _validate_api_keys(self) -> None:
        """Validate that required API keys are loaded"""
        if not self.anthropic_api_key:
            raise ValueError(
                "Missing required API key: ANTHROPIC_API_KEY. "
                "Please check your .env file."
            )

    def get_claude_config(
        self,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.7,
        timeout: int = 120,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Get Anthropic Claude configuration for AG2/AutoGen agents

        Args:
            model: Claude model name (claude-3-5-sonnet, etc.)
            temperature: Sampling temperature (0.0-1.0 for Claude)
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens in response (default 4096)

        Returns:
            Configuration dictionary for AG2/AutoGen
        """
        config_list = [
            {
                "model": model,
                "api_key": self.anthropic_api_key,
                "api_type": "anthropic",
                "max_tokens": max_tokens,
            }
        ]

        return {
            "config_list": config_list,
            "temperature": temperature,
            "timeout": timeout,
        }

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all LLM configurations at once

        Returns:
            Dictionary with configurations for all providers
        """
        return {
            "claude": self.get_claude_config(),
        }


# Singleton instance for easy import
config_manager = LLMConfigManager()
