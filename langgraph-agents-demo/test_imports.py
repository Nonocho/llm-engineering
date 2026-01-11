"""
Quick test script to verify all imports work correctly.
Run with: python test_imports.py
"""

print("Testing imports...")

try:
    print("✓ Importing os and dotenv...")
    import os
    from dotenv import load_dotenv
    load_dotenv()

    print("✓ Importing gradio...")
    import gradio as gr

    print("✓ Importing agents...")
    from agents.travel_agent import run_travel_agent
    from agents.router_pattern import run_router
    from agents.human_in_loop import submit_trade, approve_trade, reject_trade
    from agents.cycles_iteration import run_constraint_checker

    print("✓ Importing utilities...")
    from utils.code_display import get_code_snippet
    from utils.graph_viz import visualize_graph

    print("\n✅ All imports successful!")
    print("\nChecking environment variables...")

    required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY", "AMADEUS_CLIENT_ID", "AMADEUS_CLIENT_SECRET"]
    missing_keys = []

    for key in required_keys:
        if os.getenv(key):
            print(f"✓ {key} is set")
        else:
            print(f"✗ {key} is MISSING")
            missing_keys.append(key)

    if missing_keys:
        print(f"\n⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please add them to your .env file")
    else:
        print("\n✅ All required API keys are configured!")

    print("\n🎉 Setup complete! Ready to run: python app.py")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nPlease run: pip install -r requirements.txt")
except Exception as e:
    print(f"\n❌ Error: {e}")
