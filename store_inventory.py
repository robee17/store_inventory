import mysql.connector
from mysql.connector import Error


# 1. DATABASE CONNECTION
# ---------------------------------------------------------------
def connect_db():
    """Connect to MySQL. Change user/password to match your computer."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",              # <-- put your MySQL password here
            database="store_inventory_db"
        )
        return conn
    except Error as e:
        print("Cannot connect to database:", e)
        return None


# 2. INPUT HELPERS (validation)
# ---------------------------------------------------------------
def get_text(prompt):
    """Keep asking until the user types something (not empty)."""
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("Input cannot be empty. Try again.")


def get_quantity(prompt):
    """Keep asking until the user types a whole number (0 or more)."""
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("Please enter a valid whole number.")


def get_price(prompt):
    """Keep asking until the user types a valid price greater than 0."""
    while True:
        value = input(prompt).strip()
        try:
            price = float(value)
            if price > 0:
                return price
            print("Price must be greater than 0.")
        except ValueError:
            print("Please enter a valid price (example: 25.50).")


def get_gender():
    """Only allow Male, Female, or Unisex."""
    while True:
        value = input("Gender (1 = Male, 2 = Female, 3 = Unisex): ").strip()
        if value == "1":
            return "Male"
        if value == "2":
            return "Female"
        if value == "3":
            return "Unisex"
        print("Please type 1, 2, or 3.")


def find_product(cursor, product_id):
    """Return the product record if the ID exists, otherwise None."""
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    return cursor.fetchone()


# 3. CRUD FUNCTIONS
# Column order in the table:
# row[0]=id, row[1]=name, row[2]=category, row[3]=model_number,
# row[4]=size, row[5]=gender, row[6]=price, row[7]=quantity
# ---------------------------------------------------------------
def add_product(conn):
    """CREATE - add a new product."""
    print("\n--- Add New Product ---")
    product_name = get_text("Product name: ")
    category = get_text("Category: ")
    model_number = get_text("Model number: ").upper()
    size = get_text("Size (S, M, L, 38, 42, etc.): ").upper()
    gender = get_gender()
    price = get_price("Price (PHP): ")
    quantity = get_quantity("Quantity in stock: ")

    try:
        cursor = conn.cursor()
        sql = """INSERT INTO products
                 (product_name, category, model_number, size, gender, price, quantity)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (product_name, category, model_number, size, gender, price, quantity))
        conn.commit()
        print("Product added successfully!")
    except Error as e:
        if e.errno == 1062:   # 1062 = duplicate (same model number + size + gender)
            print("Error: That model with the same size and gender already exists.")
        else:
            print("Error adding product:", e)


def view_products(conn):
    """READ - display all products."""
    print("\n--- All Products ---")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()

        if len(rows) == 0:
            print("No products found.")
            return

        print(f"{'ID':<5}{'Product':<22}{'Category':<12}{'Model No.':<12}"
              f"{'Size':<7}{'Gender':<9}{'Price':<10}{'Stock'}")
        print("-" * 85)
        for row in rows:
            print(f"{row[0]:<5}{row[1]:<22}{row[2]:<12}{row[3]:<12}"
                  f"{row[4]:<7}{row[5]:<9}{float(row[6]):<10.2f}{row[7]}")
    except Error as e:
        print("Error reading products:", e)


def update_product(conn):
    """UPDATE - change a product's details. Press Enter to keep the old value."""
    print("\n--- Update Product ---")
    view_products(conn)
    product_id = get_quantity("\nEnter the product ID to update: ")

    try:
        cursor = conn.cursor()
        old = find_product(cursor, product_id)
        if old is None:
            print("No product found with that ID.")
            return

        print("(Press Enter to keep the current value)")
        product_name = input(f"Product name [{old[1]}]: ").strip() or old[1]
        category = input(f"Category [{old[2]}]: ").strip() or old[2]
        model_number = input(f"Model number [{old[3]}]: ").strip().upper() or old[3]
        size = input(f"Size [{old[4]}]: ").strip().upper() or old[4]

        gender_input = input(f"Gender [{old[5]}] (1 = Male, 2 = Female, 3 = Unisex): ").strip()
        if gender_input == "":
            gender = old[5]
        elif gender_input == "1":
            gender = "Male"
        elif gender_input == "2":
            gender = "Female"
        elif gender_input == "3":
            gender = "Unisex"
        else:
            print("Invalid gender. Update cancelled.")
            return

        price_input = input(f"Price [{float(old[6]):.2f}]: ").strip()
        if price_input == "":
            price = old[6]
        else:
            try:
                price = float(price_input)
                if price <= 0:
                    print("Price must be greater than 0. Update cancelled.")
                    return
            except ValueError:
                print("Invalid price. Update cancelled.")
                return

        qty_input = input(f"Quantity [{old[7]}]: ").strip()
        if qty_input == "":
            quantity = old[7]
        elif qty_input.isdigit():
            quantity = int(qty_input)
        else:
            print("Invalid quantity. Update cancelled.")
            return

        sql = """UPDATE products
                 SET product_name = %s, category = %s, model_number = %s,
                     size = %s, gender = %s, price = %s, quantity = %s
                 WHERE product_id = %s"""
        cursor.execute(sql, (product_name, category, model_number, size,
                             gender, price, quantity, product_id))
        conn.commit()
        print("Product updated successfully!")
    except Error as e:
        if e.errno == 1062:
            print("Error: That model with the same size and gender already exists.")
        else:
            print("Error updating product:", e)


def delete_product(conn):
    """DELETE - remove a product after confirmation."""
    print("\n--- Delete Product ---")
    view_products(conn)
    product_id = get_quantity("\nEnter the product ID to delete: ")

    try:
        cursor = conn.cursor()
        if find_product(cursor, product_id) is None:
            print("No product found with that ID.")
            return

        confirm = input("Are you sure you want to delete? (y/n): ").strip().lower()
        if confirm == "y":
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            conn.commit()
            print("Product deleted successfully!")
        else:
            print("Delete cancelled.")
    except Error as e:
        print("Error deleting product:", e)


# 4. MENU AND MAIN PROGRAM
# ---------------------------------------------------------------
def show_menu():
    print("\n===== STORE INVENTORY SYSTEM =====")
    print("1. Add Product (Create)")
    print("2. View Products (Read)")
    print("3. Update Product (Update)")
    print("4. Delete Product (Delete)")
    print("5. Exit")


def main():
    conn = connect_db()
    if conn is None:
        return  # stop the program if connection failed

    while True:
        show_menu()
        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            add_product(conn)
        elif choice == "2":
            view_products(conn)
        elif choice == "3":
            update_product(conn)
        elif choice == "4":
            delete_product(conn)
        elif choice == "5":
            conn.close()
            print("Database connection closed. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1 to 5.")


main()