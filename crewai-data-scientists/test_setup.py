"""Quick setup verification for the CrewAI Data Scientists project."""

import os
import sys
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    modules = [
        ("gradio", "Gradio"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("sklearn.ensemble", "Scikit-learn"),
        ("crewai", "CrewAI"),
        ("langchain_anthropic", "LangChain Anthropic"),
        ("dotenv", "Python-dotenv"),
    ]

    for module, name in modules:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError as e:
            print(f"[FAIL] {name}: {e}")
            return False
    return True


def test_project_modules():
    """Test that project modules can be imported."""
    print("\nTesting project modules...")

    modules = [
        ("config.llm_config", "get_llm"),
        ("utils.code_executor", "create_code_executor"),
        ("agents.agents_config", "create_all_agents"),
        ("agents.crew_workflow", "create_tasks"),
    ]

    for module, attr in modules:
        try:
            mod = __import__(module, fromlist=[attr])
            getattr(mod, attr)
            print(f"[OK] {module}")
        except Exception as e:
            print(f"[FAIL] {module}: {e}")
            return False
    return True


def test_env_file():
    """Check if .env file and API key are configured."""
    print("\nChecking environment...")

    from dotenv import load_dotenv
    load_dotenv()

    if not Path(".env").exists():
        print("[WARN] .env file not found")
        return False

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key.startswith("sk-ant-"):
        print("[OK] ANTHROPIC_API_KEY configured")
        return True

    print("[WARN] ANTHROPIC_API_KEY not found or invalid")
    return False


def main():
    """Run all setup tests."""
    print("=" * 50)
    print("CrewAI Data Scientists - Setup Test")
    print("=" * 50)

    all_passed = test_imports() and test_project_modules() and test_env_file()

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] Ready to run: python app.py")
    else:
        print("[ERROR] Fix issues above before running the app")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
