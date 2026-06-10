import os
import sys
import re
import auth
import products as prod
import cart as cart_mod
import orders as ord_mod
from database import initialize_database

W = 70

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def hdr(title):
    print("\n" + "═" * W)
    print(f"  {title}")
    print("═" * W)

def ln():
    print("─" * W)

def pause():
    input("\n  Press Enter to continue...")

def ok(msg):
    print(f"\n  ✔  {msg}")

def err(msg):
    print(f"\n  ✘  {msg}")

def info(msg):
    print(f"  ℹ  {msg}")

def fc(v):
    return f"₹{v:,.2f}"

def get_str(prompt, required=True):
    while True:
        v = input(f"  {prompt}: ").strip()
        if v or not required:
            return v
        print("  [!] This field cannot be empty.")

def get_full_name(prompt):
    while True:
        name = input(f"  {prompt}: ").strip()
        try:
            auth.validate_name(name)
            return name
        except ValueError as e:
            print(f"  [!] {e}")

def get_email(prompt):
    while True:
        email = input(f"  {prompt}: ").strip()
        try:
            auth.validate_email(email)
            return email
        except ValueError as e:
            print(f"  [!] {e}")

def get_phone(prompt):
    while True:
        phone = input(f"  {prompt}: ").strip()
        try:
            auth.validate_phone(phone)
            return phone
        except ValueError as e:
            print(f"  [!] {e}")

def get_password(prompt, strict=True):
    while True:
        password = input(f"  {prompt}: ").strip()
        if strict:
            try:
                auth.validate_password(password)
                return password
            except ValueError as e:
                print(f"  [!] {e}")
        else:
            if password:
                return password
            print("  [!] Password cannot be empty.")

def get_int(prompt, min_val=0):
    while True:
        try:
            v = int(input(f"  {prompt}: ").strip())
            if v >= min_val:
                return v
            print(f"  [!] Must be >= {min_val}.")
        except ValueError:
            print("  [!] Enter a valid integer.")

def get_float(prompt, min_val=0.0):
    while True:
        try:
            v = float(input(f"  {prompt}: ").strip())
            if v >= min_val:
                return v
            print(f"  [!] Must be >= {min_val}.")
        except ValueError:
            print("  [!] Enter a valid number.")

def get_choice(prompt, options):
    while True:
        v = input(f"  {prompt}: ").strip()
        if v in options:
            return v
        print(f"  [!] Choose from: {', '.join(options)}")

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery"]
ORDER_STATUSES  = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

def menu_users():
    while True:
        hdr("USER MANAGEMENT")
        print("  1. Register User\n  2. Login User\n  3. View All Users")
        print("  4. Search User\n  5. Update User\n  6. Delete User\n  0. Back")
        ln()
        c = get_choice("Select", ["1","2","3","4","5","6","0"])
        if c == "1": ui_register()
        elif c == "2": ui_login()
        elif c == "3": ui_view_users()
        elif c == "4": ui_search_user()
        elif c == "5": ui_update_user()
        elif c == "6": ui_delete_user()
        else: break

def ui_register():
    hdr("REGISTER USER")
    name  = get_full_name("Full Name")
    email = get_email("Email")
    phone = get_phone("Phone")
    pwd   = get_password("Password", strict=True)
    try:
        auth.register_user(name, email, phone, pwd)
        ok(f"User '{name}' registered successfully.")
    except ValueError as e:
        err(str(e))
    pause()

def ui_login():
    hdr("LOGIN")
    email = get_email("Email")
    pwd   = get_password("Password", strict=False)
    try:
        user = auth.login_user(email, pwd)
        ok(f"Welcome back, {user['name']}!  (User ID: {user['user_id']})")
    except ValueError as e:
        err(str(e))
    pause()

def ui_view_users():
    hdr("ALL USERS")
    users = auth.get_all_users()
    if not users:
        info("No users found.")
    else:
        print(f"  {'ID':<6} {'Name':<25} {'Email':<30} {'Phone':<15} {'Joined'}")
        ln()
        for u in users:
            print(f"  {u['user_id']:<6} {u['name']:<25} {u['email']:<30} {(u['phone'] or 'N/A'):<15} {u['created_at'][:10]}")
    pause()

