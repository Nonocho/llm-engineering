"""
Router Pattern Demo
Demonstrates conditional routing in LangGraph using an Investment Analysis Router.

The agent analyzes user queries and routes them to specialized analysis nodes
based on asset type (equity, bond, or alternative investments).
"""

from typing import TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END


# ============================================================================
# STATE DEFINITION
# ============================================================================

class InvestmentState(TypedDict):
    """State for investment analysis routing."""
    user_input: str
    asset_type: str
    analysis_result: str
    routing_path: str


# ============================================================================
# ANALYSIS NODES
# ============================================================================

def analyze_equity(state: InvestmentState) -> InvestmentState:
    """
    Performs fundamental analysis for equity investments.

    Args:
        state: Current state with user query

    Returns:
        Updated state with equity analysis
    """
    result = f"""
📊 **EQUITY ANALYSIS**

Asset Identified: {state['user_input']}

Analysis Type: Fundamental Equity Analysis

Key Metrics to Consider:
- **P/E Ratio**: Price-to-earnings ratio for valuation
- **Revenue Growth**: YoY revenue trends
- **Profit Margins**: Net and operating margins
- **Market Cap**: Company size and liquidity
- **Dividend Yield**: Income generation potential

Recommendation Framework:
1. Review financial statements (10-K, 10-Q)
2. Compare to industry peers
3. Analyze competitive moat
4. Assess management quality
5. Consider macroeconomic factors

Risk Factors:
- Market volatility
- Sector-specific risks
- Company-specific execution risks
"""

    return {
        **state,
        "analysis_result": result,
        "asset_type": "equity"
    }


def analyze_bond(state: InvestmentState) -> InvestmentState:
    """
    Performs credit analysis for fixed income securities.

    Args:
        state: Current state with user query

    Returns:
        Updated state with bond analysis
    """
    result = f"""
📈 **FIXED INCOME ANALYSIS**

Asset Identified: {state['user_input']}

Analysis Type: Credit & Duration Analysis

Key Metrics to Consider:
- **Yield to Maturity (YTM)**: Total return if held to maturity
- **Duration**: Interest rate sensitivity
- **Credit Rating**: S&P, Moody's, Fitch ratings
- **Coupon Rate**: Periodic interest payments
- **Spread**: Premium over risk-free rate

Recommendation Framework:
1. Assess credit quality and default risk
2. Evaluate interest rate environment
3. Calculate duration and convexity
4. Compare to similar bonds
5. Consider tax implications

Risk Factors:
- Credit/default risk
- Interest rate risk
- Inflation risk
- Liquidity risk
"""

    return {
        **state,
        "analysis_result": result,
        "asset_type": "bond"
    }


def analyze_alternative(state: InvestmentState) -> InvestmentState:
    """
    Performs analysis for alternative investments.

    Args:
        state: Current state with user query

    Returns:
        Updated state with alternative investment analysis
    """
    result = f"""
🏦 **ALTERNATIVE INVESTMENT ANALYSIS**

Asset Identified: {state['user_input']}

Analysis Type: Alternative Asset Evaluation

Asset Classes:
- Real Estate / REITs
- Commodities (Gold, Oil, Agriculture)
- Cryptocurrencies
- Private Equity
- Hedge Funds

Key Considerations:
- **Liquidity**: How easily can you exit?
- **Correlation**: Diversification benefits
- **Fees**: Management and performance fees
- **Minimum Investment**: Capital requirements
- **Time Horizon**: Typical holding period

Recommendation Framework:
1. Define investment objective
2. Assess liquidity needs
3. Evaluate track record and management
4. Understand fee structure
5. Consider portfolio allocation

Risk Factors:
- Illiquidity premium/discount
- Valuation complexity
- Regulatory changes
- Concentration risk
"""

    return {
        **state,
        "analysis_result": result,
        "asset_type": "alternative"
    }


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def route_to_analysis(state: InvestmentState) -> Literal["equity", "bond", "alternative"]:
    """
    Routes user query to appropriate analysis node based on keywords.

    Args:
        state: Current state with user_input

    Returns:
        Name of the node to route to

    Routing Logic:
        - "equity" if query mentions stocks, shares, equity
        - "bond" if query mentions bonds, fixed income, treasury
        - "alternative" for everything else (real estate, crypto, commodities)
    """
    user_input = state["user_input"].lower()

    # Check for equity keywords
    equity_keywords = [
        "stock", "stocks", "equity", "equities", "share", "shares",
        "nasdaq", "s&p", "dow", "ipo", "dividend"
    ]
    if any(keyword in user_input for keyword in equity_keywords):
        return "equity"

    # Check for bond keywords
    bond_keywords = [
        "bond", "bonds", "fixed income", "treasury", "treasuries",
        "corporate bond", "municipal bond", "yield", "coupon"
    ]
    if any(keyword in user_input for keyword in bond_keywords):
        return "bond"

    # Default to alternative
    return "alternative"


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def build_router_agent():
    """
    Constructs the investment router workflow.

    Returns:
        Compiled LangGraph application

    Graph Structure:
        Entry: router
        ├─ router (routing decision)
        │  └─ Conditional edges:
        │     ├─ "equity" → equity_analysis → END
        │     ├─ "bond" → bond_analysis → END
        │     └─ "alternative" → alternative_analysis → END
    """
    # Build the state graph
    workflow = StateGraph(InvestmentState)

    # Add analysis nodes
    workflow.add_node("equity_analysis", analyze_equity)
    workflow.add_node("bond_analysis", analyze_bond)
    workflow.add_node("alternative_analysis", analyze_alternative)

    # Set entry point to conditional routing
    workflow.set_conditional_entry_point(
        route_to_analysis,
        {
            "equity": "equity_analysis",
            "bond": "bond_analysis",
            "alternative": "alternative_analysis"
        }
    )

    # All paths lead to END
    workflow.add_edge("equity_analysis", END)
    workflow.add_edge("bond_analysis", END)
    workflow.add_edge("alternative_analysis", END)

    # Compile and return
    return workflow.compile()


# ============================================================================
# EXECUTION HELPER
# ============================================================================

def run_router(user_query: str) -> tuple[str, object]:
    """
    Executes the router agent with a user query.

    Args:
        user_query: User's investment analysis request

    Returns:
        Tuple of (analysis_result, graph_visualization)

    Example:
        >>> response, graph = run_router("Analyze Microsoft stock")
        >>> # Routes to equity_analysis node
    """
    try:
        # Build the agent
        app = build_router_agent()

        # Create initial state
        initial_state = {
            "user_input": user_query,
            "asset_type": "",
            "analysis_result": "",
            "routing_path": ""
        }

        # Execute agent
        final_state = app.invoke(initial_state)

        # Extract result
        response_text = final_state["analysis_result"]

        # Add routing info
        response_text += f"\n\n**🔀 Routing Decision:** {final_state['asset_type'].upper()} analysis path selected"

        # Generate graph visualization
        from utils.graph_viz import visualize_graph
        graph_image = visualize_graph(app)

        return response_text, graph_image

    except Exception as e:
        error_msg = f"Error executing router: {str(e)}"
        return error_msg, None
