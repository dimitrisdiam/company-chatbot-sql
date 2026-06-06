"""Natural-language-to-SQL chatbot over a company database.

Connects an OpenAI chat model to a SQLite database through LangChain's
SQL agent, wrapped in a Streamlit chat interface.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

DB_PATH = "mock_company.db"
MODEL_NAME = "gpt-4o-mini"


def load_database(db_path: str = DB_PATH) -> SQLDatabase:
    """Open a read-only SQL connection to the SQLite database."""
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def build_agent(db: SQLDatabase, api_key: str):
    """Create a SQL agent backed by an OpenAI chat model."""
    llm = ChatOpenAI(api_key=api_key, model=MODEL_NAME, temperature=0)
    return create_sql_agent(llm=llm, db=db, agent_type="openai-tools", verbose=True)


def get_response(agent, question: str) -> str:
    """Run a natural-language question through the agent and return the answer."""
    result = agent.invoke({"input": question})
    return result["output"]


@st.cache_resource
def get_agent():
    """Build the agent once and reuse it across reruns."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY is not set. Add it to your .env file.")
        st.stop()
    return build_agent(load_database(), api_key)


def main() -> None:
    st.set_page_config(page_title="Company Chatbot", layout="wide")
    st.title("Company Assistant Chatbot")
    st.caption("Ask questions about orders, products, and customers in plain English.")

    agent = get_agent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    question = st.chat_input("Ask me about orders, products, stock...")
    if question:
        st.chat_message("user").write(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Querying the database..."):
                try:
                    answer = get_response(agent, question)
                except Exception as exc:  # noqa: BLE001 - surfaced to the user
                    answer = f"Sorry, something went wrong: {exc}"
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
