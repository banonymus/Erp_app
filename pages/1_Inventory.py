import streamlit as st
import pandas as pd
from database.db import get_connection
from utils.helpers import section_title

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must log in first.")
    st.stop()

from utils.theme import load_theme
load_theme()


# Database connection
conn = get_connection()
cursor = conn.cursor()

st.title("📦 Inventory Management")

if st.session_state.get("role") != "admin":
    st.error("You do not have permission to access Inventory.")
    st.stop()



tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["➕ Add Product", "📋 View Products", "✏️ Edit Product", "🗑️ Delete Product", "📊 Analytics"]
)

with tab1:
    st.subheader("Add New Product")
    section_title("Add New Product", "➕")
    with st.form("add_product_form"):
        name = st.text_input("Product Name")
        sku = st.text_input("SKU")
        quantity = st.number_input("Quantity", min_value=0)
        price = st.number_input("Price (€)", min_value=0.0)
        submitted = st.form_submit_button("Save Product")

        if submitted:
            try:
                cursor.execute(
                    "INSERT INTO products (name, sku, quantity, price) VALUES (?, ?, ?, ?)",
                    (name, sku, quantity, price)
                )
                conn.commit()
                st.success(f"Product '{name}' added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
    st.balloons()
    st.markdown("---")

with tab2:
    st.subheader("Product List")

    search = st.text_input("Search by name or SKU")

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Name", "SKU", "Quantity", "Price"])

        if search:
            df = df[df["Name"].str.contains(search, case=False) | df["SKU"].str.contains(search, case=False)]

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No products found.")

    st.markdown("---")

    from utils.exporter import df_to_excel

    st.subheader("📤 Export Inventory")

    excel_data = df_to_excel(df)

    st.download_button(
        label="Download Inventory as Excel",
        data=excel_data,
        file_name="inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown("---")
with tab3:
    st.subheader("Edit Product")

    cursor.execute("SELECT id, name FROM products")
    product_list = cursor.fetchall()

    if product_list:
        product_dict = {f"{name} (ID: {pid})": pid for pid, name in product_list}
        selected_product = st.selectbox("Select a product", list(product_dict.keys()))
        product_id = product_dict[selected_product]

        cursor.execute("SELECT name, sku, quantity, price FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        name_edit, sku_edit, qty_edit, price_edit = product

        with st.form("edit_product_form"):
            new_name = st.text_input("Product Name", value=name_edit)
            new_sku = st.text_input("SKU", value=sku_edit)
            new_qty = st.number_input("Quantity", min_value=0, value=qty_edit)
            new_price = st.number_input("Price (€)", min_value=0.0, value=price_edit)

            update_btn = st.form_submit_button("Update Product")

            if update_btn:
                cursor.execute("""
                    UPDATE products
                    SET name = ?, sku = ?, quantity = ?, price = ?
                    WHERE id = ?
                """, (new_name, new_sku, new_qty, new_price, product_id))
                conn.commit()
                st.success("Product updated successfully!")
    else:
        st.info("No products available to edit.")

    st.markdown("---")

with tab4:
    st.subheader("Delete Product")

    cursor.execute("SELECT id, name FROM products")
    product_list = cursor.fetchall()

    if product_list:
        product_dict = {f"{name} (ID: {pid})": pid for pid, name in product_list}
        selected_product = st.selectbox("Select a product to delete", list(product_dict.keys()))
        product_id = product_dict[selected_product]

        if st.button("Delete Product"):
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            st.warning("Product deleted successfully!")
    else:
        st.info("No products available to delete.")

st.markdown("---")


with tab5:
    st.subheader("Inventory Analytics")

    with st.spinner("Loading products..."):
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Name", "SKU", "Quantity", "Price"])

        # KPIs
        total_products = len(df)
        total_stock = df["Quantity"].sum()
        inventory_value = (df["Quantity"] * df["Price"]).sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products", total_products)
        col2.metric("Total Stock Units", total_stock)
        col3.metric("Inventory Value (€)", f"{inventory_value:,.2f}")

        # Low stock
        st.subheader("Low Stock Alerts")
        low_stock_df = df[df["Quantity"] < 5]
        if not low_stock_df.empty:
            st.warning("Some products are running low!")
            st.table(low_stock_df[["Name", "SKU", "Quantity"]])
        else:
            st.success("All products have sufficient stock.")

        # Chart
        st.subheader("Stock Levels Chart")
        chart_df = df[["Name", "Quantity"]].set_index("Name")
        st.bar_chart(chart_df)
    else:
        st.info("No inventory data available.")

