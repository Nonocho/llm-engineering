"""
Human-in-the-Loop Pattern Demo
Demonstrates LangGraph's interrupt mechanism for human approval workflows.

Scenario: Trade Approval System
- Agent analyzes trade parameters
- Pauses for human approval before execution
- Resumes with user decision
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import uuid


# ============================================================================
# STATE DEFINITION
# ============================================================================

class TradeState(TypedDict):
    """State for trade approval workflow."""
    ticker: str
    quantity: int
    price: float
    trade_type: str  # "BUY" or "SELL"
    analysis: str
    human_decision: str  # "approved", "rejected", or "pending"
    execution_result: str
    thread_id: str


# ============================================================================
# WORKFLOW NODES
# ============================================================================

def analyze_trade(state: TradeState) -> TradeState:
    """
    Analyzes trade parameters and prepares for human review.

    Args:
        state: Current trade state

    Returns:
        Updated state with trade analysis
    """
    ticker = state["ticker"]
    quantity = state["quantity"]
    price = state["price"]
    trade_type = state.get("trade_type", "BUY")

    # Calculate trade value
    trade_value = quantity * price

    # Generate analysis
    analysis = f"""
📋 **TRADE ANALYSIS COMPLETE**

Trade Details:
- **Action**: {trade_type}
- **Ticker**: {ticker}
- **Quantity**: {quantity:,} shares
- **Limit Price**: ${price:.2f}
- **Total Value**: ${trade_value:,.2f}

Risk Assessment:
- **Market Impact**: {'Low' if trade_value < 100000 else 'Medium' if trade_value < 500000 else 'High'}
- **Liquidity**: Assess current market depth
- **Timing**: Consider market hours and volatility

Pre-Trade Checklist:
✓ Trade parameters validated
✓ Account has sufficient funds/shares
✓ Compliance checks passed
✓ Risk limits verified

**⚠️ AWAITING HUMAN APPROVAL**

Please review the trade details above and approve or reject this order.
"""

    return {
        **state,
        "analysis": analysis,
        "human_decision": "pending"
    }


def human_approval(state: TradeState) -> TradeState:
    """
    Human approval node - this is where the interrupt occurs.

    In a real implementation, this node would pause execution
    and wait for human input via the Gradio UI.

    Args:
        state: Current trade state

    Returns:
        State (unchanged - waiting for human decision)
    """
    # This node is a placeholder for the interrupt point
    # The actual decision is injected when resuming
    return state


def execute_trade(state: TradeState) -> TradeState:
    """
    Executes the trade after human approval.

    Args:
        state: Trade state with human decision

    Returns:
        Updated state with execution result
    """
    decision = state["human_decision"]

    if decision == "approved":
        # Simulate trade execution
        result = f"""
✅ **TRADE EXECUTED SUCCESSFULLY**

Confirmation Details:
- **Order ID**: {uuid.uuid4().hex[:8].upper()}
- **Status**: FILLED
- **Ticker**: {state['ticker']}
- **Action**: {state.get('trade_type', 'BUY')}
- **Quantity**: {state['quantity']:,} shares
- **Fill Price**: ${state['price']:.2f}
- **Total Value**: ${state['quantity'] * state['price']:,.2f}
- **Timestamp**: 2026-01-11 10:30:00 EST

The trade has been successfully executed and recorded in your account.
"""
    else:
        # Trade rejected
        result = f"""
❌ **TRADE REJECTED**

The trade order for {state['quantity']} shares of {state['ticker']} has been rejected per your decision.

No action has been taken. The order has been cancelled.

Reason: User rejected the trade
"""

    return {
        **state,
        "execution_result": result
    }


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def should_execute(state: TradeState) -> Literal["execute", "cancel"]:
    """
    Routes based on human approval decision.

    Args:
        state: Trade state with human_decision

    Returns:
        "execute" if approved, "cancel" if rejected
    """
    decision = state.get("human_decision", "")
    if decision == "approved":
        return "execute"
    elif decision == "rejected":
        return "cancel"
    else:
        # Default to cancel if decision is pending or unknown
        return "cancel"


def create_cancel_node():
    """Returns a function that generates cancellation message."""
    def cancel_trade(state: TradeState) -> TradeState:
        """Handles trade cancellation."""
        result = f"""
❌ **TRADE CANCELLED**

The trade order has been cancelled per your decision.

Order Details (Cancelled):
- Ticker: {state['ticker']}
- Action: {state.get('trade_type', 'BUY')}
- Quantity: {state['quantity']} shares
- Price: ${state['price']:.2f}

