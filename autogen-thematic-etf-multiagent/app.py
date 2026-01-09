"""
Thematic ETF Advisor - Main Application Entry Point

A Multi-Agent AI System for analyzing and marketing thematic equity ETFs
with focus on AI & Technology Innovation.

This project demonstrates:
- Multi-model agent collaboration (Google Gemini, Anthropic Claude)
- AutoGen framework for agent orchestration
- Gradio web interface for interactive user experience
- Professional software engineering practices

Based on concepts from Dr. Ryan Ahmed's LLM Engineering course:
"Building Interactive Multi-Model AI Agent Teams with AutoGen"

Author: [Your Name]
Date: 2024
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ui import launch_app


def main():
    """Main application entry point"""

    parser = argparse.ArgumentParser(
        description="Thematic ETF Advisor - Multi-Agent AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                    # Launch with default settings
  python app.py --share            # Launch with public sharing enabled
  python app.py --port 8080        # Launch on custom port

Attribution:
  Based on Dr. Ryan Ahmed's LLM Engineering course on Multi-Agent AI Systems
        """
    )

    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public share link for the Gradio interface"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run the Gradio server on (default: 7860)"
    )

    args = parser.parse_args()

    # Print welcome banner
    try:
        print("=" * 70)
        print("  🎯 THEMATIC ETF ADVISOR - Multi-Agent AI System")
        print("=" * 70)
        print()
        print("  📊 Focus: AI & Technology Innovation ETFs")
        print("  🤖 Agents: 4 AI specialists (Gemini, Claude)")
        print("  🌐 Interface: Interactive Gradio Web UI")
        print()
        print("  📚 Based on Dr. Ryan Ahmed's LLM Engineering Course")
        print("     'Building Interactive Multi-Model AI Agent Teams with AutoGen'")
        print()
        print("=" * 70)
        print()
    except UnicodeEncodeError:
        # Fallback for terminals that don't support emojis
        print("=" * 70)
        print("  THEMATIC ETF ADVISOR - Multi-Agent AI System")
        print("=" * 70)
        print()
        print("  Focus: AI & Technology Innovation ETFs")
        print("  Agents: 4 AI specialists (Gemini, Claude)")
        print("  Interface: Interactive Gradio Web UI")
        print()
        print("  Based on Dr. Ryan Ahmed's LLM Engineering Course")
        print("  'Building Interactive Multi-Model AI Agent Teams with AutoGen'")
        print()
        print("=" * 70)
        print()

    # Check for .env file
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        try:
            print("⚠️  WARNING: .env file not found!")
            print("📝 Please copy .env.example to .env and add your API keys:")
            print("   - GOOGLE_API_KEY")
            print("   - ANTHROPIC_API_KEY")
            print()
            print("💡 You can still launch the app, but you'll need to add keys")
            print("   before initializing the agent team.")
            print()
        except UnicodeEncodeError:
            print("WARNING: .env file not found!")
            print("Please copy .env.example to .env and add your API keys:")
            print("   - GOOGLE_API_KEY")
            print("   - ANTHROPIC_API_KEY")
            print()
            print("You can still launch the app, but you'll need to add keys")
            print("before initializing the agent team.")
            print()

    # Launch the application
    try:
        launch_app(share=args.share, server_port=args.port)
    except KeyboardInterrupt:
        try:
            print("\n\n👋 Application stopped by user. Goodbye!")
        except UnicodeEncodeError:
            print("\n\nApplication stopped by user. Goodbye!")
    except Exception as e:
        try:
            print(f"\n❌ Error launching application: {str(e)}")
        except UnicodeEncodeError:
            print(f"\nError launching application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
