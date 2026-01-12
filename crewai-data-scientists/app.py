"""CrewAI Data Scientists - Gradio Application."""

import os

import gradio as gr
import pandas as pd
from dotenv import load_dotenv

from agents.agents_config import create_all_agents
from agents.crew_workflow import create_crew, create_tasks, extract_results
from config.llm_config import get_llm
from utils.code_executor import create_code_executor

load_dotenv()

app_state = {
    "crew": None,
    "llm": None,
    "code_executor": None,
    "execution_namespace": {},
    "last_result": None,
}


def initialize_crew():
    """Initialize the CrewAI team if not already initialized."""
    if app_state["crew"] is not None:
        return

    try:
        app_state["llm"] = get_llm()
        app_state["code_executor"] = create_code_executor(namespace=app_state["execution_namespace"])
        agents = create_all_agents(app_state["llm"], app_state["code_executor"])
        tasks = create_tasks(agents)
        app_state["crew"] = create_crew(agents, tasks)
        print("CrewAI team initialized successfully!")
    except ValueError as e:
        raise ValueError(f"Configuration Error: {e}\nPlease ensure .env has a valid ANTHROPIC_API_KEY.")
    except Exception as e:
        raise ValueError(f"Failed to initialize CrewAI team: {e}")


def run_workflow(csv_file, target_column):
    """Execute the data science workflow with uploaded CSV."""
    if csv_file is None:
        return "[WARN] Please upload a CSV file first.", ""

    if not target_column or not target_column.strip():
        return "[WARN] Please enter the target column name.", ""

    try:
        initialize_crew()
        df = pd.read_csv(csv_file.name)

        if target_column not in df.columns:
            return f"[ERROR] Target '{target_column}' not found. Available: {', '.join(df.columns)}", ""

        app_state["execution_namespace"]["shared_df"] = df.copy()
        app_state["execution_namespace"]["target_column"] = target_column
        app_state["code_executor"]._execution_namespace = app_state["execution_namespace"]

        result = app_state["crew"].kickoff()
        app_state["last_result"] = result

        exec_results = extract_results(app_state["execution_namespace"])
        final_output = format_results(result, exec_results)

        success_msg = (
            f"[SUCCESS] Workflow Completed!\n\n"
            f"Model trained: {exec_results.get('has_model', False)}\n"
            f"Train set: {exec_results.get('X_train_shape', 'N/A')}\n"
            f"Test set: {exec_results.get('X_test_shape', 'N/A')}"
        )
        return success_msg, final_output

    except Exception as e:
        return f"[ERROR] Workflow failed: {e}", ""


def format_results(crew_result, exec_results):
    """Format the workflow results for display."""
    output = "# CrewAI Data Science Results\n\n"
    output += f"- **Data Shape**: {exec_results.get('data_shape', 'N/A')}\n"
    output += f"- **Train/Test Split**: {exec_results.get('has_train_test_split', False)}\n"
    output += f"- **Model Trained**: {exec_results.get('has_model', False)}\n"

    if exec_results.get("has_train_test_split"):
        output += f"- **Training Set**: {exec_results.get('X_train_shape', 'N/A')}\n"
        output += f"- **Test Set**: {exec_results.get('X_test_shape', 'N/A')}\n"

    output += "\n## Agent Output\n\n---\n\n"
    output += str(crew_result.raw)
    return output


with gr.Blocks(title="CrewAI Data Scientists", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # CrewAI Data Scientists

    **Automated Machine Learning with AI Agent Teams**

    This app demonstrates CrewAI agents collaborating on the data science pipeline:
    1. **Lead Data Scientist**: Creates ML workflow plan
    2. **Data Analyst**: Inspects, cleans, and prepares data
    3. **ML Engineer**: Trains model and evaluates performance

    ### How to Use:
    1. Upload a CSV file
    2. Specify the target column
    3. Click "Run Workflow"
    """)

    with gr.Row():
        with gr.Column(scale=1):
            csv_upload = gr.File(label="Upload CSV Dataset", file_types=[".csv"], type="filepath")
            target_input = gr.Textbox(label="Target Column Name", placeholder="e.g., Units Sold", value="Units Sold")
            run_button = gr.Button("Run Workflow", variant="primary", size="lg")

        with gr.Column(scale=1):
            status_output = gr.Textbox(label="Execution Status", lines=8, interactive=False)

    with gr.Row():
        results_output = gr.Markdown(label="Detailed Results")

    run_button.click(fn=run_workflow, inputs=[csv_upload, target_input], outputs=[status_output, results_output])

    gr.Markdown("""
    ---
    **Technical Stack**: CrewAI, Claude Sonnet 4.5, Gradio, Pandas, Scikit-learn

    **Note**: The Code Executor runs AI-generated Python code. Use only in trusted environments.
    """)


if __name__ == "__main__":
    print("=" * 50)
    print("CrewAI Data Scientists Application")
    print("=" * 50)
    demo.launch(server_port=7860, share=False, show_error=True)
