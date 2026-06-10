import sqlite3

DB_PATH = "ecommerce.db"


def revenue_report():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*),
               COALESCE(SUM(total_amount), 0),
               COALESCE(AVG(total_amount), 0)
        FROM Orders
        WHERE status != 'Cancelled'
    """)

    total_orders, total_revenue, avg_order = cursor.fetchone()

    print("\n========== REVENUE REPORT ==========")
    print(f"Total Orders       : {total_orders}")
    print(f"Total Revenue      : ₹{total_revenue:.2f}")
    print(f"Average Order Value: ₹{avg_order:.2f}")
    print("=" * 38)

    conn.close()


def monthly_revenue():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', order_date),
               COUNT(*),
               COALESCE(SUM(total_amount), 0)
        FROM Orders
        WHERE status != 'Cancelled'
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY 1
    """)

    rows = cursor.fetchall()

    print("\n========== MONTHLY REVENUE ==========")
    for row in rows:
        print(f"{row[0]} | Orders: {row[1]} | Revenue: ₹{row[2]:.2f}")

    conn.close()


def top_selling_product():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.product_name,
               p.category,
               SUM(oi.quantity),
               SUM(oi.quantity * oi.item_price)
        FROM Order_Items oi
        JOIN Products p ON oi.product_id = p.product_id
        JOIN Orders o ON oi.order_id = o.order_id
        WHERE o.status != 'Cancelled'
        GROUP BY p.product_id
        ORDER BY SUM(oi.quantity) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    print("\n========== TOP SELLING PRODUCT ==========")
    if result:
        print(f"Product  : {result[0]}")
        print(f"Category : {result[1]}")
        print(f"Units    : {result[2]}")
        print(f"Revenue  : ₹{result[3]:.2f}")
    else:
        print("No sales data available.")

    conn.close()


def inventory_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category,
               COUNT(*),
               SUM(stock_quantity)
        FROM Products
        GROUP BY category
        ORDER BY category
    """)

    rows = cursor.fetchall()

    print("\n========== INVENTORY STATUS ==========")
    for row in rows:
        print(f"{row[0]} | Products: {row[1]} | Total Stock: {row[2]}")

    conn.close()


def dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*),
               COALESCE(SUM(total_amount), 0),
               COALESCE(AVG(total_amount), 0)
        FROM Orders
        WHERE status != 'Cancelled'
    """)

    total_orders, total_revenue, avg_order = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Users
    """)
    total_users = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM Products
    """)
    total_products = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM Payments
        WHERE payment_status = 'Completed'
    """)
    completed_payments = cursor.fetchone()[0]

    print("\n========== DASHBOARD ==========")
    print(f"Total Users        : {total_users}")
    print(f"Total Products     : {total_products}")
    print(f"Total Orders       : {total_orders}")
    print(f"Total Revenue      : ₹{total_revenue:.2f}")
    print(f"Average Order      : ₹{avg_order:.2f}")
    print(f"Completed Payments : {completed_payments}")
    print("=" * 32)

    conn.close()