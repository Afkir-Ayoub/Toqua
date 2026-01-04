import streamlit as st
from dotenv import load_dotenv
from langchain.messages import HumanMessage, AIMessage
import asyncio
import threading
from agent.toqua_agent import ToquaShipAgent


# Config
load_dotenv()
st.set_page_config(
    page_title="Toqua Agent",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("⛴️ Toqua Agent")
st.markdown("""
Agent for performance analysis with interactive visualizations.
""")

# Session state 
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    try:
        st.session_state.agent = ToquaShipAgent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.session_state.agent = None

# Sidebar
with st.sidebar:
    st.header("Configuration")
    st.info("""
    **How to use:**
    1. Ask about ship performance (e.g., "Show fuel consumption for IMO 1234567")
    2. The agent will retrieve data and generate interactive graphs
    3. Adjust parameters in the "What-If Analysis" panel
    4. Download graphs as PNG
    """)

# Main chat 
st.header("Chat")
if len(st.session_state.messages) == 0:
    st.info("👋 Start by asking about ship performance data!") # placeholder msg
    
for message in st.session_state.messages:
    with st.chat_message(message.type):
        st.markdown(message.content)

# Chat input
user_input = st.chat_input("Ask about ship performance...")
if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    st.rerun()