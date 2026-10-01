import mysql.connector
import hashlib


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dellhell99",
    database="bank"
)

cursor = connection.cursor()

print("\n======================================")
print("       PYTHON BANKING SYSTEM")
print("======================================")


# ============================================================
# HASH PIN
# ============================================================

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


# ============================================================
# CREATE ACCOUNT
# ============================================================

def create_account():

    print("\n========== CREATE ACCOUNT ==========")

    name = input("Enter customer name: ")

    phone = input("Enter phone number: ")

    print("\n1. Savings")
    print("2. Current")

    choice = input("Enter account type: ")

    if choice == "1":
        account_type = "Savings"

    elif choice == "2":
        account_type = "Current"

    else:
        print("Invalid account type!")
        return

    pin = input("Create 4-digit PIN: ")

    if len(pin) != 4 or not pin.isdigit():
        print("PIN must be exactly 4 digits.")
        return

    opening_balance = float(
        input("Enter opening balance: ")
    )

    if opening_balance < 0:
        print("Balance cannot be negative.")
        return

    pin_hash = hash_pin(pin)

    try:

        query = """
        INSERT INTO accounts
        (customer_name, account_type, balance, pin_hash, phone)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            name,
            account_type,
            opening_balance,
            pin_hash,
            phone
        )

        cursor.execute(query, values)

        connection.commit()

        account_number = cursor.lastrowid

        print("\n======================================")
        print("       ACCOUNT CREATED SUCCESSFULLY")
        print("======================================")
        print("Account Number :", account_number)
        print("Customer Name  :", name)
        print("Account Type   :", account_type)
        print("Balance        :", opening_balance)
        print("======================================")

        # Add opening balance as transaction
        if opening_balance > 0:

            transaction_query = """
            INSERT INTO transactions
            (account_number, transaction_type, amount)
            VALUES (%s, %s, %s)
            """

            cursor.execute(
                transaction_query,
                (
                    account_number,
                    "Deposit",
                    opening_balance
                )
            )

            connection.commit()

    except mysql.connector.Error as e:

        connection.rollback()

        print("Database Error:", e)


# ============================================================
# LOGIN
# ============================================================

def login():

    print("\n========== LOGIN ==========")

    account_number = input("Enter account number: ")

    pin = input("Enter PIN: ")

    pin_hash = hash_pin(pin)

    query = """
    SELECT account_number,
           customer_name,
           account_type,
           balance
    FROM accounts
    WHERE account_number = %s
    AND pin_hash = %s
    """

    cursor.execute(
        query,
        (account_number, pin_hash)
    )

    account = cursor.fetchone()

    if account is None:

        print("\nInvalid account number or PIN.")
        return None

    print("\n======================================")
    print("          LOGIN SUCCESSFUL")
    print("======================================")
    print("Welcome,", account[1])
    print("======================================")

    return account


# ============================================================
# CHECK BALANCE
# ============================================================

def check_balance(account_number):

    print("\n========== CHECK BALANCE ==========")

    query = """
    SELECT customer_name,
           account_type,
           balance
    FROM accounts
    WHERE account_number = %s
    """

    cursor.execute(
        query,
        (account_number,)
    )

    result = cursor.fetchone()

    if result is None:

        print("Account not found!")
        return

    print("----------------------------------")
    print("Customer Name :", result[0])
    print("Account Type  :", result[1])
    print("Current Balance:", result[2])
    print("----------------------------------")


# ============================================================
# DEPOSIT
# ============================================================

def deposit_money(account_number):

    print("\n========== DEPOSIT MONEY ==========")

    try:

        amount = float(
            input("Enter amount to deposit: ")
        )

    except ValueError:

        print("Please enter a valid number.")
        return

    if amount <= 0:

        print("Amount must be greater than 0.")
        return

    try:

        # Update balance
        query = """
        UPDATE accounts
        SET balance = balance + %s
        WHERE account_number = %s
        """

        cursor.execute(
            query,
            (amount, account_number)
        )

        # Add transaction
        transaction_query = """
        INSERT INTO transactions
        (account_number, transaction_type, amount)
        VALUES (%s, %s, %s)
        """

        cursor.execute(
            transaction_query,
            (
                account_number,
                "Deposit",
                amount
            )
        )

        connection.commit()

        print("\nDeposit successful!")
        print("Deposited:", amount)

        check_balance(account_number)

    except mysql.connector.Error as e:

        connection.rollback()

        print("Database Error:", e)


# ============================================================
# WITHDRAW
# ============================================================

def withdraw_money(account_number):

    print("\n========== WITHDRAW MONEY ==========")

    try:

        amount = float(
            input("Enter amount to withdraw: ")
        )

    except ValueError:

        print("Please enter a valid number.")
        return

    if amount <= 0:

        print("Amount must be greater than 0.")
        return

    # Get current balance
    query = """
    SELECT balance
    FROM accounts
    WHERE account_number = %s
    """

    cursor.execute(
        query,
        (account_number,)
    )

    result = cursor.fetchone()

    if result is None:

        print("Account not found!")
        return

    balance = result[0]

    print("Available balance:", balance)

    if amount > balance:

        print("\nTransaction rejected!")
        print("Insufficient balance.")
        return

    try:

        # Deduct money
        update_query = """
        UPDATE accounts
        SET balance = balance - %s
        WHERE account_number = %s
        """

        cursor.execute(
            update_query,
            (amount, account_number)
        )

        # Add transaction
        transaction_query = """
        INSERT INTO transactions
        (account_number, transaction_type, amount)
        VALUES (%s, %s, %s)
        """

        cursor.execute(
            transaction_query,
            (
                account_number,
                "Withdrawal",
                amount
            )
        )

        connection.commit()

        print("\nWithdrawal successful!")
        print("Withdrawn:", amount)

        check_balance(account_number)

    except mysql.connector.Error as e:

        connection.rollback()

        print("Database Error:", e)


# ============================================================
# MINI STATEMENT
# ============================================================

def mini_statement(account_number):

    print("\n")
    print("==============================================")
    print("               MINI STATEMENT")
    print("==============================================")

    query = """
    SELECT transaction_id,
           transaction_type,
           amount,
           timestamp
    FROM transactions
    WHERE account_number = %s
    ORDER BY timestamp DESC
    """

    cursor.execute(
        query,
        (account_number,)
    )

    rows = cursor.fetchall()

    print("DEBUG: Number of transactions =", len(rows))

    if len(rows) == 0:

        print("\nNo transactions found.")

        return

    print("----------------------------------------------")
    print("ID    TYPE          AMOUNT       DATE")
    print("----------------------------------------------")

    for row in rows:

        print(
            row[0],
            row[1],
            row[2],
            row[3]
        )

    print("----------------------------------------------")


# ============================================================
# CHANGE PIN
# ============================================================

def change_pin(account_number):

    print("\n========== CHANGE PIN ==========")

    old_pin = input("Enter old PIN: ")

    old_hash = hash_pin(old_pin)

    query = """
    SELECT account_number
    FROM accounts
    WHERE account_number = %s
    AND pin_hash = %s
    """

    cursor.execute(
        query,
        (account_number, old_hash)
    )

    result = cursor.fetchone()

    if result is None:

        print("Incorrect old PIN.")
        return

    new_pin = input("Enter new 4-digit PIN: ")

    if len(new_pin) != 4 or not new_pin.isdigit():

        print("PIN must be exactly 4 digits.")
        return

    new_hash = hash_pin(new_pin)

    update_query = """
    UPDATE accounts
    SET pin_hash = %s
    WHERE account_number = %s
    """

    cursor.execute(
        update_query,
        (new_hash, account_number)
    )

    connection.commit()

    print("PIN changed successfully!")


# ============================================================
# ACCOUNT MENU
# ============================================================

def account_menu(account):

    # VERY IMPORTANT
    # account comes from login()

    account_number = account[0]
    customer_name = account[1]

    print("\nDEBUG ACCOUNT NUMBER =", account_number)

    while True:

        print("\n")
        print("======================================")
        print("              BANK MENU")
        print("======================================")
        print("Welcome,", customer_name)
        print("--------------------------------------")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Mini Statement")
        print("5. Change PIN")
        print("6. Logout")
        print("--------------------------------------")

        choice = input("ENTER YOUR CHOICE: ").strip()

        print("DEBUG: YOU SELECTED =", choice)

        # ----------------------------------
        # CHECK BALANCE
        # ----------------------------------

        if choice == "1":

            check_balance(account_number)

            input("\nPress ENTER to return to menu...")

        # ----------------------------------
        # DEPOSIT
        # ----------------------------------

        elif choice == "2":

            deposit_money(account_number)

            input("\nPress ENTER to return to menu...")

        # ----------------------------------
        # WITHDRAW
        # ----------------------------------

        elif choice == "3":

            withdraw_money(account_number)

            input("\nPress ENTER to return to menu...")

        # ----------------------------------
        # MINI STATEMENT
        # ----------------------------------

        elif choice == "4":

            mini_statement(account_number)

            input("\nPress ENTER to return to menu...")

        # ----------------------------------
        # CHANGE PIN
        # ----------------------------------

        elif choice == "5":

            change_pin(account_number)

            input("\nPress ENTER to return to menu...")

        # ----------------------------------
        # LOGOUT
        # ----------------------------------

        elif choice == "6":

            print("\nLogged out successfully.")

            break

        else:

            print("\nINVALID CHOICE!")

            input("\nPress ENTER to try again...")


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        print("\n")
        print("======================================")
        print("        PYTHON BANKING SYSTEM")
        print("======================================")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        print("======================================")

        choice = input("ENTER YOUR CHOICE: ").strip()

        print("DEBUG MAIN CHOICE =", choice)

        if choice == "1":

            create_account()

        elif choice == "2":

            account = login()

            if account is not None:

                account_menu(account)

        elif choice == "3":

            print("\nThank you for using Python Bank!")

            break

        else:

            print("\nInvalid choice!")


# ============================================================
# START PROGRAM
# ============================================================

try:

    main()

except mysql.connector.Error as e:

    print("\nDATABASE ERROR:", e)

except Exception as e:

    print("\nPROGRAM ERROR:", e)

finally:

    cursor.close()
    connection.close()

    print("\nDatabase connection closed.")
    