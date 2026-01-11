"""
Code Snippet Display Utilities
Provides formatted code snippets for educational purposes.
"""


def get_travel_agent_code() -> str:
    """Returns the Travel Agent implementation code for display."""
    return '''# Travel Agent Implementation
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """State for travel planning agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]

def build_travel_agent():
    """Constructs the travel agent workflow."""
    # Define tools
    tools = [
        tavily_search_tool,      # Web search
        search_flights_tool,     # Flight search
        search_hotels_tool,      # Hotel search
        get_current_date_tool    # Date utility
    ]

    # Create tool node
    tool_node = ToolNode(tools)

    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model_with_tools)
    workflow.add_node("action", tool_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional routing
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"action": "action", END: END}
    )

    # Loop back from tools to agent
    workflow.add_edge("action", "agent")

    return workflow.compile()
'''


def get_router_code() -> str:
    """Returns the Router Pattern implementation code."""
    return '''# Router Pattern Implementation
from typing import Literal

def route_to_analysis(state: AgentState) -> str:
    """
    Routes to appropriate analysis based on asset type.

    Returns:
        "equity", "bond", or "alternative"
    """
    user_input = state["user_input"].lower()

    if any(word in user_input for word in ["stock", "equity", "share"]):
        return "equity"
    elif any(word in user_input for word in ["bond", "fixed income", "treasury"]):
        return "bond"
    else:
        return "alternative"

# Build workflow with conditional routing
workflow = StateGraph(InvestmentState)

workflow.add_node("router", route_to_analysis)
workflow.add_node("equity_analysis", analyze_equity)
workflow.add_node("bond_analysis", analyze_bond)
workflow.add_node("alternative_analysis", analyze_alternative)

workflow.set_entry_point("router")

# Conditional edges based on router decision
workflow.add_conditional_edges(
    "router",
    route_to_analysis,
    {
        "equity": "equity_analysis",
        "bond": "bond_analysis",
        "alternative": "alternative_analysis"
    }
)

# All analysis paths end
workflow.add_edge("equity_analysis", END)
workflow.add_edge("bond_analysis", END)
workflow.add_edge("alternative_analysis", END)
'''


def get_hitl_code() -> str:
    """Returns the Human-in-the-Loop implementation code."""
    return '''# Human-in-the-Loop Implementation
from langgraph.checkpoint.memory import MemorySaver

# Compile with checkpointer for interrupts
memory = MemorySaver()
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_approval"]  # Pause before this node
)

# Initial invocation - runs until interrupt
config = {"configurable": {"thread_id": "trade_123"}}
initial_state = {
    "ticker": "AAPL",
    "quantity": 100,
    "price": 150.00
}

# Agent prepares trade, then pauses
result = app.invoke(initial_state, config)

# ... Human reviews and decides ...

# Resume with human decision
updated_state = {
    **result,
    "human_decision": "approved"  # or "rejected"
}

# Continue execution with approval
final_result = app.invoke(updated_state, config)
'''


def get_cycles_code() -> str:
    """Returns the Cycles/Iteration implementation code."""
    return '''# Cycles & Iteration Implementation

def check_constraints(state: PortfolioState) -> PortfolioState:
    """Checks portfolio constraints iteratively."""
    violations = []

    # Check diversification
    for position, weight in state["holdings"].items():
        if weight > 0.25:
            violations.append(f"{position} exceeds 25% limit")

    # Check cash reserve
    if state["holdings"].get("CASH", 0) < 0.05:
        violations.append("Cash reserve below 5%")

    return {
        **state,
        "violations": violations,
        "iteration_count": state["iteration_count"] + 1
    }

def should_continue_checking(state: PortfolioState) -> str:
    """Decides whether to continue iterating."""
    max_iterations = 5

    if state["iteration_count"] >= max_iterations:
        return "max_iterations"

    if len(state["violations"]) == 0:
        return "constraints_met"

    return "adjust_portfolio"

# Build iterative workflow
workflow.add_conditional_edges(
    "check_constraints",
    should_continue_checking,
    {
        "adjust_portfolio": "adjust_holdings",
        "constraints_met": END,
        "max_iterations": END
    }
)

# Create loop
workflow.add_edge("adjust_holdings", "check_constraints")
'''


def get_code_snippet(agent_name: str) -> str:
    """
    Returns formatted code snippet for the specified agent.

    Args:
        agent_name: One of "travel", "router", "hitl", "cycles"

    Returns:
        Python code string for display in Gradio Code component

    Example:
        >>> code = get_code_snippet("router")
        >>> gr.Code(value=code, language="python")
    """
    snippets = {
        "travel": get_travel_agent_code(),
        "router": get_router_code(),
        "hitl": get_hitl_code(),
        "cycles": get_cycles_code()
    }

    return snippets.get(agent_name, "# Code snippet not available")
