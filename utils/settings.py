from database.db import get_connection

def get_settings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM company_settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row

def update_settings(company_name, address, phone, email, invoice_footer, theme_default):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE company_settings
        SET company_name=?, address=?, phone=?, email=?, invoice_footer=?, theme_default=?
        WHERE id = 1
    """, (company_name, address, phone, email, invoice_footer, theme_default))
    conn.commit()
    conn.close()