def ui_search_user():
    hdr("SEARCH USER")
    rows = auth.search_user(get_str("Keyword (name / email / phone)"))
    if not rows:
        info("No matches found.")
    else:
        print(f"  {'ID':<6} {'Name':<25} {'Email':<30} {'Phone'}")
        ln()
        for u in rows:
            print(f"  {u['user_id']:<6} {u['name']:<25} {u['email']:<30} {u['phone'] or 'N/A'}")
    pause()

def ui_update_user():
    hdr("UPDATE USER")
    uid = get_int("User ID", 1)
    user = auth.get_user_by_id(uid)
    if not user:
        err(f"User ID {uid} not found.")
        pause()
        return

    print(f"\n  Current → {user['name']} | {user['email']} | {user['phone']}")
    print("  Enter new values. Validation rules are applied.\n")

    name = get_full_name("Full Name")
    email = get_email("Email")
    phone = get_phone("Phone")

    try:
        auth.update_user(uid, name, email, phone)
        ok("User updated.")
    except ValueError as e:
        err(str(e))
    pause()

def ui_delete_user():
    hdr("DELETE USER")
    uid = get_int("User ID", 1)
    user = auth.get_user_by_id(uid)
    if not user:
        err(f"User ID {uid} not found.")
        pause()
        return
    if input(f"\n  Delete '{user['name']}'? (yes/no): ").strip().lower() == "yes":
        try:
            auth.delete_user(uid)
            ok("User deleted.")
        except Exception as e:
            err(str(e))
    else:
        info("Cancelled.")
    pause()

def menu_products():
    while True:
        hdr("PRODUCT MANAGEMENT")
        print("  1. Add Product\n  2. View All Products\n  3. Search Product")
        print("  4. Search by Category\n  5. Update Product\n  6. Delete Product")
        print("  7. Low Stock Alert\n  8. Product Purchase History\n  0. Back")
        ln()
        c = get_choice("Select", ["1","2","3","4","5","6","7","8","0"])
        if c == "1": ui_add_product()
        elif c == "2": ui_view_products()
        elif c == "3": ui_search_product()
        elif c == "4": ui_search_by_category()
        elif c == "5": ui_update_product()
        elif c == "6": ui_delete_product()
        elif c == "7": ui_low_stock()
        elif c == "8": ui_product_history()
        else: break

def _print_products(rows):
    if not rows:
        info("No products found.")
        return
    print(f"  {'ID':<6} {'Name':<28} {'Category':<18} {'Price':>10} {'Stock':>8}")
    ln()
    for p in rows:
        flag = " ⚠" if p['stock_quantity'] <= 10 else ""
        print(f"  {p['product_id']:<6} {p['product_name']:<28} {p['category']:<18} {fc(p['price']):>10} {str(p['stock_quantity'])+flag:>8}")

def ui_add_product():
    hdr("ADD PRODUCT")
    name  = get_str("Product Name")
    cat   = get_str("Category")
    price = get_float("Price (₹)", 0.01)
    stock = get_int("Stock Quantity", 0)
    try:
        prod.add_product(name, cat, price, stock)
        ok(f"Product '{name}' added.")
    except ValueError as e:
        err(str(e))
    pause()

def ui_view_products():
    hdr("ALL PRODUCTS")
    _print_products(prod.get_all_products())
    pause()

def ui_search_product():
    hdr("SEARCH PRODUCT")
    _print_products(prod.search_product(get_str("Keyword")))
    pause()

def ui_search_by_category():
    hdr("SEARCH BY CATEGORY")
    cats = prod.get_all_categories()
    if not cats:
        info("No categories found.")
        pause()
        return
    for i, c in enumerate(cats, 1):
        print(f"    {i}. {c}")
    cat = get_str("Category name")
    kw = input("  Keyword (blank = all): ").strip()
    _print_products(prod.search_product(kw, cat))
    pause()

def ui_update_product():
    hdr("UPDATE PRODUCT")
    pid = get_int("Product ID", 1)
    p = prod.get_product_by_id(pid)
    if not p:
        err(f"Product ID {pid} not found.")
        pause()
        return

    name = get_str("Product Name")
    cat = get_str("Category")
    price = get_float("Price (₹)", 0.01)
    stock = get_int("Stock Quantity", 0)

    try:
        prod.update_product(pid, name, cat, price, stock)
        ok("Product updated.")
    except ValueError as e:
        err(str(e))
    pause()

