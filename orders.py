from database import get_connection

def place_order(user_id):
    conn = get_connection()
    try:
        cart_items = conn.execute("""
            SELECT c.product_id, c.quantity, p.price, p.stock_quantity, p.product_name
            FROM Cart c
            JOIN Products p ON c.product_id = p.product_id
            WHERE c.user_id = ?
        """, (user_id,)).fetchall()

        if not cart_items:
            raise ValueError("Cart is empty. Add products before placing an order.")

        for item in cart_items:
            if item["stock_quantity"] < item["quantity"]:
                raise ValueError(
                    f"Insufficient stock for '{item['product_name']}'. "
                    f"Available: {item['stock_quantity']}, Requested: {item['quantity']}"
                )

        total_amount = sum(item["price"] * item["quantity"] for item in cart_items)

        conn.execute("BEGIN")
        cur = conn.execute(
            "INSERT INTO Orders (user_id, total_amount, status) VALUES (?, ?, 'Pending')",
            (user_id, total_amount)
        )
        order_id = cur.lastrowid

        for item in cart_items:
            conn.execute(
                "INSERT INTO Order_Items (order_id, product_id, quantity, item_price) VALUES (?, ?, ?, ?)",
                (order_id, item["product_id"], item["quantity"], item["price"])
            )
            conn.execute(
                "UPDATE Products SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
                (item["quantity"], item["product_id"])
            )

        conn.execute("DELETE FROM Cart WHERE user_id=?", (user_id,))
        conn.commit()
        return order_id, total_amount

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_all_orders(user_id=None):
    conn = get_connection()
    try:
        if user_id:
            return conn.execute("""
                SELECT o.order_id, u.name, u.email, o.order_date, o.total_amount, o.status
                FROM Orders o JOIN Users u ON o.user_id = u.user_id
                WHERE o.user_id = ? ORDER BY o.order_date DESC
            """, (user_id,)).fetchall()
        return conn.execute("""
            SELECT o.order_id, u.name, u.email, o.order_date, o.total_amount, o.status
            FROM Orders o JOIN Users u ON o.user_id = u.user_id
            ORDER BY o.order_date DESC
        """).fetchall()
    finally:
        conn.close()

def get_order_details(order_id):
    conn = get_connection()
    try:
        order = conn.execute("""
            SELECT o.order_id, u.name, u.email, u.phone, o.order_date, o.total_amount, o.status
            FROM Orders o JOIN Users u ON o.user_id = u.user_id
            WHERE o.order_id = ?
        """, (order_id,)).fetchone()

        items = conn.execute("""
            SELECT p.product_name, p.category, oi.quantity, oi.item_price,
                   (oi.quantity * oi.item_price) AS subtotal
            FROM Order_Items oi JOIN Products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """, (order_id,)).fetchall()

        payment = conn.execute("SELECT * FROM Payments WHERE order_id=?", (order_id,)).fetchone()
        return order, items, payment
    finally:
        conn.close()

