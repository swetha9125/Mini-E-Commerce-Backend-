import hashlib
import re
from database import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_name(name):
    if not name or len(name.strip()) < 2:
        raise ValueError("Invalid name. Name must contain at least 2 characters.")
    if len(name.strip().split()) < 2:
        raise ValueError("Enter full name with surname. Example: Swetha Madhu")
    if not name.replace(" ", "").isalpha():
        raise ValueError("Name must contain only letters and spaces.")
    if not any(ch.isupper() for ch in name):
        raise ValueError("Name must contain at least one capital letter.")

def validate_email(email):
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
        raise ValueError("Invalid email address. Example: user@example.com")

def validate_phone(phone):
    if not phone:
        raise ValueError("Phone number is required.")
    if not phone.isdigit():
        raise ValueError("Phone number must contain only digits.")
    if len(phone) != 10:
        raise ValueError("Phone number must contain exactly 10 digits.")

def validate_password(password):
    if len(password) < 6:
        raise ValueError("Password must contain at least 6 characters.")
    if " " in password:
        raise ValueError("Password must not contain spaces.")
    if not any(ch.isupper() for ch in password):
        raise ValueError("Password must contain at least one capital letter.")
    if not any(ch.islower() for ch in password):
        raise ValueError("Password must contain at least one small letter.")
    if not any(ch.isdigit() for ch in password):
        raise ValueError("Password must contain at least one number.")

def register_user(name, email, phone, password):
    validate_name(name)
    validate_email(email)
    validate_phone(phone)
    validate_password(password)

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Users (name, email, phone, password) VALUES (?, ?, ?, ?)",
            (name.strip(), email.strip().lower(), phone.strip(), hash_password(password))
        )
        conn.commit()
        return True
    except Exception as e:
        if "UNIQUE" in str(e):
            raise ValueError(f"Email '{email}' is already registered.")
        raise
    finally:
        conn.close()

def login_user(email, password):
    validate_email(email)
    if not password.strip():
        raise ValueError("Password cannot be empty.")

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT * FROM Users WHERE email = ? AND password = ?",
            (email.strip().lower(), hash_password(password))
        ).fetchone()
        if not user:
            raise ValueError("Invalid login. Email or password is incorrect.")
        return dict(user)
    finally:
        conn.close()

def get_all_users():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT user_id, name, email, phone, created_at FROM Users ORDER BY user_id"
        ).fetchall()
    finally:
        conn.close()

def search_user(keyword):
    conn = get_connection()
    try:
        p = f"%{keyword}%"
        return conn.execute(
            "SELECT user_id, name, email, phone FROM Users WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?",
            (p, p, p)
        ).fetchall()
    finally:
        conn.close()

def update_user(user_id, name, email, phone):
    validate_name(name)
    validate_email(email)
    validate_phone(phone)

    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE Users SET name=?, email=?, phone=? WHERE user_id=?",
            (name.strip(), email.strip().lower(), phone.strip(), user_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"User ID {user_id} not found.")
    except Exception as e:
        if "UNIQUE" in str(e):
            raise ValueError(f"Email '{email}' is already in use.")
        raise
    finally:
        conn.close()

def delete_user(user_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM Users WHERE user_id=?", (user_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"User ID {user_id} not found.")
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM Users WHERE user_id=?", (user_id,)).fetchone()
    finally:
        conn.close()
