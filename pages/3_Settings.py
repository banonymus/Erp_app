import streamlit as st
from utils.settings import get_settings, update_settings

st.title("Company Settings")

settings = get_settings()

company_name = st.text_input("Company Name", settings[1])
address = st.text_area("Address", settings[2])
phone = st.text_input("Phone", settings[3])
email = st.text_input("Email", settings[4])
invoice_footer = st.text_area("Invoice Footer", settings[5])
theme_default = st.selectbox("Default Theme", ["light", "dark"], index=0 if settings[6] == "light" else 1)

if st.button("Save Settings"):
    update_settings(company_name, address, phone, email, invoice_footer, theme_default)
    st.success("Settings updated successfully!")
