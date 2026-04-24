import os
import streamlit as st
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

VECTORSTORE_PATH = "vectorstore.index"  # this should be a folder created by FAISS.save_local(...)


def get_gemini_key() -> str | None:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")


def ensure_google_api_key_env():
    """langchain-google-genai reads GOOGLE_API_KEY by default; map from GEMINI_API_KEY."""
    gemini_key = get_gemini_key()
    if gemini_key and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = gemini_key


def load_vectorstore():
    if os.path.exists(VECTORSTORE_PATH):
        try:
            ensure_google_api_key_env()
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=get_gemini_key(),
            )
            return FAISS.load_local(
                VECTORSTORE_PATH,
                embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            st.error(f"Error loading vectorstore: {e}")
    return None


def get_conversation_chain(vectorstore):
    ensure_google_api_key_env()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=get_gemini_key(),
        temperature=0,
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )

    custom_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an assistant specialized in police investigations. You answer questions strictly related to police reports, criminal activities, suspects, or investigations based on the provided context.

Guidelines:
- Only respond to questions relevant to investigations, crime reports, suspects, or legal matters.
- If the question is unrelated, politely decline to answer.
- Refer to Indian law sections and articles based on your knowledge.
- If the answer is unknown or unavailable, respond with "I don't know."
- Do not fabricate information or assumptions.
- If the input is just a greeting or small talk, reply in a friendly, human-like way.
- If the question is about a specific section of law, provide a brief explanation.
- If the question refers to a report not in the provided context, state that the data is unavailable.
- All responses must be in English, concise, factual, and directly relevant to the question.

Use the following context to answer:
{context}

Question: {question}

Answer:""",
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": custom_prompt},
    )


def handle_user_input(user_question: str):
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.conversation.invoke({"question": user_question})
                bot_response = response.get("answer") or response.get("result")

                if not bot_response and "chat_history" in response and response["chat_history"]:
                    bot_response = response["chat_history"][-1].content

                if not bot_response:
                    bot_response = "I don't know."

                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                st.markdown(bot_response)

            except Exception as e:
                st.error(f"Error generating response: {e}")


def run():
    st.title("Chat with Report")

    if not get_gemini_key():
        st.error("⚠️ GEMINI_API_KEY not found. Add it to your .env file.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation" not in st.session_state:
        vectorstore = load_vectorstore()
        if vectorstore:
            st.session_state.vectorstore = vectorstore
            st.session_state.conversation = get_conversation_chain(vectorstore)
        else:
            st.warning("⚠️ No vectorstore found. Please generate a report first in Report Generation.")
            return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the report:"):
        handle_user_input(prompt)


run()
