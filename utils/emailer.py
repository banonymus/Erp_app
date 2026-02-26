import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import streamlit as st


load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_invoice_email(to_email, subject, body, pdf_path):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Load template
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent

    TEMPLATE_PATH = BASE_DIR.parent / "invoice.pdf"

    import os

    st.write("Current working directory:", os.getcwd())
    st.write("Files in directory:", os.listdir())

    # Attach PDF
    with open(TEMPLATE_PATH, "rb") as f:
        pdf_data = f.read()
        msg.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path)
        )

    # Send email
    context = ssl.create_default_context()
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

    return True