No trade was executed. Your account remains unchanged.
"""
        return {
            **state,
            "execution_result": result
        }
    return cancel_trade


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def build_hitl_agent():
    """
    Constructs the human-in-the-loop trade approval workflow.

    Returns:
        Compiled LangGraph application with checkpointer

    Graph Structure:
        Entry: analyze_trade
        ├─ analyze_trade
        ├─ human_approval (INTERRUPT BEFORE THIS)
        │  └─ Conditional routing:
        │     ├─ "execute" → execute_trade → END
        │     └─ "cancel" → cancel_trade → END
    """
    # Build the state graph
    workflow = StateGraph(TradeState)

    # Add nodes
    workflow.add_node("analyze_trade", analyze_trade)
    workflow.add_node("human_approval", human_approval)
    workflow.add_node("execute_trade", execute_trade)
    workflow.add_node("cancel_trade", create_cancel_node())

    # Set entry point
    workflow.set_entry_point("analyze_trade")

    # Flow to human approval
    workflow.add_edge("analyze_trade", "human_approval")

    # Conditional routing after approval
    workflow.add_conditional_edges(
        "human_approval",
        should_execute,
        {
            "execute": "execute_trade",
            "cancel": "cancel_trade"
        }
    )

    # Both paths end
    workflow.add_edge("execute_trade", END)
    workflow.add_edge("cancel_trade", END)

    # Compile with checkpointer for state persistence
    # NOTE: interrupt_before is commented out for demo purposes
    # In production, uncomment the line below
    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory,
        # interrupt_before=["human_approval"]  # Uncomment for real interrupts
    )


# ============================================================================
# EXECUTION HELPERS
# ============================================================================

# Global state storage for demo (in production, use proper session management)
_pending_trades = {}


def submit_trade(ticker: str, quantity: int, price: float, trade_type: str = "BUY") -> tuple[str, str, object]:
    """
    Submits a trade for human approval.

    Args:
        ticker: Stock ticker symbol
        quantity: Number of shares
        price: Limit price per share
        trade_type: "BUY" or "SELL"

    Returns:
        Tuple of (thread_id, analysis_result, graph_visualization)
    """
    try:
        # Build the agent
        app = build_hitl_agent()

        # Generate unique thread ID
        thread_id = str(uuid.uuid4())

        # Create initial state (only run analyze_trade)
        initial_state = {
            "ticker": ticker.upper(),
            "quantity": int(quantity),
            "price": float(price),
            "trade_type": trade_type.upper(),
            "analysis": "",
            "human_decision": "pending",
            "execution_result": "",
            "thread_id": thread_id
        }

        # Only run analyze_trade step (not the full workflow)
        # We'll manually call just the analyze function
        analyzed_state = analyze_trade(initial_state)

        # Store the analyzed state (before human decision)
        _pending_trades[thread_id] = (app, analyzed_state, {"configurable": {"thread_id": thread_id}})

        # Generate graph visualization
        from utils.graph_viz import visualize_graph
        graph_image = visualize_graph(app)

        return thread_id, analyzed_state["analysis"], graph_image

    except Exception as e:
        error_msg = f"Error submitting trade: {str(e)}"
        return "", error_msg, None


def approve_trade(thread_id: str) -> str:
    """
    Approves a pending trade and executes it.

    Args:
        thread_id: Thread ID from submit_trade

    Returns:
        Execution result message
    """
    if thread_id not in _pending_trades:
        return "❌ No pending trade found. Please submit a trade first."

    try:
        app, state, config = _pending_trades[thread_id]

        # Update state with approval
        state["human_decision"] = "approved"

        # Execute the trade directly
        final_state = execute_trade(state)

        # Clean up
        del _pending_trades[thread_id]

        return final_state["execution_result"]

    except Exception as e:
        return f"❌ Error approving trade: {str(e)}"


def reject_trade(thread_id: str) -> str:
    """
    Rejects a pending trade.

    Args:
        thread_id: Thread ID from submit_trade

    Returns:
        Cancellation message
    """
    if thread_id not in _pending_trades:
        return "❌ No pending trade found. Please submit a trade first."

    try:
        app, state, config = _pending_trades[thread_id]

        # Update state with rejection
        state["human_decision"] = "rejected"

        # Cancel the trade directly
        cancel_node = create_cancel_node()
        final_state = cancel_node(state)

        # Clean up
        del _pending_trades[thread_id]

        return final_state["execution_result"]

    except Exception as e:
        return f"❌ Error rejecting trade: {str(e)}"


def get_graph_visualization():
    """Returns the workflow graph visualization."""
    try:
        app = build_hitl_agent()
        from utils.graph_viz import visualize_graph
        return visualize_graph(app)
    except Exception as e:
        print(f"Error generating graph: {e}")
        return None
