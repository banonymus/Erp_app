import streamlit as st
import pandas as pd
from database.db import get_connection
from utils.exporter import df_to_excel

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must log in first.")
    st.stop()

from utils.theme import load_theme
load_theme()


if "cart" not in st.session_state:
    st.session_state.cart = []


st.title("🧾 Sales Module")

conn = get_connection()
cursor = conn.cursor()

if st.session_state.role == "admin":
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Add Customer",
        "📋 View Customers",
        "🛒 Create Sales Order",
        "📜 Sales History"
    ])
else:
    tab1, tab2, tab3 = st.tabs([
        "➕ Add Customer",
        "📋 View Customers",
        "🛒 Create Sales Order"
    ])




with tab1:
    st.subheader("Add New Customer")

    with st.form("add_customer_form"):
        name = st.text_input("Customer Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")

        submitted = st.form_submit_button("Save Customer")

        if submitted:
            try:
                cursor.execute(
                    "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                    (name, email, phone)
                )
                conn.commit()
                st.success(f"Customer '{name}' added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")


with tab2:
    st.subheader("Customer List")

    search = st.text_input("Search by name, email, or phone")

    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Name", "Email", "Phone"])

        if search:
            df = df[
                df["Name"].str.contains(search, case=False) |
                df["Email"].str.contains(search, case=False) |
                df["Phone"].str.contains(search, case=False)
            ]

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No customers found.")

    st.markdown("---")
    st.subheader("📤 Export Customers")

    excel_data = df_to_excel(df)

    st.download_button(
        label="Download Customers as Excel",
        data=excel_data,
        file_name="customers.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with tab3:
    st.subheader("Create Sales Order")
    cursor.execute("SELECT id, name FROM customers")
    customers = cursor.fetchall()

    if not customers:
        st.warning("No customers found. Add a customer first.")
        st.stop()

    customer_dict = {name: cid for cid, name in customers}
    selected_customer = st.selectbox("Select Customer", list(customer_dict.keys()))
    customer_id = customer_dict[selected_customer]

    cursor.execute("SELECT id, name, price FROM products")
    products = cursor.fetchall()

    if not products:
        st.warning("No products found. Add products in the Inventory module.")
        st.stop()

    product_dict = {f"{name} (€{price})": (pid, price) for pid, name, price in products}
    selected_product = st.selectbox("Select Product", list(product_dict.keys()))
    product_id, product_price = product_dict[selected_product]

    quantity = st.number_input("Quantity", min_value=1, value=1)

    if st.button("Add to Cart"):
        st.session_state.cart.append({
            "product_id": product_id,
            "product_name": selected_product,
            "quantity": quantity,
            "price": product_price,
            "total": quantity * product_price
        })
        st.success("Item added to cart!")

    st.subheader("Cart Items")

    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.table(cart_df[["product_name", "quantity", "price", "total"]])

        order_total = cart_df["total"].sum()
        st.metric("Order Total (€)", f"{order_total:,.2f}")
    else:
        st.info("Cart is empty.")

    if st.button("Clear Cart"):
        st.session_state.cart = []
        st.warning("Cart cleared.")

    if st.button("Save Order"):

        if not st.session_state.cart:
            st.error("Cart is empty. Add items before saving.")
            st.stop()

        # Calculate order total
        cart_df = pd.DataFrame(st.session_state.cart)
        order_total = cart_df["total"].sum()

        try:
            # 1. Insert into sales_orders
            cursor.execute(
                "INSERT INTO sales_orders (customer_id, date, total) VALUES (?, DATE('now'), ?)",
                (customer_id, order_total)
            )
            conn.commit()

            # Get the new order ID
            order_id = cursor.lastrowid

            # 2. Insert each item into sales_items
            for item in st.session_state.cart:
                cursor.execute(
                    "INSERT INTO sales_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (order_id, item["product_id"], item["quantity"], item["price"])
                )

                # 3. Reduce inventory
                cursor.execute(
                    "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                    (item["quantity"], item["product_id"])
                )

            conn.commit()

            # 4. Clear cart
            st.session_state.cart = []

            # 5. Success message
            st.success(f"Order #{order_id} saved successfully!")

        except Exception as e:
            st.error(f"Error saving order: {e}")

with tab4:
    from utils.invoice_html import generate_invoice_html, export_invoice_pdf
    import streamlit as st

    st.subheader("Invoice Preview")

    pdf_order_id = st.number_input(
        "Enter Order ID to view details",
        min_value=1,
        step=1
    )

    #order_ids = df_orders["Order ID"].tolist()
    #selected_order_id = st.selectbox("Select Order", pdf_order_id)

    cursor.execute("""
        SELECT p.name, si.quantity, si.price, (si.quantity * si.price) AS total
        FROM sales_items si
        LEFT JOIN products p ON si.product_id = p.id
        WHERE si.order_id = ?
    """, (pdf_order_id,))
    items = cursor.fetchall()

    cursor.execute("""
            SELECT so.id, c.name, so.date, so.total
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.id
            WHERE so.id = ?
            ORDER BY so.id DESC
        """, (pdf_order_id,))
    orders = cursor.fetchall()

    st.subheader("Invoice Preview")

    html = generate_invoice_html(pdf_order_id)

    if html:
        st.components.v1.html(html, height=800, scrolling=True)
    else:
        st.error("Could not generate invoice.")



    if st.button("Download Invoice as PDF"):

        order_tuple = orders[0]

        order = {
            "id": order_tuple[0],
            "name": order_tuple[1],
            "date": order_tuple[2],
            "total": order_tuple[3],

        }

        #st.text_area(orders[0])
        filename = export_invoice_pdf(order, items, "invoice.pdf")
        with open(filename, "rb") as f:
            st.download_button(
                "Download PDF",
                f,
                file_name="invoice.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Order not found.")

    st.subheader("Sales History")

    if st.session_state.role != "admin":
        st.warning("Only admins can view sales history.")
        st.stop()

    cursor.execute("""
        SELECT so.id, c.name, so.date, so.total
        FROM sales_orders so
        LEFT JOIN customers c ON so.customer_id = c.id
        ORDER BY so.id DESC
    """)
    orders = cursor.fetchall()
    if orders:
        df_orders = pd.DataFrame(orders, columns=["Order ID", "Customer", "Date", "Total (€)"])
    else:
        st.info("No sales orders found.")
        st.stop()

    customer_filter = st.selectbox(
        "Filter by Customer",
        ["All"] + sorted(df_orders["Customer"].unique())
    )

    if customer_filter != "All":
        df_orders = df_orders[df_orders["Customer"] == customer_filter]

    date_filter = st.date_input("Filter by Date", value=None)

    if date_filter:
        df_orders = df_orders[df_orders["Date"] == str(date_filter)]

    st.dataframe(df_orders, use_container_width=True)

    st.subheader("📤 Export Sales Orders")

    excel_data = df_to_excel(df_orders)

    st.download_button(
        label="Download Sales Orders as Excel",
        data=excel_data,
        file_name="sales_orders.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("#### 🧾 Order Details")

    selected_order_id = st.number_input(
        "Enter Order ID to view details",
        min_value=1,
        step=1,
        key="selected_order_id"
    )
    cursor.execute("""
        SELECT p.name, si.quantity, si.price, (si.quantity * si.price) AS total
        FROM sales_items si
        LEFT JOIN products p ON si.product_id = p.id
        WHERE si.order_id = ?
    """, (selected_order_id,))
    items = cursor.fetchall()
    if items:
        df_items = pd.DataFrame(items, columns=["Product", "Quantity", "Price (€)", "Total (€)"])
        st.table(df_items)

        st.metric("Order Total (€)", f"{df_items['Total (€)'].sum():,.2f}")
    else:
        st.info("No items found for this order.")

    st.subheader("📤 Export Sales Items")

    excel_data = df_to_excel(df_items)

    st.download_button(
        label="Download Sales Items as Excel",
        data=excel_data,
        file_name="sales_items.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

