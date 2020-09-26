import sqlite3
from random import randint

# database setup
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()


def db_create():
    cur.execute("DROP TABLE IF EXISTS card;")
    cur.execute(
        """CREATE TABLE card (
            id integer PRIMARY KEY,
            number TEXT NOT NULL,
            pin TEXT NOT NULL,
            balance integer DEFAULT 0
            );""")
    conn.commit()


# init menu functions
def luhn_check(card):
    control = [int(i) for i in card[:-1]]
    odd_list, even_list = [], []
    for _ in control:
        odd_list = sum([(i * 2) - 9 if i * 2 > 9 else i * 2 for i in control[0::2]])
        even_list = sum([i for i in control[1::2]])
    control = even_list + odd_list

    if (control + int(card[-1])) % 10 == 0:
        return True
    else:
        return False


def create_account():
    user_card = ""

    # creating first 15 digits of card
    while len(user_card) < 15:
        user_card = "400000" + str(randint(000000000, 999999999))

    control = [int(i) for i in user_card]
    odd_list, even_list = [], []
    for _ in control:
        odd_list = sum([(i * 2) - 9 if i * 2 > 9 else i * 2 for i in control[0::2]])
        even_list = sum([i for i in control[1::2]])
    control = even_list + odd_list

    # checksum
    for i in range(0, 10):
        if (control + i) % 10 == 0:
            user_card += str(i)

    # PIN
    user_pin = str(randint(1000, 9999))

    # adding account to database
    sqlite3.connect("card.s3db")
    cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (user_card, user_pin))
    conn.commit()

    print("""\nYour card has been created\nYour card number:\n{}\nYour card PIN:\n{}\n"""
          .format(user_card, user_pin))


def login_screen():
    user_info = [input("Enter your card number: \n"), input("Enter your PIN: \n")]

    # validate!
    cur.execute("SELECT id FROM card WHERE number = ? and pin = ?", (user_info[0], user_info[1]))
    conn.commit()

    user_id = cur.fetchone() or 0

    if user_id == 0:
        print("\nWrong card number or PIN!\n")
    else:
        print("\nYou have successfully logged in!\n")
        main_menu(user_id[0])


def init_menu():
    while True:
        n = int(input("1. Create an account\n2. Log into account\n0. Exit\n"))
        if n in range(0, 3):
            if n == 1:
                create_account()
            elif n == 2:
                login_screen()
            else:
                print("\nBye!\n")
                exit()
        else:
            print("\nPlease enter a number between 0 and 2.\n")


# account-specific functions (requires user_id)
def balance(user_id):
    cur.execute("SELECT balance FROM card WHERE id = ?", (user_id,))
    amount = cur.fetchone()[0]
    conn.commit()

    if amount < 0:
        print("\nBalance: $\033[31m{}.00\033[00m\n".format(amount))  # *makes vomit noise*
    else:
        print("\nBalance: ${}.00\n".format(amount))


def income(user_id):
    amount = int(input("\nEnter income: \n"))
    cur.execute("UPDATE card SET balance = balance + ? WHERE id = ?;", (amount, user_id,))
    conn.commit()
    print("\nIncome was added!\n")


def transfer(user_id):
    recipient = input("\nEnter card number: \n")

    cur.execute("SELECT number FROM card where number = ?;", (recipient,))
    match = cur.fetchone() or "0"
    conn.commit()

    if recipient == match[0]:
        pass
    else:
        if luhn_check(recipient) is False:
            print("Probably you made a mistake in the card number. Please try again!\n")
            return
        else:
            print("Such a card does not exist.\n")
            print(cur.fetchone())
            return

    amount = int(input("\nEnter how much money you want to transfer: \n"))

    cur.execute("SELECT balance FROM card WHERE id = ?;", (user_id,))  # check validity of card
    conn.commit()

    if cur.fetchone()[0] > amount:
        cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (amount, recipient,))
        cur.execute("UPDATE card SET balance = balance - ? WHERE id = ?;", (amount, user_id,))
        conn.commit()
        print("\nSuccess!\n")
    else:
        print("\nNot enough money!\n")


def close_account(user_id):
    cur.execute("DELETE FROM card WHERE id = ?;", (user_id,))
    conn.commit()

    print("\nThe account has been closed!\n")


def main_menu(user_id):
    while True:
        n = int(input("1. Balance\n2. Add income\n3. Make a transfer\n4. Close account\n5. Log Out\n0. Exit\n"))
        if n in range(0, 6):
            if n == 1:
                balance(user_id)
            elif n == 2:
                income(user_id)
            elif n == 3:
                transfer(user_id)
            elif n == 4:
                close_account(user_id)
                return
            elif n == 5:
                print("\nYou have successfully logged out!\n")
                return
            else:
                print("\nBye!\n")
                exit()
        else:
            print("\nPlease enter a number between 0 and 2.\n")


if __name__ == "__main__":
    db_create()
    init_menu()
