import streamlit as st

def load_theme():
    theme = st.session_state.get("theme", "light")

    if theme == "dark":
        css = """
        <style>
            body { background-color: #1e1e1e; color: #e0e0e0; }
            .stApp { background-color: #1e1e1e; }
            h1, h2, h3, h4, h5 { color: #ffffff !important; }
            .stButton>button {
                background-color: #333333;
                color: white;
                border-radius: 6px;
            }
            .stDataFrame { background-color: #2a2a2a; }
        </style>
        """
    else:
        css = """
        <style>
            body { background-color: #ffffff; color: #333333; }
            .stApp { background-color: #ffffff; }
            h1, h2, h3, h4, h5 { color: #222222 !important; }
            .stButton>button {
                background-color: #f0f0f0;
                color: black;
                border-radius: 6px;
            }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)
