"""
LangGraph Portfolio Application
A professional Gradio application demonstrating LangGraph agentic patterns.

Author: Arnaud Demes
Based on Dr. Ryan Ahmed's LangGraph course
"""

import os
from dotenv import load_dotenv
import gradio as gr

# Load environment variables
load_dotenv()

# Import agent functions
from agents.travel_agent import run_travel_agent, stream_travel_agent
from agents.router_pattern import run_router
from agents.human_in_loop import submit_trade, approve_trade, reject_trade, get_graph_visualization as get_hitl_graph
from agents.cycles_iteration import run_constraint_checker
from utils.code_display import get_code_snippet

def create_travel_agent_tab():
    """Creates the Travel Planning Agent demo tab."""
    with gr.Column():
        gr.Markdown("""
        # 🌍 AI Travel Planning Agent

        A sophisticated agent that helps plan your trips using real-time data from:
        - **Tavily Search**: Latest news and travel advisories
        - **Amadeus API**: Live flight and hotel pricing
        - **Multi-tool coordination**: Intelligent routing between tools

        ### Try it out:
        Ask me to plan a trip! For example:
        - "Find flights from Toronto to Paris for June 1-7, 2026"
        - "What are the latest travel advisories for Tokyo?"
        - "Search for hotels in New York City for 3 nights starting May 15"
        """)

        with gr.Row():
            with gr.Column(scale=1):
                user_input = gr.Textbox(
                    label="Your Travel Request",
                    placeholder="e.g., Find me flights from YYZ to CDG for June 1-7",
                    lines=3
                )
                submit_btn = gr.Button("Plan My Trip", variant="primary")
                clear_btn = gr.Button("Clear")

            with gr.Column(scale=1):
                output = gr.Textbox(
                    label="Agent Response",
                    lines=15
                )

        with gr.Row():
            graph_viz = gr.Image(label="Agent Workflow Graph")

        with gr.Accordion("📝 View Implementation Code", open=False):
            code_display = gr.Code(
                value=get_code_snippet("travel"),
                language="python",
                label="Agent Code"
            )

        submit_btn.click(
            fn=run_travel_agent,
            inputs=[user_input],
            outputs=[output, graph_viz]
        )
        clear_btn.click(lambda: ("", "", None), outputs=[user_input, output, graph_viz])


def create_router_tab():
    """Creates the Router Pattern demo tab."""
    with gr.Column():
        gr.Markdown("""
        # 🔀 Router Pattern Demo

        Demonstrates conditional routing in LangGraph using an **Investment Analysis Router**.

        The agent analyzes your query and routes to the appropriate analysis:
        - **Equity Analysis**: For stocks and equity investments
        - **Bond Analysis**: For fixed income securities
        - **Alternative Analysis**: For real estate, commodities, crypto, etc.

        ### How it works:
        1. User asks about an asset type
        2. Router node determines the asset category
        3. Request routed to specialized analysis node
        4. Results returned to user
        """)

        with gr.Row():
            with gr.Column(scale=1):
                asset_query = gr.Textbox(
                    label="Ask about an investment",
                    placeholder="e.g., Analyze Microsoft stock",
                    lines=2
                )
                analyze_btn = gr.Button("Analyze", variant="primary")

            with gr.Column(scale=1):
                router_output = gr.Textbox(
                    label="Analysis Result",
                    lines=10
                )

        with gr.Row():
            router_graph = gr.Image(label="Router Workflow")

        with gr.Accordion("📝 View Implementation Code", open=False):
            router_code = gr.Code(
                value=get_code_snippet("router"),
                language="python"
            )

        analyze_btn.click(
            fn=run_router,
            inputs=[asset_query],
            outputs=[router_output, router_graph]
        )


