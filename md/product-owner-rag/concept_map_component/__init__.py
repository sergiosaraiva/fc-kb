"""
Concept Map Component - Bidirectional Streamlit component for vis.js network graph.

This component allows the concept map to send clicked node queries back to Python,
bypassing iframe sandbox restrictions that prevent navigation.
"""
import os
import streamlit.components.v1 as components

# Get the directory where this file is located
_COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIR = os.path.join(_COMPONENT_DIR, "frontend")

# Declare the component
_component_func = components.declare_component(
    "concept_map",
    path=_FRONTEND_DIR
)


def concept_map(key=None):
    """
    Render the Financial Consolidation concept map.

    Returns the query string when a user clicks a node and presses the search button,
    or None if no selection has been made.

    Args:
        key: Optional unique key for the component instance

    Returns:
        str or None: The search query from the clicked node, or None
    """
    return _component_func(key=key, default=None)
