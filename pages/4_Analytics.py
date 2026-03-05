import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_connection

st.title("📈 Advanced Analytics Dashboard")

conn = get_connection()
cursor = conn.cursor()

# Load sales orders
df_orders = pd.read_sql_query("SELECT * FROM sales_orders", conn)

# Load sales items
df_items = pd.read_sql_query("""
    SELECT si.*, p.name AS product_name, p.category
    FROM sales_items si
    LEFT JOIN products p ON si.product_id = p.id
""", conn)

conn.close()

# Convert date column
df_orders["date"] = pd.to_datetime(df_orders["date"] ,format="%d-%m-%Y")

col1, col2, col3, col4 = st.columns(4)

total_sales = df_orders["total"].sum()
total_orders = len(df_orders)
avg_order_value = df_orders["total"].mean()
unique_products_sold = df_items["product_id"].nunique()

col1.metric("Total Sales (€)", f"{total_sales:,.2f}")
col2.metric("Total Orders", total_orders)
col3.metric("Avg Order Value (€)", f"{avg_order_value:,.2f}")
col4.metric("Unique Products Sold", unique_products_sold)

df_orders["month"] = df_orders["date"].dt.to_period("M").astype(str)
monthly_sales = df_orders.groupby("month")["total"].sum().reset_index()

fig = px.line(monthly_sales, x="month", y="total", title="Sales per Month")
st.plotly_chart(fig, use_container_width=True)


category_sales = df_items.groupby("category")["total"].sum().reset_index()

fig = px.pie(category_sales, names="category", values="total",
             title="Sales by Category")
st.plotly_chart(fig, use_container_width=True)


top_products = df_items.groupby("product_name")["total"].sum().nlargest(5).reset_index()

fig = px.bar(top_products, x="product_name", y="total",
             title="Top 5 Products", text_auto=True)
st.plotly_chart(fig, use_container_width=True)


conn = get_connection()
df_customers = pd.read_sql_query("SELECT * FROM customers", conn)
conn.close()

df_orders_customers = df_orders.merge(df_customers, left_on="customer_id", right_on="id")

customer_sales = df_orders_customers.groupby("name")["total"].sum().reset_index()

fig = px.bar(customer_sales, x="name", y="total",
             title="Sales by Customer", text_auto=True)
st.plotly_chart(fig, use_container_width=True)


df_orders["day"] = df_orders["date"].dt.day
df_orders["month_num"] = df_orders["date"].dt.month

pivot = df_orders.pivot_table(values="total", index="month_num", columns="day", aggfunc="sum")

fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Blues",
                title="Sales Heatmap (Month x Day)")
st.plotly_chart(fig, use_container_width=True)
