"""
Cycles & Iteration Pattern Demo
Demonstrates LangGraph's ability to handle cyclic workflows and iteration.

Scenario: Portfolio Constraint Checker
- Iteratively checks multiple portfolio constraints
- Loops until all constraints are satisfied or max iterations reached
- Suggests adjustments for violated constraints
"""

import json
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ============================================================================
# STATE DEFINITION
# ============================================================================

class PortfolioState(TypedDict):
    """State for portfolio constraint checking."""
    holdings: dict  # {ticker: weight} e.g., {"AAPL": 0.30, "CASH": 0.20}
    violations: list  # List of constraint violations
    iteration_count: int
    adjustments_made: list  # History of adjustments
    status: str  # "checking", "adjusting", "satisfied", "max_iterations"


# ============================================================================
# CONSTRAINT RULES
# ============================================================================

MAX_POSITION_SIZE = 0.25  # No single position > 25%
MIN_CASH_RESERVE = 0.05   # Minimum 5% cash
MAX_ITERATIONS = 5        # Prevent infinite loops


# ============================================================================
# WORKFLOW NODES
# ============================================================================

def check_constraints(state: PortfolioState) -> PortfolioState:
    """
    Checks portfolio against all defined constraints.

    Args:
        state: Current portfolio state

    Returns:
        Updated state with violation list

    Constraints Checked:
        1. Diversification: No single position > 25%
        2. Cash Reserve: Minimum 5% in cash
        3. Sum to 100%: All weights sum to 1.0
    """
    holdings = state["holdings"]
    violations = []

    # Check 1: Position size limits
    for ticker, weight in holdings.items():
        if ticker != "CASH" and weight > MAX_POSITION_SIZE:
            violations.append({
                "type": "position_size",
                "ticker": ticker,
                "current": weight,
                "limit": MAX_POSITION_SIZE,
                "message": f"{ticker} position ({weight:.1%}) exceeds maximum allowed ({MAX_POSITION_SIZE:.1%})"
            })

    # Check 2: Cash reserve
    cash_position = holdings.get("CASH", 0)
    if cash_position < MIN_CASH_RESERVE:
        violations.append({
            "type": "cash_reserve",
            "current": cash_position,
            "required": MIN_CASH_RESERVE,
            "message": f"Cash reserve ({cash_position:.1%}) below minimum required ({MIN_CASH_RESERVE:.1%})"
        })

    # Check 3: Sum to 100%
    total_weight = sum(holdings.values())
    if abs(total_weight - 1.0) > 0.01:  # Allow 1% tolerance
        violations.append({
            "type": "sum_constraint",
            "current": total_weight,
            "required": 1.0,
            "message": f"Portfolio weights sum to {total_weight:.1%} instead of 100%"
        })

    # Update iteration count
    new_iteration = state["iteration_count"] + 1

    return {
        **state,
        "violations": violations,
        "iteration_count": new_iteration,
        "status": "checking"
    }


def adjust_portfolio(state: PortfolioState) -> PortfolioState:
    """
    Automatically adjusts portfolio to fix constraint violations.

    Args:
        state: Portfolio state with violations

    Returns:
        Updated state with adjusted holdings

    Adjustment Strategy:
        1. For oversized positions: Scale down to limit
        2. For low cash: Proportionally reduce other positions
        3. Rebalance to sum to 100%
    """
    holdings = state["holdings"].copy()
    violations = state["violations"]
    adjustments = []

    # Fix oversized positions first
    for violation in violations:
        if violation["type"] == "position_size":
            ticker = violation["ticker"]
            old_weight = holdings[ticker]
            new_weight = MAX_POSITION_SIZE
            holdings[ticker] = new_weight
            adjustments.append(f"Reduced {ticker} from {old_weight:.1%} to {new_weight:.1%}")

    # Fix cash reserve
    cash_violations = [v for v in violations if v["type"] == "cash_reserve"]
    if cash_violations:
        current_cash = holdings.get("CASH", 0)
        needed_cash = MIN_CASH_RESERVE - current_cash

        # Scale down non-cash positions proportionally
        non_cash_total = sum(v for k, v in holdings.items() if k != "CASH")

        if non_cash_total > 0:
            scale_factor = (non_cash_total - needed_cash) / non_cash_total

            for ticker in holdings:
                if ticker != "CASH":
                    old_weight = holdings[ticker]
                    holdings[ticker] = old_weight * scale_factor

            holdings["CASH"] = holdings.get("CASH", 0) + needed_cash
            adjustments.append(f"Increased cash reserve to {MIN_CASH_RESERVE:.1%}")

    # Normalize to sum to 100%
    total = sum(holdings.values())
    if abs(total - 1.0) > 0.01:
        for ticker in holdings:
            holdings[ticker] = holdings[ticker] / total
        adjustments.append("Normalized portfolio to 100%")

    return {
        **state,
        "holdings": holdings,
        "adjustments_made": state["adjustments_made"] + adjustments,
        "status": "adjusting"
    }


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def should_continue_iteration(state: PortfolioState) -> Literal["adjust", "satisfied", "max_iterations"]:
    """
    Determines next step in the iteration cycle.

    Args:
        state: Current portfolio state

    Returns:
        - "adjust": Violations found, adjust portfolio
        - "satisfied": All constraints met, end workflow
        - "max_iterations": Hit iteration limit, end workflow

    Decision Logic:
        1. Check if max iterations reached
        2. Check if constraints are satisfied
        3. Otherwise, continue adjusting
    """
    # Check iteration limit
    if state["iteration_count"] >= MAX_ITERATIONS:
        return "max_iterations"

    # Check if all constraints satisfied
    if len(state["violations"]) == 0:
        return "satisfied"

    # Continue adjusting
    return "adjust"


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def build_cycles_agent():
    """
    Constructs the iterative portfolio constraint checker.

    Returns:
        Compiled LangGraph application

    Graph Structure:
        Entry: check_constraints
        ├─ check_constraints
        │  └─ Conditional routing:
        │     ├─ "adjust" → adjust_portfolio → check_constraints (CYCLE)
        │     ├─ "satisfied" → END
        │     └─ "max_iterations" → END
    """
    # Build the state graph
    workflow = StateGraph(PortfolioState)

    # Add nodes
    workflow.add_node("check_constraints", check_constraints)
    workflow.add_node("adjust_portfolio", adjust_portfolio)

    # Set entry point
    workflow.set_entry_point("check_constraints")

    # Add conditional routing
    workflow.add_conditional_edges(
        "check_constraints",
        should_continue_iteration,
        {
            "adjust": "adjust_portfolio",
            "satisfied": END,
            "max_iterations": END
        }
    )

    # Create the cycle: adjust → check
    workflow.add_edge("adjust_portfolio", "check_constraints")

    # Compile and return
    return workflow.compile()


