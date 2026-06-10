from database import get_connection

def add_to_cart(user_id, product_id, quantity):
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0.")

    conn = get_connection()
    try:
        product = conn.execute(
            "SELECT stock_quantity, product_name FROM Products WHERE product_id=?", (product_id,)
        ).fetchone()

        if not product:
            raise ValueError("Product not found.")

        if product["stock_quantity"] == 0:
            raise ValueError(f"'{product['product_name']}' is currently out of stock.")

        existing = conn.execute(
            "SELECT cart_id, quantity FROM Cart WHERE user_id=? AND product_id=?",
            (user_id, product_id)
        ).fetchone()

        if existing:
            new_qty = existing["quantity"] + quantity
            if product["stock_quantity"] < new_qty:
                raise ValueError(f"Only {product['stock_quantity']} units available.")
            conn.execute("UPDATE Cart SET quantity=? WHERE cart_id=?", (new_qty, existing["cart_id"]))
        else:
            if product["stock_quantity"] < quantity:
                raise ValueError(f"Only {product['stock_quantity']} units available.")
            conn.execute(
                "INSERT INTO Cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                (user_id, product_id, quantity)
            )

        conn.commit()
    finally:
        conn.close()

def view_cart(user_id):
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT c.cart_id, p.product_id, p.product_name, p.category, p.price,
                   c.quantity, (p.price * c.quantity) AS subtotal
            FROM Cart c
            JOIN Products p ON c.product_id = p.product_id
            WHERE c.user_id = ?
            ORDER BY p.product_name
        """, (user_id,)).fetchall()
    finally:
        conn.close()

def remove_from_cart(cart_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM Cart WHERE cart_id=?", (cart_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Cart item ID {cart_id} not found.")
    finally:
        conn.close()

def clear_cart(user_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM Cart WHERE user_id=?", (user_id,))
        conn.commit()
    finally:
        conn.close()
