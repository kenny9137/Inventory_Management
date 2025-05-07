import sqlite3
from datetime import datetime


def create_connection():
    connection = sqlite3.connect("inventory.db")
    return connection, connection.cursor()
#new addiion just checking

def create_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'staff')) NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        low_stock_alert INTEGER DEFAULT 5
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        type TEXT CHECK(type IN ('sale', 'purchase')) NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)


def register(cur, connection):
    print("\n--- Register New User ---")
    username = input("Enter username: ")
    role = input("Enter role (admin/staff): ").lower()

    if role not in ("admin", "staff"):
        print("Invalid role! Choose either 'admin' or 'staff'.")
        return

    cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    if cur.fetchone()[0] > 0:
        print("Username already exists! Try another.")
        return

    password = input("Enter password: ")
    cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    connection.commit()
    print("User registered successfully!")


def login(cur):
    print("\n--- Login ---")
    username = input("Enter username: ")
    password = input("Enter password: ")

    cur.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if user and user[0] == password:  # Plain text password check
        print(f"Login successful! Welcome {username} ({user[1]})")
        return user[1]  # Return user role
    else:
        print("Invalid username or password.")
        return None


def add_product(cur, connection):
    print("\n--- Add Product ---")
    name = input("Product Name: ")
    description = input("Description: ")
    price = float(input("Price: "))
    stock = int(input("Initial Stock: "))
    low_stock_alert = int(input("Low Stock Alert Level: "))

    cur.execute("INSERT INTO products (name, description, price, stock, low_stock_alert) VALUES (?, ?, ?, ?, ?)",
                (name, description, price, stock, low_stock_alert))
    connection.commit()
    print("✅ Product added successfully!")


def view_inventory(cur):
    print("\n--- Inventory List ---")
    cur.execute("SELECT * FROM products")
    items = cur.fetchall()

    for item in items:
        stock_status = "⚠ LOW STOCK" if item[4] <= item[5] else "✔ Sufficient"
        print(f"ID: {item[0]}, Name: {item[1]}, Price: ${item[3]}, Stock: {item[4]} ({stock_status})")


def update_product(cur, connection):
    print("\n--- Update Product ---")
    product_id = input("Enter Product ID to update: ")

    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cur.fetchone()

    if not product:
        print("❌ Product not found!")
        return

    new_name = input(f"New name (leave blank to keep '{product[1]}'): ") or product[1]
    new_description = input(f"New description (leave blank to keep '{product[2]}'): ") or product[2]
    new_price = input(f"New price (leave blank to keep '{product[3]}'): ") or product[3]
    new_stock = input(f"New stock quantity (leave blank to keep '{product[4]}'): ") or product[4]
    new_alert = input(f"New low stock alert (leave blank to keep '{product[5]}'): ") or product[5]

    cur.execute("""
        UPDATE products 
        SET name = ?, description = ?, price = ?, stock = ?, low_stock_alert = ?
        WHERE id = ?
    """, (new_name, new_description, new_price, new_stock, new_alert, product_id))

    connection.commit()
    print("✅ Product updated successfully!")


def delete_product(cur, connection):
    print("\n--- Delete Product ---")
    product_id = input("Enter Product ID to delete: ")

    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cur.fetchone()

    if not product:
        print("❌ Product not found!")
        return

    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()

    # Reset Auto-Increment for product IDs
    cur.execute("DELETE FROM sqlite_sequence WHERE name='products'")
    connection.commit()

    print("✅ Product deleted successfully, and ID sequence reset!")


def record_transaction(cur, connection, transaction_type):
    print(f"\n--- Record {transaction_type.capitalize()} ---")
    try:
        product_id = int(input("Enter Product ID: "))
        quantity = int(input("Enter Quantity: "))

        # Fetch product details (price & stock)
        cur.execute("SELECT price, stock FROM products WHERE id = ?", (product_id,))
        product = cur.fetchone()

        if not product:
            print("❌ Invalid Product ID!")
            return

        price, stock = product  # Correct indexing
        total_price = price * quantity

        # Check stock availability for sales
        if transaction_type == "sale" and stock < quantity:
            print("❌ Not enough stock available!")
            return

        # Insert transaction
        cur.execute("INSERT INTO transactions (product_id, type, quantity, total_price) VALUES (?, ?, ?, ?)",
                    (product_id, transaction_type, quantity, total_price))

        # Update stock
        new_stock = stock - quantity if transaction_type == "sale" else stock + quantity
        cur.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))

        connection.commit()
        print(f"✅ {transaction_type.capitalize()} recorded successfully!")

    except ValueError:
        print("❌ Invalid input! Please enter a number.")


def generate_report(cur):
    print("\n--- Sales Report ---")
    cur.execute("SELECT type, SUM(quantity), SUM(total_price) FROM transactions GROUP BY type")
    results = cur.fetchall()

    for row in results:
        print(f"Type: {row[0].capitalize()}, Total Quantity: {row[1]}, Total Amount: ${row[2]}")


def main():
    connection, cur = create_connection()
    create_tables(cur)

    role = None
    while not role:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            register(cur, connection)
        elif choice == "2":
            role = login(cur)
        elif choice == "3":
            print("Goodbye!")
            connection.close()
            break

    while role:
        if role == "admin":
            print("\n1. Add Product\n2. View Inventory\n3. Update Product\n4. Delete Product")
            print("5. Record Sale\n6. Record Purchase\n7. Generate Report\n8. Logout")
        else:
            print("\n1. Add Product\n2. View Inventory\n3. Update Product\n8. Logout")


        choice = input("Choose an option: ")

        if choice == "1" and role == "admin":
            add_product(cur, connection)
        elif choice == "2":
            view_inventory(cur)
        elif choice == "3" and role == "admin":
            update_product(cur, connection)
        elif choice == "4" and role == "admin":
            delete_product(cur, connection)
        elif choice == "5":
            record_transaction(cur, connection, "sale")
        elif choice == "6":
            record_transaction(cur, connection, "purchase")
        elif choice == "7":
            generate_report(cur)
        elif choice == "8":
            print("Logging out...")
            role = None
        else:
            print("❌ Invalid option or insufficient privileges!")

    connection.close()


if __name__ == "__main__":
    main()
