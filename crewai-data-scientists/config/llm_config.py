"""LLM configuration for CrewAI agents."""

import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


def get_llm() -> LLM:
    """Initialize and return the configured LLM for CrewAI agents."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Please create a .env file with your API key."
        )

    return LLM(
        model="claude-sonnet-4-5-20250929",
        temperature=0.1,
        max_tokens=4096,
        api_key=api_key,
    )


if __name__ == "__main__":
    try:
        llm = get_llm()
        print(f"LLM configured: {llm.model}")
    except Exception as e:
        print(f"LLM configuration failed: {e}")
