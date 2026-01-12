# 🤖 CrewAI Data Scientists

**Automated Machine Learning with AI Agent Teams**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.86.0-green.svg)](https://docs.crewai.com/)
[![Gradio](https://img.shields.io/badge/Gradio-4.44.0-orange.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A professional Gradio application demonstrating **CrewAI agents** collaborating to automate end-to-end data science workflows. Built as a portfolio piece showcasing AI engineering capabilities and multi-agent orchestration.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [The Agent Team](#the-agent-team)
- [Technologies](#technologies)
- [Credits](#credits)
- [License](#license)

---

## 🎯 Overview

This application demonstrates how **three specialized AI agents** can work together to perform a complete machine learning workflow:

1. **📋 Lead Data Scientist**: Creates strategic ML plans
2. **🔍 Data Analyst**: Cleans and prepares data
3. **🎯 ML Engineer**: Trains models and evaluates performance

The agents use a **Code Executor tool** to write and run Python code, performing all steps from data inspection to model evaluation automatically.

### Screenshots

![App Interface](crewai_image1.png)
*Clean Gradio interface for uploading data and running workflows*

![Workflow Results](crewai_image2.png)
*Real-time agent execution and results display*

![Agent Output](crewai_image3.png)
*Detailed metrics and generated code from agents*

### What Gets Automated

- Data inspection and quality checks
- Date handling and preprocessing
- Categorical encoding (one-hot encoding)
- Train/test splitting (80/20)
- RandomForestRegressor training
- Metric calculation (MAE, MSE, RMSE, R²)
- Feature importance analysis

---

## ✨ Features

### 🤖 Multi-Agent Collaboration
- **Three specialized agents** working in sequence
- **Code generation** and execution by AI agents
- **Shared state management** between agents
- **Sequential workflow** with context passing

### 📊 Complete ML Pipeline
- **Automated preprocessing**: Handles dates, identifiers, categoricals
- **Model training**: RandomForestRegressor with best practices
- **Performance evaluation**: Full regression metrics suite
- **Feature importance**: Top 10 most important features

### 🎨 Professional Interface
- **Clean Gradio UI** inspired by langgraph-agents-demo
- **Real-time status updates** during execution
- **Formatted results** with metrics and generated code
- **Example dataset** included for testing

### 🏗️ Production-Ready Structure
- **Modular design**: Agents, config, and utils separated
- **Type hints** and documentation throughout
- **Error handling** and validation
- **Extensible architecture** for adding more agents

---

## 🏗️ Architecture

```
crewai-data-scientists/
├── app.py                          # Main Gradio application
├── agents/                         # Agent definitions
│   ├── __init__.py
│   ├── agents_config.py            # Agent roles and prompts
│   └── crew_workflow.py            # Task definitions and orchestration
├── config/                         # Configuration
│   ├── __init__.py
│   └── llm_config.py              # LLM setup (Claude Sonnet 4.5)
├── utils/                          # Utility modules
│   ├── __init__.py
│   └── code_executor.py           # Code execution tool
├── data/                           # Dataset storage
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .env                            # Your API keys (not in git)
├── PROJECT.md                      # Detailed project documentation
└── README.md                       # This file
```

### Workflow Diagram

```
User Uploads CSV
    ↓
[Lead Data Scientist]
    ↓
Creates ML Plan
    ↓
[Data Analyst & Preprocessor]
    ↓
Generates & Executes Preprocessing Code
    ↓
Data Cleaned & Split (X_train, X_test, y_train, y_test)
    ↓
[ML Modeler & Evaluator]
    ↓
Generates & Executes Training Code
    ↓
Model Trained & Evaluated
    ↓
Results Displayed (Metrics + Code)
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** (Recommended: 3.10 or 3.11)
- **pip** package manager
- **Virtual environment** (recommended)
- **Anthropic API key** (for Claude Sonnet 4.5)

### Step 1: Clone or Download

```bash
cd crewai-data-scientists
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Step 5: Get Your API Key

Sign up for an Anthropic API key:
- Visit: [console.anthropic.com](https://console.anthropic.com/)
- Create an account (free credits available)
- Generate an API key
- Add it to your `.env` file

---

## 💻 Usage

### Running the Application

```bash
python app.py
```

The app will launch at: **http://localhost:7860**

### Using the Interface

1. **Upload CSV**: Click the file upload button and select your dataset
2. **Specify Target**: Enter the name of your target variable column
3. **Run Workflow**: Click the "Run Workflow" button
4. **Watch Agents Work**: See real-time updates as agents execute
5. **Review Results**: Examine metrics, code, and insights

### Example Dataset

The project includes `Supplement_Sales_Weekly.csv`:
- **Target**: `Units Sold`
- **Features**: Date, Platform, Product attributes
- **Task**: Predict weekly supplement sales

### Example Queries

Try the workflow with:
- **Supplement Sales** (included): Target = `Units Sold`
- **Your own data**: Any regression dataset with numeric/categorical features

---

## 📁 Project Structure

### Core Modules

#### [app.py](app.py) - Main Application
- Gradio interface with clean layout
- Workflow orchestration
- Results formatting and display

#### [config/llm_config.py](config/llm_config.py) - LLM Configuration
- Claude Sonnet 4.5 initialization
- Temperature and token settings
- API key validation

#### [utils/code_executor.py](utils/code_executor.py) - Code Execution Tool
- Custom CrewAI tool for running Python code
- Shared namespace management
- Library installation support
- Stdout capture and error handling

#### [agents/agents_config.py](agents/agents_config.py) - Agent Definitions
- Three specialized agents with distinct roles
- Detailed goals and backstories
- Tool assignments

#### [agents/crew_workflow.py](agents/crew_workflow.py) - Workflow Orchestration
- Task definitions with clear objectives
- Sequential process configuration
- Result extraction utilities

---

## 🤖 The Agent Team

### 1. Lead Data Scientist and Planner

**Role**: Strategic planning and workflow design

**Responsibilities**:
- Analyze the ML objective
- Create step-by-step plan
- Instruct other agents on their goals

**Tools**: None (planning only)

**Output**: Numbered plan with clear objectives

---

### 2. Data Analysis and Preprocessing Expert

**Role**: Data inspection, cleaning, and preparation

**Responsibilities**:
- Inspect data (shape, info, nulls, describe)
- Convert dates to datetime
- Drop identifier columns
- One-hot encode categorical features
- Create train/test splits (80/20)

**Tools**: Code Executor (writes and runs pandas/sklearn code)

**Output**: Clean data with global variables (X_train, X_test, y_train, y_test)

---

### 3. Machine Learning Modeler and Evaluator

**Role**: Model training and performance evaluation

**Responsibilities**:
- Train RandomForestRegressor (random_state=42)
- Make predictions on test set
- Calculate regression metrics (MAE, MSE, RMSE, R²)
- Extract top 10 feature importances

**Tools**: Code Executor (writes and runs sklearn code)

**Output**: Model metrics, feature importances, and generated code

---

## 🛠️ Technologies

### Core Frameworks
- **CrewAI** `0.86.0` - Multi-agent orchestration
- **LangChain** `0.3.7` - LLM integrations
- **Gradio** `4.44.0` - Web interface

### AI & APIs
- **Anthropic API** - Claude Sonnet 4.5 for reasoning
- **LangChain-Anthropic** - Integration layer

### Data Science
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-learn** - Machine learning

### Utilities
- **python-dotenv** - Environment management

---

## 🎓 Credits

- **Built by**: Arnaud Demes
- **Based on**: Dr. Ryan Ahmed's [LLM Engineering Course](https://www.udemy.com/course/)
- **Inspired by**: Professional structure from langgraph-agents-demo
- **Powered by**: [CrewAI](https://docs.crewai.com/) and [Anthropic](https://www.anthropic.com/)

---

## 📊 Success Metrics

This project demonstrates:

✅ **CrewAI Mastery**: Multi-agent collaboration and tool usage
✅ **Code Quality**: Clean, modular, well-documented
✅ **ML Automation**: Complete end-to-end pipeline
✅ **User Experience**: Intuitive interface and clear outputs
✅ **Portfolio Value**: Showcases AI engineering competence

---

## 🔒 Security Considerations

**⚠️ Important**: The Code Executor tool runs AI-generated Python code.

- Only use with **trusted datasets**
- Only run in **secure environments**
- Review generated code before production use
- API keys are kept in `.env` (not committed to git)

---

## 🔮 Future Enhancements

- [ ] Add support for classification tasks
- [ ] Implement multiple model comparison (XGBoost, LinearRegression)
- [ ] Add data visualization agent
- [ ] Support hyperparameter tuning
- [ ] Add model persistence and export
- [ ] Create Docker container
- [ ] Deploy to Hugging Face Spaces

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

**Arnaud Demes**
- LinkedIn: [arnaud-demes-19101990a](https://www.linkedin.com/in/arnaud-demes-19101990a/)
- GitHub: [@Nonocho](https://github.com/Nonocho/)

---

## 📚 Learning Resources

- **CrewAI Documentation**: https://docs.crewai.com/
- **LangChain Guide**: https://python.langchain.com/
- **Anthropic API**: https://docs.anthropic.com/
- **Dr. Ryan Ahmed**: [LinkedIn](https://www.linkedin.com/in/dr-ryan-ahmed)

---

## ⭐ Star History

If you find this project helpful, please consider giving it a star!

---

**Built with ❤️ using CrewAI, LangChain, and Gradio**