def cancel_order(order_id):
    conn = get_connection()
    try:
        order = conn.execute("SELECT status FROM Orders WHERE order_id=?", (order_id,)).fetchone()
        if not order:
            raise ValueError(f"Order ID {order_id} not found.")
        if order["status"] in ("Delivered", "Cancelled"):
            raise ValueError(f"Cannot cancel an order with status '{order['status']}'.")

        items = conn.execute(
            "SELECT product_id, quantity FROM Order_Items WHERE order_id=?", (order_id,)
        ).fetchall()

        conn.execute("BEGIN")
        conn.execute("UPDATE Orders SET status='Cancelled' WHERE order_id=?", (order_id,))

        for item in items:
            conn.execute(
                "UPDATE Products SET stock_quantity = stock_quantity + ? WHERE product_id=?",
                (item["quantity"], item["product_id"])
            )

        conn.execute(
            "UPDATE Payments SET payment_status='Refunded' WHERE order_id=? AND payment_status='Completed'",
            (order_id,)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def update_order_status(order_id, status):
    allowed_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    if status not in allowed_statuses:
        raise ValueError("Invalid order status.")

    conn = get_connection()
    try:
        cur = conn.execute("UPDATE Orders SET status=? WHERE order_id=?", (status, order_id))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Order ID {order_id} not found.")
    finally:
        conn.close()

def record_payment(order_id, payment_method):
    allowed_methods = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery"]
    if payment_method not in allowed_methods:
        raise ValueError("Invalid payment method.")

    conn = get_connection()
    try:
        order = conn.execute("SELECT status FROM Orders WHERE order_id=?", (order_id,)).fetchone()
        if not order:
            raise ValueError(f"Order ID {order_id} not found.")
        if order["status"] == "Cancelled":
            raise ValueError("Cannot record payment for a cancelled order.")

        existing = conn.execute("SELECT payment_status FROM Payments WHERE order_id=?", (order_id,)).fetchone()

        if existing and existing["payment_status"] == "Completed":
            raise ValueError("Payment already completed for this order.")

        if existing:
            conn.execute(
                "UPDATE Payments SET payment_method=?, payment_status='Completed', payment_date=CURRENT_TIMESTAMP WHERE order_id=?",
                (payment_method, order_id)
            )
        else:
            conn.execute(
                "INSERT INTO Payments (order_id, payment_method, payment_status) VALUES (?, ?, 'Completed')",
                (order_id, payment_method)
            )

        conn.execute(
            "UPDATE Orders SET status='Processing' WHERE order_id=? AND status='Pending'", (order_id,)
        )
        conn.commit()
    finally:
        conn.close()

def get_all_payments():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT p.payment_id, p.order_id, u.name, o.total_amount,
                   p.payment_method, p.payment_status, p.payment_date
            FROM Payments p
            JOIN Orders o ON p.order_id = o.order_id
            JOIN Users u ON o.user_id = u.user_id
            ORDER BY p.payment_date DESC
        """).fetchall()
    finally:
        conn.close()

def report_revenue():
    conn = get_connection()
    try:
        total = conn.execute("""
            SELECT COUNT(*) AS total_orders,
                   COALESCE(SUM(total_amount), 0) AS total_revenue,
                   COALESCE(AVG(total_amount), 0) AS avg_order_value
            FROM Orders WHERE status != 'Cancelled'
        """).fetchone()

        monthly = conn.execute("""
            SELECT strftime('%Y-%m', order_date) AS month,
                   COUNT(*) AS orders,
                   COALESCE(SUM(total_amount), 0) AS revenue
            FROM Orders WHERE status != 'Cancelled'
            GROUP BY month ORDER BY month DESC LIMIT 12
        """).fetchall()

        return total, monthly
    finally:
        conn.close()

def report_top_selling_products(limit=5):
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT p.product_name, p.category,
                   SUM(oi.quantity) AS total_sold,
                   SUM(oi.quantity * oi.item_price) AS total_revenue
            FROM Order_Items oi
            JOIN Products p ON oi.product_id = p.product_id
            JOIN Orders o ON oi.order_id = o.order_id
            WHERE o.status != 'Cancelled'
            GROUP BY p.product_id ORDER BY total_sold DESC LIMIT ?
        """, (limit,)).fetchall()
    finally:
        conn.close()

def report_customer_purchases():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT u.user_id, u.name, u.email,
                   COUNT(o.order_id) AS total_orders,
                   COALESCE(SUM(o.total_amount), 0) AS total_spent
            FROM Users u
            LEFT JOIN Orders o ON u.user_id = o.user_id AND o.status != 'Cancelled'
            GROUP BY u.user_id ORDER BY total_spent DESC
        """).fetchall()
    finally:
        conn.close()

def report_inventory_status():
    conn = get_connection()
    try:
        summary = conn.execute("""
            SELECT category, COUNT(*) AS product_count,
                   COALESCE(SUM(stock_quantity), 0) AS total_stock,
                   MIN(stock_quantity) AS min_stock,
                   MAX(stock_quantity) AS max_stock
            FROM Products GROUP BY category ORDER BY category
        """).fetchall()

        low_stock = conn.execute(
            "SELECT * FROM Products WHERE stock_quantity <= 10 ORDER BY stock_quantity"
        ).fetchall()

        return summary, low_stock
    finally:
        conn.close()

def report_pending_payments():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT o.order_id, u.name, u.email, o.order_date, o.total_amount, o.status,
                   COALESCE(p.payment_status, 'No Payment Record') AS payment_status
            FROM Orders o
            JOIN Users u ON o.user_id = u.user_id
            LEFT JOIN Payments p ON o.order_id = p.order_id
            WHERE o.status != 'Cancelled'
              AND (p.payment_status IS NULL OR p.payment_status = 'Pending')
            ORDER BY o.order_date
        """).fetchall()
    finally:
        conn.close()

def report_sales_by_category():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT p.category,
                   COUNT(DISTINCT o.order_id) AS total_orders,
                   SUM(oi.quantity) AS units_sold,
                   SUM(oi.quantity * oi.item_price) AS revenue
            FROM Order_Items oi
            JOIN Products p ON oi.product_id = p.product_id
            JOIN Orders o ON oi.order_id = o.order_id
            WHERE o.status != 'Cancelled'
            GROUP BY p.category ORDER BY revenue DESC
        """).fetchall()
    finally:
        conn.close()

def report_orders_by_user():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT u.name, u.email,
                   COUNT(o.order_id) AS total_orders,
                   COALESCE(SUM(o.total_amount), 0) AS total_spent,
                   MAX(o.order_date) AS last_order_date
            FROM Users u
            JOIN Orders o ON u.user_id = o.user_id
            WHERE o.status != 'Cancelled'
            GROUP BY u.user_id ORDER BY total_orders DESC
        """).fetchall()
    finally:
        conn.close()
