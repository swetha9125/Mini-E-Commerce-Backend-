# Mini-E-Commerce-Backend-
Mini E-Commerce Backend System built using Python and SQLite with user, product, cart, order, payment, and reporting modules.

## Problem Statement
Many small businesses manage customer details, product inventory, cart items, orders, and payments manually using notebooks or basic spreadsheets. This manual process is time-consuming, prone to errors, and makes it difficult to track stock availability, order history, and sales reports accurately.
This project solves the problem by providing a simple backend system that automates user management, product management, cart handling, order processing, payment recording, and report generation using Python and SQLite.

## Project Description
The Mini E-Commerce Backend System is a console-based backend application developed using Python and SQLite. It provides the core backend operations of an online shopping system without a web interface.
The system allows users to register and log in, manage products, add items to cart, place orders, record payments, update inventory, and generate useful business reports. The project follows a modular structure where different files handle authentication, products, cart, orders, database connection, and main menu operations.

## Objectives
- To automate basic e-commerce backend operations.
- To reduce manual errors in product, cart, order, and payment management.
- To maintain customer and product data in a structured database.
- To handle inventory updates when orders are placed or cancelled.
- To generate useful reports for sales, revenue, inventory, and customers.
- To demonstrate database connectivity, CRUD operations, and modular programming in Python.

## Features
### User Management
- Register new users.
- Login existing users.
- View all users.
- Search users by name, email, or phone number.
- Update user details.
- Delete users.

### Product Management
- Add new products.
- View all products.
- Search products by keyword.
- Search products by category.
- Update product details.
- Delete products.
- Show low stock products.
- View product purchase history.

### Cart Management
- Add products to cart.
- View cart items.
- Remove items from cart.
- Check product availability before adding to cart.
- Prevent adding quantity greater than available stock.

### Order Management
- Place orders from cart.
- Automatically reduce product stock after order placement.
- View all orders.
- View orders by user.
- View detailed order information.
- Cancel orders.
- Restore stock when an order is cancelled.
- Update order status.

### Payment Management
- Record payment for an order.
- View all payment records.
- Prevent duplicate completed payments.
- Prevent payment for cancelled orders.

### Reports and Analytics
- Revenue report.
- Monthly revenue report.
- Top selling products.
- Customer purchase report.
- Inventory status report.
- Pending payments report.
- Sales by category.
- Orders by user.
- Customer ranking.

## Input Validation
The system validates input data to prevent wrong entries and improve reliability.

### User Validation
- Full name must include surname.
- Name must contain only letters and spaces.
- Name must contain at least one capital letter.
- Email must follow a valid email format.
- Phone number must contain exactly 10 digits.
- Password must contain:
  - Minimum 6 characters
  - At least one capital letter
  - At least one lowercase letter
  - At least one number
  - No spaces

### Product Validation
- Product name cannot be empty.
- Category cannot be empty.
- Price must be greater than zero.
- Stock quantity cannot be negative.

### Cart Validation
- User ID must exist.
- Product ID must exist.
- Quantity must be greater than zero.
- Product must be available in stock.
- Requested quantity must not exceed available stock.

### Order Validation
- User ID must exist.
- Empty cart cannot be ordered.
- Invalid order ID is rejected.
- Delivered or cancelled orders cannot be cancelled again.

### Payment Validation
- Order ID must exist.
- Payment method must be valid.
- Duplicate completed payments are prevented.
- Payment cannot be recorded for a cancelled order.

## Technologies Used
| Technology | Purpose                             |
|------------|-------------------------------------|
| Python     | Main programming language           |
| SQLite     | Database management                 |
| SQL        | Database queries and table creation |
| Hashlib    | Password hashing                    |
| OS Module  | File path handling                  |
| RE Module  | Email validation                    | 
| VS Code    | Code editor                         |

## Project Structure
```text
mini_ecommerce_backend/
│
├── main.py
├── database.py
├── schema.sql
├── auth.py
├── products.py
├── cart.py
├── orders.py
├── requirements.txt
└── README.md
```

## File Description
| File Name        | Description                                                               |
|------------------|---------------------------------------------------------------------------|
| main.py          | Contains the main menu and user interface for the console application.    |
| database.py      | Handles SQLite database connection and database initialization.           |
| schema.sql       | Contains SQL commands to create database tables and indexes.              |
| auth.py          | Handles user registration, login, password hashing, and user validation.  |
| products.py      | Handles product CRUD operations and product-related reports.              |
| cart.py          | Handles cart operations such as adding, viewing, and removing cart items. |
| orders.py        | Handles order placement, payment records, order status, and reports.      |
| requirements.txt | Lists project requirements.                                               |
| README.md        | Contains project explanation and running instructions.                    |

## How to Run
### Step 1: Install Python
Install Python 3.10 or above.
Check Python version:
```bash
python --version
```
### Step 2: Open Project Folder
Open the project folder in VS Code or terminal.
```bash
cd mini_ecommerce_backend
```
### Step 3: Run the Project
```bash
python main.py
```
### Step 4: Use the Menu
After running the program, the main menu will appear. Select options to manage users, products, cart, orders, payments, and reports.

## Sample Workflow
1. Register a new user.
2. Login using registered email and password.
3. Add products in Product Management.
4. Add products to cart using User ID and Product ID.
5. View cart.
6. Place an order.
7. Record payment.
8. View reports.

## Database Creation
The database file `ecommerce.db` is created automatically when the program is executed. The tables are created using the SQL commands present in `schema.sql`.

## Learning Outcomes
This project helps in understanding:
- Python modular programming
- SQLite database connectivity
- SQL table creation and queries
- CRUD operations
- User authentication
- Password hashing
- Input validation
- Cart and order workflow
- Inventory management
- Payment handling
- Report generation

## Future Enhancements
- Add graphical user interface.
- Convert the project into a web application.
- Add admin and customer roles.
- Add product images.
- Add email notifications.
- Add online payment gateway.
- Add invoice generation.
- Add search filters and sorting.
- Add cloud database support.

##Author
Surada Swetha Madhu — [GitHub](https://github.com/swetha9125)
