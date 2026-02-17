import streamlit as st

def section_title(title, icon=""):
    st.markdown(f"### {icon} {title}")

def success(msg):
    st.success(msg)

def error(msg):
    st.error(msg)

def warn(msg):
    st.warning(msg)

def info(msg):
    st.info(msg)
