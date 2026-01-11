# 🚀 Quick Start Guide

Get the LangGraph Portfolio Application running in 5 minutes!

## Step 1: Verify Your Setup

You already have a virtual environment set up. Let's make sure everything is configured:

### Check Python Installation

```bash
# Activate your virtual environment
# On Windows (Git Bash):
source venv/Scripts/activate

# OR on Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# OR on Windows (CMD):
venv\Scripts\activate.bat
```

### Install Missing Dependencies (if any)

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Keys

Your `.env` file is already set up with API keys. Verify they're correct:

```bash
# Open .env file and check:
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
AMADEUS_CLIENT_ID=...
AMADEUS_CLIENT_SECRET=...
```

## Step 3: Test Your Setup

Run the import test to verify everything works:

```bash
python test_imports.py
```

You should see:
```
✅ All imports successful!
✅ All required API keys are configured!
🎉 Setup complete!
```

## Step 4: Launch the Application

```bash
python app.py
```

The app will start at: **http://localhost:7860**

## Step 5: Try the Demos

### 🌍 Tab 1: Travel Agent
Try asking:
```
Find me flights from Toronto to Paris for June 1-7, 2026
```

### 🔀 Tab 2: Router Pattern
Try asking:
```
Analyze Microsoft stock
```

### 👤 Tab 3: Human-in-the-Loop
1. Enter: `AAPL`, `100`, `150.00`
2. Click "Submit for Approval"
3. Review and click "Approve" or "Reject"

### 🔄 Tab 4: Cycles & Iteration
Enter this portfolio:
```json
{"AAPL": 0.35, "GOOGL": 0.30, "MSFT": 0.25, "CASH": 0.10}
```

Click "Check Constraints" to see automatic rebalancing!

---

## Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Missing API Keys
```bash
# Copy example and edit
cp .env.example .env
# Then edit .env with your actual keys
```

### Port Already in Use
```bash
# Change port in app.py (line near the end):
demo.launch(server_port=7861)  # Change from 7860
```

### Graph Visualization Not Working
The graphs require the `mermaid` backend. If you see errors:
```bash
pip install pygraphviz  # May require additional system dependencies
```

---

## Next Steps

- ✅ Explore all 4 tabs
- ✅ View the code snippets in each tab
- ✅ Check the graph visualizations
- ✅ Review the [README.md](README.md) for architecture details
- ✅ Explore the agent code in `agents/` directory

---

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [PROJECT.md](PROJECT.md) for project specifications
- See [SKILL.md](SKILL.md) for best practices

**Enjoy exploring LangGraph! 🤖**
