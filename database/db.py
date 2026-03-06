import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")

def get_connection():
    return psycopg2.connect(POSTGRES_URL)
