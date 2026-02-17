
import streamlit as st
from utils.auth import authenticate
import pandas as pd
from database.db import get_connection
from utils.theme import load_theme
load_theme()

theme_choice = st.sidebar.radio("Theme", ["light", "dark"])
st.session_state.theme = theme_choice

if "theme" not in st.session_state:
    st.session_state.theme = "light"



VERSION = "1.0.0"


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = authenticate(username, password)
        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            # Load role
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            st.session_state.role = cursor.fetchone()[0]
            conn.close()
            st.rerun()

            st.success("Login successful!")
            #st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()



st.sidebar.write(f"Logged in as: {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()



st.set_page_config(page_title="ERP Dashboard", layout="wide")
st.title("📊 ERP Dashboard")

conn = get_connection()
cursor = conn.cursor()

# Load products
cursor.execute("SELECT quantity, price FROM products")
products = cursor.fetchall()

# Load customers
cursor.execute("SELECT COUNT(*) FROM customers")
customer_count = cursor.fetchone()[0]

# Load sales orders
cursor.execute("SELECT id, date, total FROM sales_orders")
orders = cursor.fetchall()

# Load sales items
cursor.execute("""
    SELECT p.name, si.quantity
    FROM sales_items si
    LEFT JOIN products p ON si.product_id = p.id
""")
sales_items = cursor.fetchall()

col1, col2, col3, col4 = st.columns(4)






# Total Products
total_products = len(products)
col1.metric("📦 Total Products", total_products)

# Total Customers
col2.metric("👥 Total Customers", customer_count)

# Total Sales Orders
total_orders = len(orders)
col3.metric("🧾 Total Sales Orders", total_orders)

# Inventory Value
inventory_value = sum(q * p for q, p in products)
col4.metric("💰 Inventory Value (€)", f"{inventory_value:,.2f}")

st.subheader("📅 Monthly Sales Overview")

if orders:
    df_orders = pd.DataFrame(orders, columns=["Order ID", "Date", "Total"])
    df_orders["Date"] = pd.to_datetime(df_orders["Date"])
    df_orders["Month"] = df_orders["Date"].dt.to_period("M").astype(str)

    monthly_sales = df_orders.groupby("Month")["Total"].sum()

    st.line_chart(monthly_sales)
else:
    st.info("No sales data available yet.")

st.subheader("🏆 Best-Selling Products")

if sales_items:
    df_items = pd.DataFrame(sales_items, columns=["Product", "Quantity"])
    best_sellers = df_items.groupby("Product")["Quantity"].sum().sort_values(ascending=False)

    st.bar_chart(best_sellers)
else:
    st.info("No sales items found.")


st.subheader("📦 Inventory Summary")

cursor.execute("SELECT name, quantity, price FROM products")
rows = cursor.fetchall()

if rows:
    df_inventory = pd.DataFrame(rows, columns=["Product", "Quantity", "Price (€)"])
    df_inventory["Value (€)"] = df_inventory["Quantity"] * df_inventory["Price (€)"]
    st.dataframe(df_inventory, use_container_width=True)
else:
    st.info("No products found.")
