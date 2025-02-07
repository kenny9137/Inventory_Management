import sqlite3


# Function to create a database connection and cursor
def create_connection():
    connection = sqlite3.connect("user_data.db")  # Connect to SQLite database (or create it if it doesn't exist)
    return connection, connection.cursor()


# Function to create the table (if it doesn't exist)
def create_table(cur):
    query = """
    CREATE TABLE IF NOT EXISTS users_db (
        Username TEXT PRIMARY KEY,
        Password TEXT NOT NULL
    );
    """
    cur.execute(query)


# Function for user registration
def register(cur, connection):
    print("Registration")
    userName = input("Enter username: ")

    # Check if the username already exists
    q = "SELECT COUNT(*) FROM users_db WHERE Username = ?"
    cur.execute(q, (userName,))
    a = cur.fetchone()
    if a[0] > 0:
        print("Username exists! Try another one.")
        return

    Password = input("Enter password: ")

    # Insert new user into the database
    q2 = "INSERT INTO users_db (Username, Password) VALUES (?, ?)"
    cur.execute(q2, (userName, Password))
    connection.commit()
    print("You registered successfully!")


# Function for user login
def login(cur):
    print("LOGIN")
    userName = input("Enter username: ")

    # Check if the username exists
    q = "SELECT Password FROM users_db WHERE Username = ?"
    cur.execute(q, (userName,))
    a = cur.fetchone()
    if a is None:
        print("Username not found! Kindly register!!")
        return

    Password = input("Enter password: ")
    if a[0] == Password:
        print("Login successful!")
    else:
        print("Invalid password. Try again!")


# Function to display all users (for debugging purposes)
def display(cur):
    q = "SELECT * FROM users_db"
    cur.execute(q)
    result = cur.fetchall()
    for i in result:
        print(i)


def main():
    connection, cur = create_connection()  # Create the connection and cursor

    # Create the table (if it doesn't exist)
    create_table(cur)

    while True:
        print("\n1. Register\n2. Login\n3. Display Users\n4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            register(cur, connection)
        elif choice == "2":
            login(cur)
        elif choice == "3":
            display(cur)  # Display all users (for debugging)
        elif choice == "4":
            print("Exiting system. Goodbye!")
            connection.close()  # Close the connection before exiting
            break
        else:
            print("Invalid choice. Kindly select a valid option.")


if __name__ == "__main__":
    main()
