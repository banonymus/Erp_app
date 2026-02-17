from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database.db import get_connection
import os

def generate_invoice(order_id, filename="invoice.pdf"):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch order info
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

    # Fetch order items
    cursor.execute("""
        SELECT p.name, si.quantity, si.price
        FROM sales_items si
        LEFT JOIN products p ON si.product_id = p.id
        WHERE si.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()

    conn.close()

    # Create PDF
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 50

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, f"Invoice #{order_id}")
    y -= 40

    # Customer info
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Customer: {customer_name}")
    y -= 20
    c.drawString(50, y, f"Email: {email}")
    y -= 20
    c.drawString(50, y, f"Phone: {phone}")
    y -= 40

    # Table header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Product")
    c.drawString(250, y, "Qty")
    c.drawString(320, y, "Price (€)")
    c.drawString(420, y, "Total (€)")
    y -= 20

    c.setFont("Helvetica", 12)

    # Items
    for name, qty, price in items:
        c.drawString(50, y, name)
        c.drawString(250, y, str(qty))
        c.drawString(320, y, f"{price:.2f}")
        c.drawString(420, y, f"{qty * price:.2f}")
        y -= 20

    # Total
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Order Total: €{total:.2f}")

    c.save()

    return filename