def ui_delete_product():
    hdr("DELETE PRODUCT")
    pid = get_int("Product ID", 1)
    p = prod.get_product_by_id(pid)
    if not p:
        err(f"Product ID {pid} not found.")
        pause()
        return
    if input(f"\n  Delete '{p['product_name']}'? (yes/no): ").strip().lower() == "yes":
        try:
            prod.delete_product(pid)
            ok("Product deleted.")
        except Exception as e:
            err(str(e))
    else:
        info("Cancelled.")
    pause()

def ui_low_stock():
    hdr("LOW STOCK ALERT  (≤ 10 units)")
    rows = prod.get_low_stock_products(10)
    if not rows:
        ok("All products have sufficient stock.")
    else:
        _print_products(rows)
    pause()

def ui_product_history():
    hdr("PRODUCT PURCHASE HISTORY")
    pid = get_int("Product ID", 1)
    if not prod.get_product_by_id(pid):
        err(f"Product ID {pid} not found.")
        pause()
        return
    rows = prod.get_product_purchase_history(pid)
    if not rows:
        info("No purchase history.")
    else:
        print(f"  {'Order':<8} {'Customer':<25} {'Qty':>5} {'Price':>10} {'Date':<20} {'Status'}")
        ln()
        for h in rows:
            print(f"  {h['order_id']:<8} {h['name']:<25} {h['quantity']:>5} {fc(h['item_price']):>10} {h['order_date'][:16]:<20} {h['status']}")
    pause()

def menu_cart():
    while True:
        hdr("CART MANAGEMENT")
        print("  1. Add Item to Cart\n  2. View Cart\n  3. Remove Item from Cart\n  0. Back")
        ln()
        c = get_choice("Select", ["1","2","3","0"])
        if c == "1": ui_add_to_cart()
        elif c == "2": ui_view_cart()
        elif c == "3": ui_remove_from_cart()
        else: break

def ui_add_to_cart():
    hdr("ADD TO CART")
    uid = get_int("User ID", 1)
    if not auth.get_user_by_id(uid):
        err(f"User ID {uid} not found.")
        pause()
        return
    pid = get_int("Product ID", 1)
    if not prod.get_product_by_id(pid):
        err(f"Product ID {pid} not found.")
        pause()
        return
    qty = get_int("Quantity", 1)
    try:
        cart_mod.add_to_cart(uid, pid, qty)
        ok("Item added to cart.")
    except ValueError as e:
        err(str(e))
    pause()

def ui_view_cart():
    hdr("VIEW CART")
    uid = get_int("User ID", 1)
    if not auth.get_user_by_id(uid):
        err(f"User ID {uid} not found.")
        pause()
        return
    items = cart_mod.view_cart(uid)
    if not items:
        info("Cart is empty.")
    else:
        total = 0
        print(f"  {'Cart ID':<9} {'Product':<28} {'Price':>10} {'Qty':>5} {'Subtotal':>12}")
        ln()
        for i in items:
            print(f"  {i['cart_id']:<9} {i['product_name']:<28} {fc(i['price']):>10} {i['quantity']:>5} {fc(i['subtotal']):>12}")
            total += i['subtotal']
        ln()
        print(f"  {'TOTAL':>55} {fc(total):>12}")
    pause()

def ui_remove_from_cart():
    hdr("REMOVE FROM CART")
    cid = get_int("Cart Item ID", 1)
    try:
        cart_mod.remove_from_cart(cid)
        ok("Item removed.")
    except ValueError as e:
        err(str(e))
    pause()

def menu_orders():
    while True:
        hdr("ORDER MANAGEMENT")
        print("  1. Place Order\n  2. View All Orders\n  3. View Orders by User")
        print("  4. Order Details\n  5. Cancel Order\n  6. Update Order Status\n  0. Back")
        ln()
        c = get_choice("Select", ["1","2","3","4","5","6","0"])
        if c == "1": ui_place_order()
        elif c == "2": ui_view_orders()
        elif c == "3": ui_my_orders()
        elif c == "4": ui_order_details()
        elif c == "5": ui_cancel_order()
        elif c == "6": ui_update_status()
        else: break

def _print_orders(rows):
    if not rows:
        info("No orders found.")
        return
    print(f"  {'Order ID':<10} {'Customer':<25} {'Date':<20} {'Total':>12} {'Status'}")
    ln()
    for o in rows:
        print(f"  {o['order_id']:<10} {o['name']:<25} {o['order_date'][:16]:<20} {fc(o['total_amount']):>12}  {o['status']}")

