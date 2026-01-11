"""
Graph Visualization Utilities
Handles generation and display of LangGraph workflow visualizations.
"""

import io
from PIL import Image
from typing import Optional


def visualize_graph(app) -> Optional[Image.Image]:
    """
    Generates a visual representation of a LangGraph workflow.

    Args:
        app: Compiled LangGraph application

    Returns:
        PIL Image object for display in Gradio, or None if visualization fails

    Example:
        >>> from langgraph.graph import StateGraph
        >>> workflow = StateGraph(MyState)
        >>> # ... build workflow ...
        >>> app = workflow.compile()
        >>> img = visualize_graph(app)
        >>> # Display in Gradio: gr.Image(value=img)
    """
    try:
        # Get graph as PNG bytes using Mermaid
        graph_png = app.get_graph().draw_mermaid_png()

        # Convert bytes to PIL Image for Gradio compatibility
        img = Image.open(io.BytesIO(graph_png))

        return img

    except Exception as e:
        print(f"⚠️ Graph visualization failed: {e}")
        return None


def get_mermaid_diagram(app) -> str:
    """
    Returns the Mermaid diagram code for a LangGraph workflow.

    Args:
        app: Compiled LangGraph application

    Returns:
        String containing Mermaid diagram syntax

    Example:
        >>> mermaid_code = get_mermaid_diagram(app)
        >>> print(mermaid_code)
        graph TD
            __start__ --> agent
            agent --> action
            ...
    """
    try:
        return app.get_graph().draw_mermaid()
    except Exception as e:
        return f"Error generating Mermaid diagram: {e}"


def save_graph_image(app, filename: str) -> bool:
    """
    Saves a LangGraph workflow visualization to a PNG file.

    Args:
        app: Compiled LangGraph application
        filename: Output file path (should end in .png)

    Returns:
        True if successful, False otherwise

    Example:
        >>> success = save_graph_image(app, "workflow.png")
        >>> if success:
        ...     print("Graph saved!")
    """
    try:
        png_bytes = app.get_graph().draw_mermaid_png()

        with open(filename, "wb") as f:
            f.write(png_bytes)

        print(f"✅ Graph saved to {filename}")
        return True

    except Exception as e:
        print(f"❌ Failed to save graph: {e}")
        return False
