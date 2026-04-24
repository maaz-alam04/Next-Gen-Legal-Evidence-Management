import os
import io
import base64
import tempfile
import time

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

VECTORSTORE_PATH = "vectorstore.index"  # folder name created by FAISS.save_local(...)


def get_gemini_key() -> str | None:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")


def ensure_google_api_key_env():
    gemini_key = get_gemini_key()
    if gemini_key and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = gemini_key


GEMINI_KEY = get_gemini_key()
if not GEMINI_KEY:
    st.error("⚠️ GEMINI_API_KEY not found. Add it to your .env file.")
    st.stop()

ensure_google_api_key_env()
genai.configure(api_key=GEMINI_KEY)


def set_bg(local_image_path: str):
    try:
        if os.path.exists(local_image_path):
            with open(local_image_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode()
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/png;base64,{base64_image}");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )
    except Exception:
        pass


def get_vectorstore(text: str, existing_vectorstore=None):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_KEY,
    )

    if existing_vectorstore:
        existing_vectorstore.add_texts([text])
        existing_vectorstore.save_local(VECTORSTORE_PATH)
        return existing_vectorstore

    vectorstore = FAISS.from_texts(texts=[text], embedding=embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    return vectorstore


def load_vectorstore():
    if os.path.exists(VECTORSTORE_PATH):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=GEMINI_KEY,
        )
        return FAISS.load_local(
            VECTORSTORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return None


def wait_for_file_active(uploaded_file, max_wait=180):
    elapsed = 0
    while elapsed < max_wait:
        info = genai.get_file(uploaded_file.name)
        state = getattr(info, "state", None)
        state_name = getattr(state, "name", None)

        if state_name == "ACTIVE":
            return info
        if state_name == "FAILED":
            return None

        time.sleep(5)
        elapsed += 5

    return None


set_bg("output-onlinepngtools.png")
st.markdown("<h1 style='text-align: center;'>Report Generator</h1>", unsafe_allow_html=True)

video_file = st.file_uploader("Upload a video to generate a report", type=["mp4", "avi", "mov", "mkv"])

response_text = None

if video_file is None:
    st.warning("Please upload a video file.")

if video_file is not None and st.button("Generate Report", use_container_width=True):
    st.warning("📤 Uploading and processing video... Please wait.")

    suffix = os.path.splitext(video_file.name)[1] or ".mp4"
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(video_file.getbuffer())
            tmp_path = tmp.name

        with st.spinner("Uploading to Gemini Files API..."):
            uploaded = genai.upload_file(path=tmp_path)

        with st.spinner("⏳ Waiting for video to be processed..."):
            active_file = wait_for_file_active(uploaded)

        if active_file is None:
            st.error("❌ Video processing failed or timed out. Try a shorter video.")
            st.stop()

        prompt = """
You are analyzing a full video. Provide the following details:

1. Incident Overview: Describe what happened, environmental conditions (e.g., lighting, weather).
2. Suspects: Provide details on their appearance, actions, and any distinguishing features.
3. Victims/Witnesses: If visible, describe them, including their actions.
4. Vehicles: Describe any vehicles, license plates, and their interaction with the crime scene.
5. Affected Items: Describe items impacted during the incident.
6. Suspicious Activities: Identify illegal activities and summarize the sequence of events.
7. Conversations/Sounds: Analyze any audible conversations or sounds relevant to the crime scene.
8. Additional Details: Mention any visible landmarks, signboards, or other context about the scene.

Summarize all information and generate a comprehensive report for the police investigation.
"""

        # You can switch to gemini-1.5-flash-latest if Pro is slow/expensive:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")


        with st.spinner("🤖 Generating report..."):
            response = model.generate_content(
                [active_file, prompt],
                request_options={"timeout": 600},
            )

        response_text = getattr(response, "text", str(response))

    except Exception as e:
        st.error(f"Error encountered: {e}")

    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


if response_text:
    existing_vs = load_vectorstore()
    vectorstore = get_vectorstore(response_text, existing_vs)
    st.session_state.vectorstore = vectorstore

    st.subheader("Generated Report:")
    st.write(response_text)

    pdf_buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf_canvas.setFont("Helvetica", 12)

    wrapped_text = []
    for line in response_text.split("\n"):
        wrapped_text.extend(wrap(line, width=80))

    y = 750
    for line in wrapped_text:
        pdf_canvas.drawString(50, y, line)
        y -= 20
        if y < 50:
            pdf_canvas.showPage()
            pdf_canvas.setFont("Helvetica", 12)
            y = 750

    pdf_canvas.save()
    pdf_buffer.seek(0)

    st.download_button(
        label="Download Report (PDF)",
        data=pdf_buffer,
        file_name="Crime_Report.pdf",
        mime="application/pdf",
    )
