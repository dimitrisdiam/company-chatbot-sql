# !pip install langchain langchain-community langchain-experimental openai
# !pip install python-dotenv sqlalchemy

import os
from dotenv import load_dotenv
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
from langchain.sql_database import SQLDatabase
from langchain.memory import ConversationBufferMemory

# Load API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Setup LLM
llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)

# Connect to Databse
db_path = "mock_company.db"
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
tools_kit = SQLDatabaseToolkit(db=db, llm=llm)
tools = tools_kit.get_tools()

# Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


# Build the Agent 
from langchain.agents import initialize_agent

agent_executor = initialize_agent(
    tools = tools,
    llm = llm,
    agent = "zero-shot-react-description",
    memory=memory,
    verbose = True
)

# Streamlit UI
st.set_page_config(page_title="Company Chatbot", layout="wide")
st.title("🤖 Company Assistant Chatbot")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Get user input
user_input = st.chat_input("Ask me about orders, products, stock...")

if user_input:
    # Display user message
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Run the agent
    try:
        response = agent_executor.run(user_input)
    except Exception as e:
        response = f"❌ Error: {str(e)}"

    # Display agent message
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
