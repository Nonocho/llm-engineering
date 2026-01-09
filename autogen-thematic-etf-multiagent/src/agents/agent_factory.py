"""
Agent Factory Module
Creates and configures multi-model AI agents for thematic ETF analysis

Based on AutoGen multi-agent concepts from Dr. Ryan Ahmed's LLM Engineering course
"""

import autogen
from typing import Dict, Any, List
from .prompts import (
    CIO_PROMPT,
    PORTFOLIO_ANALYST_PROMPT,
    MARKET_RESEARCH_PROMPT,
    MARKETING_STRATEGIST_PROMPT,
    USER_PROXY_MESSAGE,
)
from ..config import config_manager


class AgentFactory:
    """Factory class for creating AutoGen agents with different LLM backends"""

    def __init__(self):
        """Initialize agent factory with LLM configurations"""
        self.config_manager = config_manager
        self.agents = {}

    def create_cio_agent(self) -> autogen.ConversableAgent:
        """
        Create Chief Investment Officer agent using Anthropic Claude

        Claude is chosen for strategic thinking and high-level planning

        Returns:
            ConversableAgent configured as CIO
        """
        claude_config = self.config_manager.get_claude_config(
            temperature=0.6  # Lower temperature for strategic, consistent responses
        )

        agent = autogen.ConversableAgent(
            name="Chief_Investment_Officer",
            system_message=CIO_PROMPT,
            llm_config=claude_config,
            human_input_mode="NEVER",
        )

        self.agents["cio"] = agent
        return agent

    def create_portfolio_analyst_agent(self) -> autogen.ConversableAgent:
        """
        Create Portfolio Analyst agent using Anthropic Claude

        Claude is chosen for detailed analytical work and quantitative reasoning

        Returns:
            ConversableAgent configured as Portfolio Analyst
        """
        claude_config = self.config_manager.get_claude_config(
            temperature=0.5  # Low temperature for precise, factual analysis
        )

        agent = autogen.ConversableAgent(
            name="Portfolio_Analyst",
            system_message=PORTFOLIO_ANALYST_PROMPT,
            llm_config=claude_config,
            human_input_mode="NEVER",
        )

        self.agents["portfolio_analyst"] = agent
        return agent

    def create_market_research_agent(self) -> autogen.ConversableAgent:
        """
        Create Market Research agent using Anthropic Claude

        Claude is chosen for its broad knowledge base and research capabilities

        Returns:
            ConversableAgent configured as Market Researcher
        """
        claude_config = self.config_manager.get_claude_config(
            temperature=0.7  # Moderate temperature for insightful analysis
        )

        agent = autogen.ConversableAgent(
            name="Market_Research_Specialist",
            system_message=MARKET_RESEARCH_PROMPT,
            llm_config=claude_config,
            human_input_mode="NEVER",
        )

        self.agents["market_research"] = agent
        return agent

    def create_marketing_strategist_agent(self) -> autogen.ConversableAgent:
        """
        Create Marketing Strategist agent using Anthropic Claude

        Claude is chosen for creative, nuanced communication and marketing copy

        Returns:
            ConversableAgent configured as Marketing Strategist
        """
        claude_config = self.config_manager.get_claude_config(
            temperature=0.7  # Balanced temperature for creative yet professional output
        )

        agent = autogen.ConversableAgent(
            name="Marketing_Strategist",
            system_message=MARKETING_STRATEGIST_PROMPT,
            llm_config=claude_config,
            human_input_mode="NEVER",
        )

        self.agents["marketing_strategist"] = agent
        return agent

    def create_user_proxy_agent(
        self,
        human_input_mode: str = "ALWAYS"
    ) -> autogen.UserProxyAgent:
        """
        Create User Proxy agent for human interaction

        Args:
            human_input_mode: When to request human input ("ALWAYS", "NEVER", "TERMINATE")

        Returns:
            UserProxyAgent configured for human interaction
        """
        agent = autogen.UserProxyAgent(
            name="Human_User",
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=0,  # No auto-replies from user proxy
            is_termination_msg=lambda x: x.get("content", "").rstrip().lower()
            in ["exit", "quit", "terminate", "stop"],
            code_execution_config=False,
            system_message=USER_PROXY_MESSAGE,
        )

        self.agents["user_proxy"] = agent
        return agent

    def create_all_agents(
        self,
        include_user_proxy: bool = True,
        user_input_mode: str = "ALWAYS"
    ) -> Dict[str, Any]:
        """
        Create all agents at once and return them as a dictionary

        Args:
            include_user_proxy: Whether to create user proxy agent
            user_input_mode: Human input mode for user proxy

        Returns:
            Dictionary of agent name to agent instance
        """
        agents = {
            "cio": self.create_cio_agent(),
            "portfolio_analyst": self.create_portfolio_analyst_agent(),
            "market_research": self.create_market_research_agent(),
            "marketing_strategist": self.create_marketing_strategist_agent(),
        }

        if include_user_proxy:
            agents["user_proxy"] = self.create_user_proxy_agent(user_input_mode)

        return agents

    def get_agent_list(self) -> List[autogen.ConversableAgent]:
        """
        Get list of all created agents for GroupChat

        Returns:
            List of agent instances
        """
        return list(self.agents.values())

    def reset_all_agents(self) -> None:
        """Reset conversation history for all agents"""
        for agent in self.agents.values():
            agent.reset()


# Convenience function for creating agents
def create_agent_team(
    include_user_proxy: bool = True,
    user_input_mode: str = "ALWAYS"
) -> Dict[str, Any]:
    """
    Convenience function to create complete agent team

    Args:
        include_user_proxy: Whether to include user proxy agent
        user_input_mode: Human input mode for user proxy

    Returns:
        Dictionary of agent instances
    """
    factory = AgentFactory()
    return factory.create_all_agents(include_user_proxy, user_input_mode)