def ui_place_order():
    hdr("PLACE ORDER")
    uid = get_int("User ID", 1)
    if not auth.get_user_by_id(uid):
        err(f"User ID {uid} not found.")
        pause()
        return
    items = cart_mod.view_cart(uid)
    if not items:
        info("Cart is empty. Add products first.")
        pause()
        return
    total = sum(i['subtotal'] for i in items)
    print(f"\n  Order Total: {fc(total)}")
    if input("\n  Confirm order? (yes/no): ").strip().lower() != "yes":
        info("Cancelled.")
        pause()
        return
    try:
        oid, amt = ord_mod.place_order(uid)
        ok(f"Order #{oid} placed! Total: {fc(amt)}")
    except ValueError as e:
        err(str(e))
    pause()

def ui_view_orders():
    hdr("ALL ORDERS")
    _print_orders(ord_mod.get_all_orders())
    pause()

def ui_my_orders():
    hdr("ORDERS BY USER")
    uid = get_int("User ID", 1)
    if not auth.get_user_by_id(uid):
        err(f"User ID {uid} not found.")
        pause()
        return
    _print_orders(ord_mod.get_all_orders(uid))
    pause()

def ui_order_details():
    hdr("ORDER DETAILS")
    oid = get_int("Order ID", 1)
    order, items, payment = ord_mod.get_order_details(oid)
    if not order:
        err(f"Order ID {oid} not found.")
        pause()
        return
    print(f"\n  Order #: {order['order_id']} | Status: {order['status']} | Date: {order['order_date'][:16]}")
    print(f"  Customer: {order['name']} | Email: {order['email']} | Phone: {order['phone']}")
    ln()
    for i in items:
        print(f"  {i['product_name']} x{i['quantity']} = {fc(i['subtotal'])}")
    ln()
    print(f"  ORDER TOTAL: {fc(order['total_amount'])}")
    print("  Payment:", "Not recorded yet." if not payment else f"{payment['payment_method']} | {payment['payment_status']}")
    pause()

def ui_cancel_order():
    hdr("CANCEL ORDER")
    oid = get_int("Order ID", 1)
    try:
        ord_mod.cancel_order(oid)
        ok(f"Order #{oid} cancelled and stock restored.")
    except ValueError as e:
        err(str(e))
    pause()

def ui_update_status():
    hdr("UPDATE ORDER STATUS")
    oid = get_int("Order ID", 1)
    print("  Statuses: " + " | ".join(ORDER_STATUSES))
    status = get_choice("New status", ORDER_STATUSES)
    try:
        ord_mod.update_order_status(oid, status)
        ok(f"Order #{oid} updated to '{status}'.")
    except ValueError as e:
        err(str(e))
    pause()

def menu_payments():
    while True:
        hdr("PAYMENT MANAGEMENT")
        print("  1. Record Payment\n  2. View All Payments\n  0. Back")
        ln()
        c = get_choice("Select", ["1","2","0"])
        if c == "1": ui_record_payment()
        elif c == "2": ui_view_payments()
        else: break

def ui_record_payment():
    hdr("RECORD PAYMENT")
    oid = get_int("Order ID", 1)
    for i, m in enumerate(PAYMENT_METHODS, 1):
        print(f"    {i}. {m}")
    idx = get_int("Select method", 1)
    if idx > len(PAYMENT_METHODS):
        err("Invalid payment method selection.")
        pause()
        return
    try:
        ord_mod.record_payment(oid, PAYMENT_METHODS[idx - 1])
        ok(f"Payment recorded for Order #{oid}.")
    except ValueError as e:
        err(str(e))
    pause()

def ui_view_payments():
    hdr("ALL PAYMENTS")
    rows = ord_mod.get_all_payments()
    if not rows:
        info("No payment records.")
    else:
        for p in rows:
            print(f"  Payment ID: {p['payment_id']} | Order: {p['order_id']} | {p['name']} | {fc(p['total_amount'])} | {p['payment_method']} | {p['payment_status']}")
    pause()

