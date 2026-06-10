from database import get_connection

def validate_product(product_name, category, price, stock_quantity):
    if not product_name or len(product_name.strip()) < 2:
        raise ValueError("Product name must contain at least 2 characters.")
    if not category or len(category.strip()) < 2:
        raise ValueError("Category must contain at least 2 characters.")
    if price <= 0:
        raise ValueError("Price must be greater than 0.")
    if stock_quantity < 0:
        raise ValueError("Stock quantity cannot be negative.")

def add_product(product_name, category, price, stock_quantity):
    validate_product(product_name, category, price, stock_quantity)

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Products (product_name, category, price, stock_quantity) VALUES (?, ?, ?, ?)",
            (product_name.strip(), category.strip(), price, stock_quantity)
        )
        conn.commit()
    finally:
        conn.close()

def get_all_products():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT product_id, product_name, category, price, stock_quantity FROM Products ORDER BY category, product_name"
        ).fetchall()
    finally:
        conn.close()

def search_product(keyword, category=None):
    conn = get_connection()
    try:
        p = f"%{keyword}%"
        if category:
            return conn.execute(
                "SELECT * FROM Products WHERE (product_name LIKE ? OR category LIKE ?) AND category=?",
                (p, p, category)
            ).fetchall()
        return conn.execute(
            "SELECT * FROM Products WHERE product_name LIKE ? OR category LIKE ?",
            (p, p)
        ).fetchall()
    finally:
        conn.close()

def update_product(product_id, product_name, category, price, stock_quantity):
    validate_product(product_name, category, price, stock_quantity)

    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE Products SET product_name=?, category=?, price=?, stock_quantity=? WHERE product_id=?",
            (product_name.strip(), category.strip(), price, stock_quantity, product_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Product ID {product_id} not found.")
    finally:
        conn.close()

def delete_product(product_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM Products WHERE product_id=?", (product_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Product ID {product_id} not found.")
    finally:
        conn.close()

def get_product_by_id(product_id):
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM Products WHERE product_id=?", (product_id,)).fetchone()
    finally:
        conn.close()

def get_low_stock_products(threshold=10):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM Products WHERE stock_quantity <= ? ORDER BY stock_quantity",
            (threshold,)
        ).fetchall()
    finally:
        conn.close()

def get_all_categories():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT category FROM Products ORDER BY category").fetchall()
        return [r["category"] for r in rows]
    finally:
        conn.close()

def get_product_purchase_history(product_id):
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT o.order_id, u.name, oi.quantity, oi.item_price, o.order_date, o.status
            FROM Order_Items oi
            JOIN Orders o ON oi.order_id = o.order_id
            JOIN Users u ON o.user_id = u.user_id
            WHERE oi.product_id = ?
            ORDER BY o.order_date DESC
        """, (product_id,)).fetchall()
    finally:
        conn.close()