def create_hitl_tab():
    """Creates the Human-in-the-Loop demo tab."""
    with gr.Column():
        gr.Markdown("""
        # 👤 Human-in-the-Loop Pattern

        Demonstrates LangGraph's **interrupt** mechanism for human approval workflows.

        **Scenario**: Trade Approval System
        - Agent analyzes trade parameters
        - Pauses for human approval before execution
        - Resumes with user decision

        ### Workflow:
        1. Submit trade details (ticker, quantity, price)
        2. Agent analyzes and prepares order
        3. **Interrupt**: Waits for your approval
        4. Approve or reject the trade
        5. Agent executes or cancels based on your decision
        """)

        with gr.Row():
            with gr.Column(scale=1):
                ticker = gr.Textbox(label="Ticker Symbol", placeholder="AAPL")
                quantity = gr.Number(label="Quantity", value=100)
                price = gr.Number(label="Limit Price ($)", value=150.00)
                submit_trade_btn = gr.Button("Submit for Approval", variant="primary")

            with gr.Column(scale=1):
                trade_status = gr.Textbox(
                    label="Trade Status",
                    lines=8
                )

        with gr.Row():
            approve_btn = gr.Button("✅ Approve Trade", variant="primary")
            reject_btn = gr.Button("❌ Reject Trade", variant="stop")

        with gr.Row():
            hitl_graph = gr.Image(label="Human-in-the-Loop Workflow")

        with gr.Accordion("📝 View Implementation Code", open=False):
            hitl_code = gr.Code(
                value=get_code_snippet("hitl"),
                language="python"
            )

        # State to store thread_id
        thread_id_state = gr.State(value="")

        def submit_for_approval(tick, qty, px):
            thread_id, result, graph = submit_trade(tick, qty, px, "BUY")
            return result, graph, thread_id

        def approve_trade_wrapper(thread_id):
            return approve_trade(thread_id)

        def reject_trade_wrapper(thread_id):
            return reject_trade(thread_id)

        submit_trade_btn.click(
            fn=submit_for_approval,
            inputs=[ticker, quantity, price],
            outputs=[trade_status, hitl_graph, thread_id_state]
        )
        approve_btn.click(
            fn=approve_trade_wrapper,
            inputs=[thread_id_state],
            outputs=[trade_status]
        )
        reject_btn.click(
            fn=reject_trade_wrapper,
            inputs=[thread_id_state],
            outputs=[trade_status]
        )


def create_cycles_tab():
    """Creates the Cycles/Iteration demo tab."""
    with gr.Column():
        gr.Markdown("""
        # 🔄 Cycles & Iteration Pattern

        Demonstrates LangGraph's ability to handle **cyclic workflows** and iteration.

        **Scenario**: Portfolio Constraint Checker
        - Iteratively checks multiple portfolio constraints
        - Loops until all constraints are satisfied
        - Maximum iterations to prevent infinite loops

        ### Constraints Checked:
        1. **Diversification**: No single position > 25%
        2. **Risk Level**: Overall portfolio risk within limits
        3. **Cash Reserve**: Minimum 5% cash position

        The agent will suggest adjustments if constraints are violated.

        ### 📊 Example Portfolios to Test:

        **Violates position size limit (AAPL at 35%):**
        ```json
        {"AAPL": 0.35, "GOOGL": 0.30, "MSFT": 0.25, "CASH": 0.10}
        ```

        **Violates cash reserve (only 2%):**
        ```json
        {"AAPL": 0.33, "GOOGL": 0.33, "MSFT": 0.32, "CASH": 0.02}
        ```

        **Violates both (oversized position + low cash):**
        ```json
        {"AAPL": 0.40, "GOOGL": 0.30, "TSLA": 0.27, "CASH": 0.03}
        ```

        **Already compliant:**
        ```json
        {"AAPL": 0.24, "GOOGL": 0.24, "MSFT": 0.24, "NVDA": 0.23, "CASH": 0.05}
        ```
        """)

        with gr.Row():
            with gr.Column(scale=1):
                portfolio_input = gr.Textbox(
                    label="Portfolio Holdings (JSON format)",
                    placeholder='{"AAPL": 0.30, "GOOGL": 0.25, "MSFT": 0.20, "CASH": 0.25}',
                    lines=5
                )
                check_btn = gr.Button("Check Constraints", variant="primary")

            with gr.Column(scale=1):
                constraint_output = gr.Textbox(
                    label="Constraint Check Results",
                    lines=12
                )

        with gr.Row():
            cycles_graph = gr.Image(label="Iterative Workflow")

        with gr.Accordion("📝 View Implementation Code", open=False):
            cycles_code = gr.Code(
                value=get_code_snippet("cycles"),
                language="python"
            )

        check_btn.click(
            fn=run_constraint_checker,
            inputs=[portfolio_input],
            outputs=[constraint_output, cycles_graph]
        )


# Build the main Gradio interface
with gr.Blocks(
    title="LangGraph Portfolio - Agentic AI Patterns"
) as demo:

    gr.Markdown("""
    # 🤖 LangGraph Portfolio Application

    **Professional demonstrations of LangGraph agentic patterns**

    Built by **Arnaud Demes** | Based on Dr. Ryan Ahmed's LangGraph Course

    ---

    Explore four practical implementations showcasing LangGraph's core capabilities:
    multi-agent systems, conditional routing, human oversight, and iterative workflows.
    """)

    with gr.Tabs():
        with gr.Tab("🌍 Travel Agent"):
            create_travel_agent_tab()

        with gr.Tab("🔀 Router Pattern"):
            create_router_tab()

        with gr.Tab("👤 Human-in-the-Loop"):
            create_hitl_tab()

        with gr.Tab("🔄 Cycles & Iteration"):
            create_cycles_tab()

    gr.Markdown("""
    ---

    ### 📝 Attribution
    This application demonstrates production-ready LangGraph patterns for educational purposes.
    Built with LangGraph, LangChain, OpenAI, Tavily, and Amadeus APIs.
    """)


if __name__ == "__main__":
    # Launch the app
    demo.launch(
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()
    )