def menu_reports():
    while True:
        hdr("REPORTS & ANALYTICS")
        print("  1. Revenue Report\n  2. Monthly Revenue\n  3. Top 5 Selling Products")
        print("  4. Customer Purchase Report\n  5. Inventory Status\n  6. Pending Payments")
        print("  7. Sales by Category\n  8. Orders by User\n  9. Customer Ranking\n  0. Back")
        ln()
        c = get_choice("Select", ["1","2","3","4","5","6","7","8","9","0"])
        if c == "1": ui_revenue()
        elif c == "2": ui_monthly()
        elif c == "3": ui_top_products()
        elif c == "4": ui_customer_report()
        elif c == "5": ui_inventory()
        elif c == "6": ui_pending()
        elif c == "7": ui_by_category()
        elif c == "8": ui_by_user()
        elif c == "9": ui_ranking()
        else: break

def ui_revenue():
    hdr("REVENUE REPORT")
    t, _ = ord_mod.report_revenue()
    print(f"  Total Orders    : {t['total_orders']}")
    print(f"  Total Revenue   : {fc(t['total_revenue'])}")
    print(f"  Avg Order Value : {fc(t['avg_order_value'])}")
    pause()

def ui_monthly():
    hdr("MONTHLY REVENUE")
    _, rows = ord_mod.report_revenue()
    if not rows: info("No data.")
    for r in rows:
        print(f"  {r['month']} | Orders: {r['orders']} | Revenue: {fc(r['revenue'])}")
    pause()

def ui_top_products():
    hdr("TOP 5 SELLING PRODUCTS")
    rows = ord_mod.report_top_selling_products(5)
    if not rows: info("No sales data.")
    for r in rows:
        print(f"  {r['product_name']} | {r['category']} | Sold: {r['total_sold']} | Revenue: {fc(r['total_revenue'])}")
    pause()

def ui_customer_report():
    hdr("CUSTOMER PURCHASE REPORT")
    rows = ord_mod.report_customer_purchases()
    if not rows: info("No data.")
    for r in rows:
        print(f"  {r['name']} | Orders: {r['total_orders']} | Spent: {fc(r['total_spent'])}")
    pause()

def ui_inventory():
    hdr("INVENTORY STATUS")
    summary, low = ord_mod.report_inventory_status()
    for s in summary:
        print(f"  {s['category']} | Products: {s['product_count']} | Stock: {s['total_stock']}")
    if low:
        print("\\n  LOW STOCK:")
        for p in low:
            print(f"  {p['product_name']} - {p['stock_quantity']} units")
    pause()

def ui_pending():
    hdr("PENDING PAYMENTS")
    rows = ord_mod.report_pending_payments()
    if not rows: ok("No pending payments.")
    for r in rows:
        print(f"  Order {r['order_id']} | {r['name']} | {fc(r['total_amount'])} | {r['payment_status']}")
    pause()

def ui_by_category():
    hdr("SALES BY CATEGORY")
    rows = ord_mod.report_sales_by_category()
    if not rows: info("No data.")
    for r in rows:
        print(f"  {r['category']} | Orders: {r['total_orders']} | Units: {r['units_sold']} | Revenue: {fc(r['revenue'])}")
    pause()

def ui_by_user():
    hdr("ORDERS BY USER")
    rows = ord_mod.report_orders_by_user()
    if not rows: info("No data.")
    for r in rows:
        print(f"  {r['name']} | Orders: {r['total_orders']} | Spent: {fc(r['total_spent'])}")
    pause()

def ui_ranking():
    hdr("CUSTOMER RANKING")
    rows = ord_mod.report_customer_purchases()
    for rank, c in enumerate(rows, 1):
        print(f"  {rank}. {c['name']} | {fc(c['total_spent'])} | Orders: {c['total_orders']}")
    pause()

def main():
    initialize_database()
    while True:
        clr()
        print("═" * W)
        print(" " * 14 + "🛒  MINI E-COMMERCE BACKEND SYSTEM")
        print("═" * W)
        print("  1. User Management")
        print("  2. Product Management")
        print("  3. Cart Management")
        print("  4. Order Management")
        print("  5. Payment Management")
        print("  6. Reports & Analytics")
        print("  7. Exit")
        print("═" * W)
        c = get_choice("Select", ["1","2","3","4","5","6","7"])
        if c == "1": menu_users()
        elif c == "2": menu_products()
        elif c == "3": menu_cart()
        elif c == "4": menu_orders()
        elif c == "5": menu_payments()
        elif c == "6": menu_reports()
        else:
            print("\\n  Goodbye!\\n")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\n  Interrupted. Goodbye!\\n")
        sys.exit(0)
    except Exception as e:
        print(f"\\n  Fatal error: {e}")
        sys.exit(1)
