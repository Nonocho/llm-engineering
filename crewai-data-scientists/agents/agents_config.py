"""Agent configuration for the data science CrewAI team."""

from typing import List

from crewai import Agent
from crewai.tools import BaseTool


def create_planner_agent(llm) -> Agent:
    """Create the Lead Data Scientist and Planner agent."""
    return Agent(
        role="Lead Data Scientist and Planner",
        goal=(
            "Analyze the objective (predict target variable) with data in 'shared_df'. "
            "Create a step-by-step regression analysis plan. "
            "Instruct agents to use the 'Code Executor' tool to write and execute Python code."
        ),
        backstory=(
            "Experienced lead data scientist with 10+ years in ML projects. "
            "Expert at breaking down complex workflows into clear, actionable steps."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )


def create_analyst_preprocessor_agent(llm, tools: List[BaseTool]) -> Agent:
    """Create the Data Analysis and Preprocessing Expert agent."""
    return Agent(
        role="Data Analysis and Preprocessing Expert",
        goal=(
            "Follow the plan for data analysis and preprocessing. "
            "Write Python code using pandas and scikit-learn to: "
            "1) Inspect 'shared_df' (shape, info, nulls, describe), "
            "2) Handle dates and drop identifier columns, "
            "3) One-hot encode categorical columns (updating 'shared_df'), "
            "4) Create global X, y variables and train/test split (80/20, shuffle=False). "
            "Use the 'Code Executor' tool to run your code."
        ),
        backstory=(
            "Meticulous data analyst skilled in pandas and scikit-learn. "
            "Always inspects data first, then transforms systematically."
        ),
        llm=llm,
        tools=tools,
        allow_delegation=False,
        verbose=True,
    )


def create_modeler_evaluator_agent(llm, tools: List[BaseTool]) -> Agent:
    """Create the Machine Learning Modeler and Evaluator agent."""
    return Agent(
        role="Machine Learning Modeler and Evaluator",
        goal=(
            "Follow the plan for modeling and evaluation. "
            "Write Python code using scikit-learn to: "
            "1) Train RandomForestRegressor(random_state=42) with X_train, y_train, "
            "2) Predict on X_test, "
            "3) Calculate and print MAE, MSE, RMSE, R2 metrics, "
            "4) Print top 10 feature importances. "
            "Use the 'Code Executor' tool and include your code in a markdown block."
        ),
        backstory=(
            "ML engineer specializing in regression with deep scikit-learn expertise. "
            "Writes production-quality code with proper imports and error handling."
        ),
        llm=llm,
        tools=tools,
        allow_delegation=False,
        verbose=True,
    )


def create_all_agents(llm, code_executor_tool: BaseTool) -> dict:
    """Create all three agents for the data science workflow."""
    return {
        "planner": create_planner_agent(llm),
        "analyst": create_analyst_preprocessor_agent(llm, [code_executor_tool]),
        "modeler": create_modeler_evaluator_agent(llm, [code_executor_tool]),
    }
