from jinja2 import Template
from database.db import get_connection
import pdfkit
import os

def generate_invoice_html(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch order
    cursor.execute("""
        SELECT so.id, so.date, so.total, c.name, c.email, c.phone
        FROM sales_orders so
        LEFT JOIN customers c ON so.customer_id = c.id
        WHERE so.id = ?
    """, (order_id,))
    order = cursor.fetchone()

    if not order:
        return None

    order_id, date, total, customer_name, email, phone = order

    # Fetch items
    cursor.execute("""
        SELECT p.name, si.quantity, si.price
        FROM sales_items si
        LEFT JOIN products p ON si.product_id = p.id
        WHERE si.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()

    conn.close()

    # Build HTML rows
    items_html = ""
    for name, qty, price in items:
        items_html += f"""
        <tr>
            <td>{name}</td>
            <td>{qty}</td>
            <td>{price:.2f}</td>
            <td>{qty * price:.2f}</td>
        </tr>
        """

    # Load template
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent
    TEMPLATE_PATH = BASE_DIR.parent / "templates" / "invoice_template.html"

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        #html_template = f.read()
        template = Template(f.read())
    #with open("Erp_app/venv/templates/invoice_template.html") as f:
        #template = Template(f.read())

    html = template.render(
        order_id=order_id,
        date=date,
        customer_name=customer_name,
        email=email,
        phone=phone,
        items_html=items_html,
        total=f"{total:.2f}"
    )

    return html




from weasyprint import HTML, CSS

def export_invoice_pdf(html, filename):
    HTML(string=html).write_pdf(
        filename,
        stylesheets=[CSS(string="""
            body { font-family: Arial; }
            h1 { color: #333; }
        """)]
    )
    return filename