# ============================================================================
# EXECUTION HELPER
# ============================================================================

def run_constraint_checker(portfolio_json: str) -> tuple[str, object]:
    """
    Executes the portfolio constraint checker.

    Args:
        portfolio_json: JSON string of portfolio holdings
                       e.g., '{"AAPL": 0.30, "GOOGL": 0.25, "MSFT": 0.20, "CASH": 0.25}'

    Returns:
        Tuple of (result_text, graph_visualization)

    Example:
        >>> result, graph = run_constraint_checker('{"AAPL": 0.50, "CASH": 0.50}')
        >>> # Will identify sum constraint violation
    """
    try:
        # Parse portfolio
        try:
            holdings = json.loads(portfolio_json)
        except json.JSONDecodeError:
            return "❌ Invalid JSON format. Please provide a valid portfolio dictionary.", None

        # Validate holdings
        if not isinstance(holdings, dict):
            return "❌ Portfolio must be a dictionary of {ticker: weight}", None

        # Build the agent
        app = build_cycles_agent()

        # Create initial state
        initial_state = {
            "holdings": holdings,
            "violations": [],
            "iteration_count": 0,
            "adjustments_made": [],
            "status": "checking"
        }

        # Execute agent (will iterate until satisfied or max iterations)
        final_state = app.invoke(initial_state)

        # Format results
        result_text = format_results(initial_state, final_state)

        # Generate graph visualization
        from utils.graph_viz import visualize_graph
        graph_image = visualize_graph(app)

        return result_text, graph_image

    except Exception as e:
        error_msg = f"❌ Error executing constraint checker: {str(e)}"
        return error_msg, None


def format_results(initial_state: PortfolioState, final_state: PortfolioState) -> str:
    """
    Formats the constraint checking results for display.

    Args:
        initial_state: Starting portfolio state
        final_state: Final portfolio state after iterations

    Returns:
        Formatted result string
    """
    result = "# 🔄 PORTFOLIO CONSTRAINT ANALYSIS\n\n"

    # Initial portfolio
    result += "## Initial Portfolio\n"
    for ticker, weight in sorted(initial_state["holdings"].items()):
        result += f"- **{ticker}**: {weight:.1%}\n"
    result += f"\n**Total**: {sum(initial_state['holdings'].values()):.1%}\n\n"

    # Iterations
    result += f"## Iteration Summary\n"
    result += f"**Total Iterations**: {final_state['iteration_count']}\n\n"

    # Violations (if any)
    if final_state["violations"]:
        result += "## ⚠️ Remaining Violations\n"
        for v in final_state["violations"]:
            result += f"- {v['message']}\n"
        result += "\n"

    # Adjustments made
    if final_state["adjustments_made"]:
        result += "## 🔧 Adjustments Made\n"
        for adj in final_state["adjustments_made"]:
            result += f"- {adj}\n"
        result += "\n"

    # Final portfolio
    result += "## Final Portfolio\n"
    for ticker, weight in sorted(final_state["holdings"].items()):
        result += f"- **{ticker}**: {weight:.1%}\n"
    result += f"\n**Total**: {sum(final_state['holdings'].values()):.1%}\n\n"

    # Status
    if len(final_state["violations"]) == 0:
        result += "## ✅ Status: ALL CONSTRAINTS SATISFIED\n\n"
        result += "The portfolio meets all defined constraints:\n"
        result += f"✓ No position exceeds {MAX_POSITION_SIZE:.1%}\n"
        result += f"✓ Cash reserve above {MIN_CASH_RESERVE:.1%}\n"
        result += "✓ Portfolio sums to 100%\n"
    elif final_state["iteration_count"] >= MAX_ITERATIONS:
        result += "## ⚠️ Status: MAXIMUM ITERATIONS REACHED\n\n"
        result += f"Could not satisfy all constraints within {MAX_ITERATIONS} iterations.\n"
        result += "Manual review recommended.\n"
    else:
        result += "## ❌ Status: CONSTRAINTS VIOLATED\n"

    return result
