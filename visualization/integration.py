"""
Displays the interactive Plotly figures from Toqua API data
"""

import streamlit as st


def display_graph_artifact(fig, metadata):
    """
    Displays the Plotly figure artifact in Streamlit session state.
    """
    if metadata is None:
        metadata = {}

    st.session_state["latest_figure"] = fig
    st.session_state["latest_metadata"] = metadata

    return {"status": "success"}
