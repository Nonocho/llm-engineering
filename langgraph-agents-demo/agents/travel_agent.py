"""
Travel Planning Agent
A sophisticated agent using LangGraph to coordinate multiple tools for travel planning.

Features:
- Real-time flight search via Amadeus API
- Hotel search via Amadeus API
- Web search for news and advisories via Tavily
- Current date utility for relative date queries
"""

import os
from datetime import date
from typing import TypedDict, Annotated, Sequence, Literal
import operator

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from amadeus import Client, ResponseError


# ============================================================================
# AGENT STATE
# ============================================================================

class AgentState(TypedDict):
    """State for the travel planning agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@tool
def get_current_date_tool():
    """
    Returns the current date in 'YYYY-MM-DD' format.
    Useful for finding flights or hotels relative to today's date.

    Returns:
        str: Current date in ISO format (YYYY-MM-DD)

    Example:
        >>> get_current_date_tool()
        '2026-01-11'
    """
    return date.today().isoformat()


@tool
def search_flights_tool(
    origin_code: str,
    destination_code: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
    currency: str = "USD",
    max_offers: int = 5,
):
    """
    Searches for flight offers using the Amadeus Flight Offers Search API.

    Args:
        origin_code: IATA airport code for departure (e.g., 'YYZ' for Toronto)
        destination_code: IATA airport code for arrival (e.g., 'CDG' for Paris)
        departure_date: Departure date in 'YYYY-MM-DD' format
        return_date: Optional return date in 'YYYY-MM-DD' format (for round trips)
        adults: Number of adult passengers (default: 1)
        travel_class: Travel class - ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST
        currency: Currency code for pricing (default: USD)
        max_offers: Maximum number of offers to return (default: 5)

    Returns:
        str: Formatted flight offers with prices, airlines, and times

    Example:
        >>> search_flights_tool('YYZ', 'CDG', '2026-06-01', '2026-06-07', 2)
        'Flight 1: Air Canada... $850 per person...'
    """
    try:
        # Initialize Amadeus client
        amadeus = Client(
            client_id=os.getenv('AMADEUS_CLIENT_ID'),
            client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
        )

        # Build search parameters
        search_params = {
            'originLocationCode': origin_code,
            'destinationLocationCode': destination_code,
            'departureDate': departure_date,
            'adults': adults,
            'travelClass': travel_class,
            'currencyCode': currency,
            'max': max_offers
        }

        # Add return date if provided
        if return_date:
            search_params['returnDate'] = return_date

        # Execute search
        response = amadeus.shopping.flight_offers_search.get(**search_params)

        # Parse and format results
        if not response.data:
            return "No flights found for the specified criteria."

        results = []
        for idx, offer in enumerate(response.data[:max_offers], 1):
            price = offer['price']['total']
            currency = offer['price']['currency']

            # Extract itinerary details
            itineraries = offer['itineraries']
            outbound = itineraries[0]
            segments = outbound['segments']

            # First segment details
            first_segment = segments[0]
            airline = first_segment['carrierCode']
            departure = first_segment['departure']['at']
            arrival = segments[-1]['arrival']['at']

            result = f"Flight {idx}:\n"
            result += f"  Airline: {airline}\n"
            result += f"  Departure: {departure}\n"
            result += f"  Arrival: {arrival}\n"
            result += f"  Price: {currency} {price}\n"

            results.append(result)

        return "\n".join(results)

    except ResponseError as error:
        return f"Amadeus API Error: {error.description}"
    except Exception as e:
        return f"Error searching flights: {str(e)}"


@tool
def search_hotels_tool(
    city_code: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 1,
    radius: int = 5,
    radius_unit: str = "KM",
    currency: str = "USD",
    max_offers: int = 5
):
    """
    Searches for hotel offers using the Amadeus Hotel Search API.

    Args:
        city_code: IATA city code (e.g., 'PAR' for Paris, 'NYC' for New York)
        check_in_date: Check-in date in 'YYYY-MM-DD' format
        check_out_date: Check-out date in 'YYYY-MM-DD' format
        adults: Number of adult guests (default: 1)
        radius: Search radius from city center (default: 5)
        radius_unit: Unit for radius - KM or MILE (default: KM)
        currency: Currency code for pricing (default: USD)
        max_offers: Maximum number of offers to return (default: 5)

    Returns:
        str: Formatted hotel offers with names, ratings, and prices

    Example:
        >>> search_hotels_tool('PAR', '2026-06-01', '2026-06-07', 2)
        'Hotel 1: Hotel Paris... 4 stars... $150/night...'
    """
    try:
        # Initialize Amadeus client
        amadeus = Client(
            client_id=os.getenv('AMADEUS_CLIENT_ID'),
            client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
        )

        # First, search for hotel IDs by city
        hotel_search = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code
        )

        if not hotel_search.data:
            return f"No hotels found in {city_code}."

        # Get first few hotel IDs
        hotel_ids = [hotel['hotelId'] for hotel in hotel_search.data[:10]]

        # Search for offers
        offer_search = amadeus.shopping.hotel_offers_search.get(
            hotelIds=','.join(hotel_ids),
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=adults,
            currency=currency
        )

        if not offer_search.data:
            return "No hotel offers available for the specified dates."

        # Format results
        results = []
        for idx, hotel in enumerate(offer_search.data[:max_offers], 1):
            name = hotel.get('hotel', {}).get('name', 'Unknown Hotel')

            # Get best offer
            if hotel.get('offers'):
                offer = hotel['offers'][0]
                price = offer['price']['total']
                currency = offer['price']['currency']

                result = f"Hotel {idx}:\n"
                result += f"  Name: {name}\n"
                result += f"  Price: {currency} {price} (total)\n"

                results.append(result)

        if not results:
            return "No hotel offers with pricing available."

        return "\n".join(results)

    except ResponseError as error:
        return f"Amadeus API Error: {error.description}"
    except Exception as e:
        return f"Error searching hotels: {str(e)}"


# Initialize Tavily web search tool
tavily_search_tool = TavilySearchResults(
    max_results=3,
    search_depth="advanced",
    include_answer=True
)


# ============================================================================
# LLM CONFIGURATION
# ============================================================================

llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0,
    max_tokens=4096
)


# ============================================================================
# AGENT NODES
# ============================================================================

def call_model_with_tools(state: AgentState, tools: list):
    """
    Agent node that calls the LLM with tools bound.

    Args:
        state: Current agent state with message history
        tools: List of tools available to the agent

    Returns:
        Updated state with LLM response
    """
    messages = state["messages"]

    # Bind tools to the LLM
    model_with_tools = llm.bind_tools(tools)

    # Invoke with conversation history
    response = model_with_tools.invoke(messages)

    # Return new message to be appended to state
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["action", "__end__"]:
    """
    Routing function to decide next step.

    Args:
        state: Current agent state

    Returns:
        "action" if tools should be called, "__end__" to terminate
    """
    last_message = state["messages"][-1]

    # If the LLM made tool calls, route to action node
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "action"

    # Otherwise, end the workflow
    return "__end__"


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def build_travel_agent():
    """
    Constructs and compiles the travel planning agent graph.

    Returns:
        Compiled LangGraph application ready for invocation

    Graph Structure:
        Entry: agent
        ├─ agent (LLM with tools)
        │  └─ Conditional routing:
        │     ├─ "action" → tool_node
        │     └─ "__end__" → END
        └─ action (ToolNode)
           └─ Loop back to agent
    """
    # Define all available tools
    tools = [
        tavily_search_tool,
        search_flights_tool,
        search_hotels_tool,
        get_current_date_tool
    ]

    # Create tool execution node
    tool_node = ToolNode(tools)

    # Create agent node (bind tools)
    def agent_node(state: AgentState):
        return call_model_with_tools(state, tools)

    # Build the state graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("action", tool_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edge (routing logic)
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "action": "action",
            "__end__": END
        }
    )

    # Add edge from tools back to agent (creates the loop)
    workflow.add_edge("action", "agent")

    # Compile and return
    return workflow.compile()


# ============================================================================
# EXECUTION HELPERS
# ============================================================================

def run_travel_agent(user_query: str) -> tuple[str, object]:
    """
    Executes the travel agent with a user query.

    Args:
        user_query: User's travel-related question or request

    Returns:
        Tuple of (response_text, graph_visualization)

    Example:
        >>> response, graph = run_travel_agent("Find flights from YYZ to CDG")
    """
    try:
        # Build the agent
        app = build_travel_agent()

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_query)]
        }

        # Execute agent
        final_state = app.invoke(
            initial_state,
            config={"recursion_limit": 15}
        )

        # Extract final response
        final_message = final_state["messages"][-1]

        if isinstance(final_message, AIMessage):
            response_text = final_message.content
        else:
            response_text = str(final_message)

        # Generate graph visualization
        from utils.graph_viz import visualize_graph
        graph_image = visualize_graph(app)

        return response_text, graph_image

    except Exception as e:
        error_msg = f"Error executing travel agent: {str(e)}"
        return error_msg, None


def stream_travel_agent(user_query: str):
    """
    Streams the travel agent execution for real-time UI updates.

    Args:
        user_query: User's travel-related question or request

    Yields:
        Chunks of text as the agent executes

    Example:
        >>> for chunk in stream_travel_agent("Find hotels in Paris"):
        ...     print(chunk)
    """
    try:
        # Build the agent
        app = build_travel_agent()

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_query)]
        }

        # Stream execution
        tools_used = []
        for chunk in app.stream(initial_state, config={"recursion_limit": 15}):
            # Extract node name and content
            node_name, node_output = next(iter(chunk.items()))

            if isinstance(node_output, dict) and "messages" in node_output:
                for msg in node_output["messages"]:
                    if isinstance(msg, ToolMessage):
                        tools_used.append(msg.name)
                        yield f"\n\n**🔧 Tool Used:** {msg.name}\n{msg.content}\n\n"
                    elif isinstance(msg, AIMessage) and msg.content:
                        yield msg.content

        # Summary
        if tools_used:
            yield f"\n\n**📊 Tools Used:** {', '.join(set(tools_used))}"

    except Exception as e:
        yield f"❌ Error: {str(e)}"
