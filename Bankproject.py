import random
import re
import datetime
import pytz
import geocoder

class User:
    def __init__(self, name, last_name, email, telephone, usersId, password, balance=0, dateOfLogin=None, location=None):
        self.name = name
        self.last_name = last_name
        self.email = email
        self.telephone = telephone
        self.usersId = usersId
        self.password = password
        self.balance = float(balance)
        self.dateOfLogin = dateOfLogin
        self.location = location

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited {amount} PLN. Your new balance is {self.balance} PLN.")
        update_user_balance_in_file(self)

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient funds.")
        else:
            self.balance -= amount
            print(f"Withdrawn {amount} PLN. Your new balance is {self.balance} PLN.")
            update_user_balance_in_file(self)

    def transfer(self, recipient, amount):
        if amount > self.balance:
            print("Insufficient funds.")
        else:
            recipient.balance += amount
            self.balance -= amount
            print(f"Transferred {amount} PLN to {recipient.name}. Your new balance is {self.balance} PLN.")
            update_user_balance_in_file(self)
            update_user_balance_in_file(recipient)

def get_user_balance_from_file(usersId):
    with open(".venv/users.txt", "r") as file:
        for line in file:
            if usersId in line:
                user_data = line.strip().split(", ")
                balance = float(user_data[-1].split(":")[-1].strip())  # Correctly read balance as float
                return balance
    return 0

def save_user(user):
    with open(".venv/users.txt", "a") as file:
        file.write(f"Name: {user.name}, Last Name: {user.last_name}, Email: {user.email}, Telephone: {user.telephone}, UserId: {user.usersId}, Password: {user.password}, Balance: {user.balance}\n")

def login(usersId, password):
    logged = False
    with open(".venv/users.txt", "r") as file:
        for line in file:
            if usersId in line:
                user_data = line.strip().split(", ")
                existing_usersId = user_data[4].split(":")[-1].strip()
                existing_password = user_data[5].split(":")[-1].strip()
                if password == existing_password:
                    print("Login successful!")
                    try:
                        balance = float(user_data[-1].split(":")[-1].strip())  # Correctly read balance as float
                    except IndexError:
                        print("User data incomplete. Unable to retrieve balance.")
                        break

                    date_of_login = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
                    location = get_user_location()

                    logged_user = User(name=user_data[0].split(":")[-1].strip(),
                                       last_name=user_data[1].split(":")[-1].strip(),
                                       email=user_data[2].split(":")[-1].strip(),
                                       telephone=user_data[3].split(":")[-1].strip(),
                                       usersId=existing_usersId,
                                       password=existing_password,
                                       balance=balance,
                                       dateOfLogin=date_of_login,
                                       location=location)
                    logged = True
                    UsersAccount(logged_user)
                    break
    if not logged:
        print("Invalid client number or password.")

def UsersAccount(user):
    print(f"Logged in as {user.name}, User ID: {user.usersId}, Balance: {user.balance} PLN, Logged in at: {user.dateOfLogin}, Location: {user.location}")
    print("1. Deposit")
    print("2. Withdraw")
    print("3. Transfer")
    print("4. Exit")
    choice = input("Enter your choice: ")

    if choice == "1":
        amount = float(input("Enter the amount to deposit: "))
        user.deposit(amount)
    elif choice == "4":
        return
    elif choice == "2":
        amount = float(input("Enter the amount to withdraw: "))
        user.withdraw(amount)
    elif choice == "3":
        recipient_id = input("Enter the recipient's User ID: ")
        amount = float(input("Enter the amount to transfer: "))
        recipient = find_user_by_id(recipient_id)
        if recipient:
            user.transfer(recipient, amount)
        else:
            print("Recipient with provided User ID not found.")
    else:
        print("Invalid choice.")

def find_user_by_id(usersId):
    with open(".venv/users.txt", "r") as file:
        for line in file:
            if usersId in line:
                user_data = line.strip().split(", ")
                return User(*[info.split(":")[-1].strip() for info in user_data])
    return None

def get_user_location():
    g = geocoder.ip('me')
    return g.city

def update_user_balance_in_file(user):
    updated_line = None
    with open(".venv/users.txt", "r") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if user.usersId in line:
            user_data = line.strip().split(", ")
            user_data[-1] = f"Balance: {user.balance}"
            updated_line = ", ".join(user_data)
            lines[i] = updated_line + "\n"
            break
    if updated_line:
        with open(".venv/users.txt", "w") as file:
            file.writelines(lines)

users_choice = int(input("Sign up press 1/Log in press 2 to continue: "))
if users_choice == 1:
    name = input("What is your name? ")
    last_name = input("What is your last name? ")
    email = input("What is your email? ")
    telephone = input("What is your telephone number? ")
    password = input("What is your password? ")

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Invalid email format.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    usersId = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    print(f"Your client number is {usersId}, remember to write it down!")

    user = User(name, last_name, email, telephone, usersId, password)
    save_user(user)
    print("User successfully created and saved.")

elif users_choice == 2:
    usersId = input("Enter the client number:")
    password = input("Enter your password: ")
    login(usersId, password)

else:
    print("Invalid choice.")
