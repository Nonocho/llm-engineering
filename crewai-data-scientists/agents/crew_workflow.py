"""Crew workflow orchestration for the data science pipeline."""

from typing import Any, Dict

import pandas as pd
from crewai import Crew, Process, Task


def create_tasks(agents: dict) -> list:
    """Create the three main tasks for the data science workflow."""

    planning_task = Task(
        description=(
            "Create a plan for regression predicting the target variable.\n"
            "Data is available in global DataFrame 'shared_df'.\n"
            "Outline steps for agents to:\n"
            "  a. Inspect 'shared_df' (shape, info, nulls, describe)\n"
            "  b. Preprocess (handle Date, drop identifiers, OneHotEncode, create train/test split)\n"
            "  c. Train RandomForestRegressor (random_state=42)\n"
            "  d. Evaluate (MAE, MSE, RMSE, R2)\n"
            "  e. Extract top 10 feature importances\n"
            "Remind agents to use 'Code Executor' tool."
        ),
        expected_output="Numbered plan outlining data science goals and tool usage instructions.",
        agent=agents["planner"],
    )

    data_analysis_task = Task(
        description=(
            "Inspect and prepare 'shared_df' DataFrame.\n"
            "Generate Python code to:\n"
            "1. Inspect (shape, info(), isnull().sum(), describe())\n"
            "2. Convert 'Date' to datetime, sort, then drop 'Date'\n"
            "3. Drop identifier columns (like 'Product Name')\n"
            "4. One-hot encode categorical columns (pd.get_dummies, drop_first=True)\n"
            "5. Create global 'y' from target column, 'X' from remaining columns\n"
            "6. Create X_train, X_test, y_train, y_test (80/20 split, shuffle=False)\n"
            "Execute with 'Code Executor' tool. Include print statements for verification."
        ),
        expected_output="Successful code execution output showing data inspection and variable creation.",
        agent=agents["analyst"],
    )

    modeling_task = Task(
        description=(
            "Train and evaluate a regression model.\n"
            "Generate Python code assuming X_train, X_test, y_train, y_test exist.\n"
            "1. Train RandomForestRegressor(random_state=42), store as 'trained_model'\n"
            "2. Predict on X_test\n"
            "3. Calculate and print MAE, MSE, RMSE, R2 metrics\n"
            "4. Print top 10 feature importances\n"
            "Execute with 'Code Executor' tool.\n"
            "Include the Python code in a markdown block in your final response."
        ),
        expected_output="Code execution output with metrics and feature importances, plus markdown code block.",
        agent=agents["modeler"],
    )

    return [planning_task, data_analysis_task, modeling_task]


def create_crew(agents: dict, tasks: list) -> Crew:
    """Create the CrewAI data science team."""
    return Crew(
        agents=[agents["planner"], agents["analyst"], agents["modeler"]],
        tasks=tasks,
        process=Process.sequential,
        verbose=1,
        output_log_file="crew_output.log",
    )


def run_data_science_workflow(
    crew: Crew,
    data_path: str = None,
    dataframe: pd.DataFrame = None,
    target_column: str = "Units Sold",
) -> Dict[str, Any]:
    """Execute the complete data science workflow."""

    shared_namespace = {"pd": pd}

    if dataframe is not None:
        shared_namespace["shared_df"] = dataframe.copy()
    elif data_path:
        shared_namespace["shared_df"] = pd.read_csv(data_path)
    else:
        raise ValueError("Either data_path or dataframe must be provided")

    shared_namespace["target_column"] = target_column

    print(f"Starting workflow... Dataset: {shared_namespace['shared_df'].shape}, Target: {target_column}")

    crew_result = crew.kickoff()

    print("Workflow completed!")

    return {"result": crew_result, "shared_namespace": shared_namespace}


def extract_results(shared_namespace: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key results from the shared namespace after workflow completion."""
    results = {
        "data_shape": shared_namespace.get("shared_df", pd.DataFrame()).shape,
        "has_train_test_split": all(
            key in shared_namespace for key in ["X_train", "X_test", "y_train", "y_test"]
        ),
        "has_model": "trained_model" in shared_namespace,
    }

    if results["has_train_test_split"]:
        results["X_train_shape"] = shared_namespace["X_train"].shape
        results["X_test_shape"] = shared_namespace["X_test"].shape

    if results["has_model"]:
        results["model"] = shared_namespace["trained_model"]

    return results
