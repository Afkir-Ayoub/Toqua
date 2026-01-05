import streamlit as st
from dotenv import load_dotenv
from langchain.messages import HumanMessage, AIMessage
from agent.toqua_agent import ToquaShipAgent
import json
import plotly.io as pio


# Config
load_dotenv()
st.set_page_config(
    page_title="Toqua Agent",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title
st.title("Toqua Agent")
st.markdown(
    """
Agent for performance analysis with interactive visualizations.
"""
)


# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_figure" not in st.session_state:
    st.session_state.latest_figure = None

if "latest_metadata" not in st.session_state:
    st.session_state.latest_metadata = None

if "latest_performances" not in st.session_state:
    st.session_state.latest_performances = None

if "agent" not in st.session_state:
    try:
        st.session_state.agent = ToquaShipAgent(
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.session_state.agent = None

# Sidebar
with st.sidebar:
    st.header("Configuration")
    if st.button("Clear Chat", width="stretch"):
        st.session_state.messages = []
        st.session_state.latest_figure = None
        st.session_state.latest_metadata = None
        st.session_state.latest_performances = None
        st.rerun()

    st.info(
        """
    **How to use:**
    1. Ask about ship performance
    2. The agent will retrieve data and generate interactive graphs
    3. View performance data and metadata
    4. Download graphs as HTML
    """
    )

    st.divider()
    
    st.success(
        """
    ## Key Features

    - **Interactive Graphs** - Clear ship performance visualizations  
    
    - **Real-Time Data** - Live performance metrics inspired by Toqua API
    
    - **Conversational Updates** - Modify charts by talking to the AI agent  
    
    - **HTML Export** - Share interactive charts instantly
        """
    )


chat_col, graph_col = st.columns([1, 1], gap="large")

# Chat
with chat_col:
    st.header("Chat")
    if len(st.session_state.messages) == 0:
        st.info("👋 Start by asking about ship performance data!")  # placeholder msg
    else:
        for msg in st.session_state.messages:
            if msg.type == "human":
                with st.chat_message("human"):
                    st.markdown(msg.content)
            else:
                with st.chat_message("ai"):
                    st.markdown(msg.content)

    # Chat input
    user_input = st.chat_input("Ask about ship performance...")
    if user_input and st.session_state.agent:
        # Show user message
        human_msg = HumanMessage(content=user_input)
        with st.chat_message("human"):
            st.markdown(human_msg.content)

        # Agent response
        with st.chat_message("ai"):
            with st.spinner("Agent thinking..."):
                latest_figure = st.session_state.latest_figure
                latest_metadata = st.session_state.latest_metadata
                latest_performances = st.session_state.latest_performances
                try:
                    result = st.session_state.agent.agent.invoke(
                        {"messages": [human_msg]}
                    )

                    # Extract performance data + figure/metadata
                    for msg in result["messages"]:
                        if msg.type == "tool":
                            tool_content = json.loads(msg.content)

                            # Performance data
                            performance_data = tool_content["data"].get(
                                "performance_data", None
                            )
                            if performance_data:
                                latest_performances = performance_data

                            # Figure/metadata
                            figure_data = tool_content["data"].get("figure", None)
                            if (
                                figure_data
                                and figure_data != st.session_state.latest_figure
                            ):
                                latest_figure = pio.from_json(figure_data)
                                latest_metadata = tool_content["data"].get(
                                    "metadata", None
                                )

                    ai_msg = result["messages"][-1]
                    if ai_msg.type == "ai":
                        st.markdown(ai_msg.content)
                    else:
                        error_msg = result.get("response", "Unknown error")
                        st.error(f"{error_msg}")
                        ai_msg = AIMessage(content=f"Error: {error_msg}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    ai_msg = AIMessage(content=f"Error: {str(e)}")

        # Update session state
        st.session_state.messages.append(human_msg)
        st.session_state.messages.append(ai_msg)

        if latest_figure and latest_metadata:
            st.session_state.latest_figure = latest_figure
            st.session_state.latest_metadata = latest_metadata
        if latest_performances:
            st.session_state.latest_performances = latest_performances

        st.rerun()

    elif user_input and not st.session_state.agent:
        st.error("Agent not initialized. Check your GROQ_API_KEY in .env")


# Graph Artifact
with graph_col:
    st.header("Graph Artifact")

    if st.session_state.latest_figure:
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Graph", "Performance Table", "Metadata", "Download"]
        )

        with tab1:
            # Plotly graph
            st.plotly_chart(st.session_state.latest_figure, width="stretch")

        with tab2:
            # Display performance data in table format
            if st.session_state.latest_performances:
                st.markdown("**Performance Data:**")
                perf_data = st.session_state.latest_performances

                metrics = {
                    "Speed Over Ground (knots)": perf_data.get("sog", []),
                    "Speed Through Water (knots)": perf_data.get("stw", []),
                    "Main Engine Power (kW)": perf_data.get("me_power", []),
                    "Main Engine RPM": perf_data.get("me_rpm", []),
                    "Fuel Consumption (MT/day)": perf_data.get("me_fo_consumption", []),
                    "Fuel Emissions (kg/day)": perf_data.get("me_fo_emission", []),
                }

                max_len = (
                    max(len(values) for values in metrics.values())
                    if metrics.values()
                    else 0
                )

                # Create table data
                table_data = []
                for i in range(max_len):
                    row = {}
                    for metric, values in metrics.items():
                        row[metric] = values[i] if i < len(values) else ""
                    table_data.append(row)

                if table_data:
                    st.dataframe(table_data, width="stretch")
                    st.caption(f"Showing {len(table_data)} data points")
                else:
                    st.info("No performance data available")
            else:
                st.info("No performance data available")

        with tab3:
            # Display metadata table
            if st.session_state.latest_metadata:
                st.markdown("**Graph Metadata:**")
                metadata = st.session_state.latest_metadata
                metadata_items = [
                    {"Parameter": k, "Value": v} for k, v in metadata.items()
                ]
                st.table(metadata_items)
            else:
                st.info("No graph metadata available")

        with tab4:
            # Download
            st.markdown("**Export this graph:**")

            # HTML export
            html_data = st.session_state.latest_figure.to_html()
            st.download_button(
                label="📥 Download as HTML",
                data=html_data,
                file_name="speed_fuel_curve.html",
                mime="text/html",
                width="stretch",
            )

            st.divider()
            st.caption("💡 Download HTML for interactive viewing")
    else:
        st.info("💬 Start a conversation to see generated graphs here!")
        st.markdown(
            """
        **Example queries to try:**
        - "Show graph of fuel consumption for IMO 9999999"
        - "List all available ships"
        """
        )
