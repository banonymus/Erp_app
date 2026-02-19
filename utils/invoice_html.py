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




from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm

def export_invoice_pdf(order, items, filename="invoice.pdf"):
    """
    order = {
        "id": 1,
        "date": "2026-02-10",
        "customer_name": "Customer One",
        "email": "cust@gmail.com",
        "phone": "999999999",
        "total": 600.00
    }

    items = [
        ("Laptop 15\"", 1, 500.00),
        ("LCD Screen 21\"", 1, 100.00)
    ]
    """

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Margins
    left = 20 * mm
    top = height - 20 * mm

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(left, top, f"Invoice #{order['id']}")

    c.setFont("Helvetica", 12)
    c.drawString(left, top - 15, f"Date: {order['date']}")

    # Customer Info
    y = top - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left, y, "Customer Information")

    c.setFont("Helvetica", 12)
    y -= 15
    c.drawString(left, y, f"Name: {order['customer_name']}")
    y -= 15
    #c.drawString(left, y, f"Email: {order['email']}")
    #y -= 15
    #c.drawString(left, y, f"Phone: {order['phone']}")

    # Table of items
    y -= 30

    table_data = [["Product", "Qty", "Price (€)", "Total (€)"]]

    for name, qty, price in items:
        table_data.append([
            name,
            str(qty),
            f"{price:.2f}",
            f"{qty * price:.2f}"
        ])

    table = Table(table_data, colWidths=[80*mm, 20*mm, 30*mm, 30*mm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, left, y - len(table_data) * 18)

    # Total
    y -= len(table_data) * 18 + 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left, y, f"Order Total: €{order['total']:.2f}")

    # Footer
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)
    c.drawString(left, 20*mm, "Thank you for your business!")

    c.save()
    return filename



