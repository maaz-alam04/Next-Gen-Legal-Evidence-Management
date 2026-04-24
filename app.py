import streamlit as st

st.set_page_config(
    page_title="Next Gen Legal Evidence Management",
    page_icon="⚖️",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page("pages/report_generation.py", title="Report Generation", icon="📄"),
        st.Page("pages/chat.py", title="Start Chat", icon="💬"),
    ]
)

pg.run()
