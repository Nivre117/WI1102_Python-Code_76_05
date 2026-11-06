"""
==================================================================
  WI1102 COMPUTATIONAL THINKING - GROUP 5
  Project : Design and Implementation of an ATM Transaction
            Processing System in Python

  Members : 1. Muhammad Farish Haykal  (13526020)
            2. Nauval Rizki Zaidan     (13526033)
            3. Al Kindi Delvara        (13226024)
            4. Ervin Gustandi Putera   (13226040)
            5. Fakhri Dzaki Cahyono    (18026028)

  Date    : November 2026

  Description :
  This program is a simple ATM simulation. We made it based on the
  flowcharts in our presentation:
    - Flowchart 1 : Account creation
    - Flowchart 2 : ATM main flow (insert card, language, PIN, menu)
    - Balance inquiry and cash withdrawal
    - Interbank transfer
    - Mobile phone top up and electricity token
    - PDAM water bill payment and change PIN

  Since we don't have a real bank database, all the data is saved
  in dictionaries while the program is running.

  Important variables :
  accounts      : all accounts in our bank (key = card/account number)
  other_banks   : dummy accounts in other banks (for transfer)
  pdam_regions  : list of PDAM codes
  pdam_bills    : PDAM customers and their bills (billing database)
  account       : the account that is using the ATM right now
  attempts      : how many times the user typed a wrong PIN
  choice        : menu option picked by the user
  amount        : money used in a transaction
  admin_fee     : extra fee for payments
  total         : amount + admin_fee
==================================================================
"""

import random
import time
from datetime import datetime


bank_name = "CT BANK"

# minimum and maximum for transfer (per transaction)
min_transfer = 10000
max_transfer = 25000000


# ------------------------------------------------------------------
#  "DATABASE"
# ------------------------------------------------------------------

# accounts in our own bank
# there is already 1 account here so we can test transfer between CT Bank accounts
accounts = {
    "1029384756": {
        "number": "1029384756",
        "name": "Budi Santoso",
        "dob": "17/08/2005",
        "pin": "123456",
        "balance": 2500000,
        "blocked": False,
        "history": []
    }
}

# accounts in other banks (only used as transfer destination)
other_banks = {
    "BCA": {
        "5210887341": {"name": "Andi Wijaya", "balance": 1000000},
        "5210993412": {"name": "Rina Kusuma", "balance": 750000}
    },
    "BNI": {
        "0812345670": {"name": "Dewi Lestari", "balance": 1200000}
    },
    "BRI": {
        "3301000123": {"name": "Joko Prasetyo", "balance": 500000}
    },
    "Mandiri": {
        "1370011223": {"name": "Rizky Ramadhan", "balance": 3000000}
    },
    "BSI": {
        "7145566778": {"name": "Aisyah Putri", "balance": 900000}
    }
}

bank_list = ["CT BANK", "BCA", "BNI", "BRI", "Mandiri", "BSI"]

# PDAM code = first 2 digits of the customer number
pdam_regions = {
    "11": "PDAM Bandung City",
    "12": "PDAM Jakarta",
    "13": "PDAM Surabaya City",
    "14": "PDAM Bogor City",
    "15": "PDAM Makassar City"
}

# billing database for PDAM
pdam_bills = {
    "11004521": {"name": "Siti Rahmawati", "period": "October 2026", "usage": 18, "bill": 96500, "paid": False},
    "11007832": {"name": "Hendra Gunawan", "period": "October 2026", "usage": 25, "bill": 134000, "paid": False},
    "12000415": {"name": "Maya Anggraini", "period": "October 2026", "usage": 12, "bill": 71000, "paid": False},
    "13002290": {"name": "Agus Salim", "period": "October 2026", "usage": 30, "bill": 162500, "paid": True},
    "14005567": {"name": "Lina Marlina", "period": "October 2026", "usage": 9, "bill": 52000, "paid": False},
    "15001108": {"name": "Fajar Nugroho", "period": "October 2026", "usage": 21, "bill": 113000, "paid": False}
}


# ------------------------------------------------------------------
#  SMALL HELPER FUNCTIONS
# ------------------------------------------------------------------

def line():
    print("=" * 46)


def rupiah(number):
    # example: 1500000 -> Rp 1,500,000
    return "Rp " + "{:,}".format(number)


def loading(text):
    print(text, end="", flush=True)
    for i in range(3):
        time.sleep(0.4)
        print(".", end="", flush=True)
    print()


def ask_number(text):
    # keep asking until the user types a number
    while True:
        answer = input(text).strip()
        answer = answer.replace(",", "").replace(".", "")
        if answer.isdigit():
            return int(answer)
        print("Please enter numbers only.")


def ask_yes_no(text):
    while True:
        answer = input(text + " (y/n): ").strip().lower()
        if answer == "y" or answer == "yes":
            return True
        elif answer == "n" or answer == "no":
            return False
        else:
            print("Please type y or n.")


def pin_is_valid(pin):
    # PIN must be exactly 6 digits
    if len(pin) == 6 and pin.isdigit():
        return True
    else:
        return False


def dob_is_valid(dob):
    # very simple check for DD/MM/YYYY
    if len(dob) != 10:
        return False
    if dob[2] != "/" or dob[5] != "/":
        return False
    day = dob[0:2]
    month = dob[3:5]
    year = dob[6:10]
    if day.isdigit() == False or month.isdigit() == False or year.isdigit() == False:
        return False
    if int(day) < 1 or int(day) > 31:
        return False
    if int(month) < 1 or int(month) > 12:
        return False
    return True


def hide_number(number):
    # 1029384756 -> 102****756 (so the receipt doesn't show the full number)
    return number[:3] + "****" + number[-3:]


def save_history(account, text):
    time_now = datetime.now().strftime("%d/%m/%Y %H:%M")
    account["history"].append(time_now + " | " + text)


def print_receipt(title, details):
    time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print()
    loading("Printing receipt")
    print("*" * 46)
    print(bank_name.center(46))
    print(title.center(46))
    print("-" * 46)
    for d in details:
        print(" " + d)
    print(" Date/Time       : " + time_now)
    print("-" * 46)
    print("Please keep this receipt".center(46))
    print("*" * 46)


# ------------------------------------------------------------------
#  FLOWCHART 1 : ACCOUNT CREATION
# ------------------------------------------------------------------

def create_account():
    print()
    line()
    print("CREATE A NEW ACCOUNT".center(46))
    line()

    # input full name, date of birth, PIN, and initial balance
    while True:
        name = input("Full name                  : ").strip()
        dob = input("Date of birth (DD/MM/YYYY) : ").strip()
        pin = input("PIN (6 digits)             : ").strip()
        initial_balance = ask_number("Initial balance            : Rp ")

        if name == "":
            print("Name cannot be empty. Please fill in your data again.\n")
        elif dob_is_valid(dob) == False:
            print("Wrong date format, use DD/MM/YYYY. Please fill in your data again.\n")
        elif pin_is_valid(pin) == False:
            print("PIN must be 6 digits. Please fill in your data again.\n")
        elif initial_balance < 50000:
            print("Minimum initial balance is Rp 50,000. Please fill in your data again.\n")
        else:
            break

    # PIN confirmation
    while True:
        confirm_pin = input("Re-enter your PIN          : ").strip()
        if confirm_pin == pin:
            break
        else:
            print("PIN does not match. Try again.")

    # make a new account number that is not used yet
    new_number = str(random.randint(1000000000, 9999999999))
    while new_number in accounts:
        new_number = str(random.randint(1000000000, 9999999999))

    # save account data
    accounts[new_number] = {
        "number": new_number,
        "name": name,
        "dob": dob,
        "pin": pin,
        "balance": initial_balance,
        "blocked": False,
        "history": []
    }

    print()
    loading("Saving your data")
    print("Account created successfully!")
    print("Name                : " + name)
    print("Card/account number : " + new_number)
    print("Balance             : " + rupiah(initial_balance))
    print("Please remember your card number, you need it to use the ATM.")


# ------------------------------------------------------------------
#  FLOWCHART 2 : ATM MAIN FLOW
# ------------------------------------------------------------------

def choose_language():
    print()
    print("Select language:")
    print("1. Indonesian")
    print("2. English")
    while True:
        language = input("Choose (1/2): ").strip()
        if language == "1":
            print("Sorry, Indonesian is not available yet. The ATM will use English.")
            return "english"
        elif language == "2":
            return "english"
        else:
            print("Invalid option.")


def check_pin_login(account):
    attempts = 0
    while True:
        pin = input("Enter your PIN: ").strip()

        if pin == account["pin"]:
            print("PIN correct. Welcome, " + account["name"] + "!")
            return

        attempts = attempts + 1
        print("Incorrect PIN!")

        if attempts >= 3:
            # account recovery using full name and date of birth
            print()
            print("You entered a wrong PIN 3 times.")
            print("Please verify your data to recover your account.")
            while True:
                name = input("Full name                  : ").strip()
                dob = input("Date of birth (DD/MM/YYYY) : ").strip()
                if name.lower() == account["name"].lower() and dob == account["dob"]:
                    print("Data is valid. You can enter your PIN again.\n")
                    break
                else:
                    print("Recovery data is not valid. Please try again.\n")
            attempts = 0   # reset failed attempts


def show_main_menu():
    print()
    line()
    print("MAIN MENU".center(46))
    line()
    print("1. Balance Inquiry")
    print("2. Cash Withdrawal")
    print("3. Interbank Transfer")
    print("4. Payment / Purchase")
    print("5. Change PIN")
    print("6. End Transaction")
    line()


def atm_session():
    print()
    print("Please insert your ATM card.")
    card_number = input("Card number: ").strip()
    loading("Reading card")

    if card_number not in accounts:
        print("Card is not recognized. Please take your card.")
        return

    account = accounts[card_number]

    if account["blocked"] == True:
        print("This card is blocked. Please contact our customer service.")
        return

    choose_language()
    print()
    check_pin_login(account)

    while True:
        show_main_menu()
        choice = input("Input menu option (1-6): ").strip()

        if choice == "1":
            balance_inquiry(account)
        elif choice == "2":
            cash_withdrawal(account)
        elif choice == "3":
            transfer(account)
        elif choice == "4":
            payment_menu(account)
        elif choice == "5":
            change_pin(account)
        elif choice == "6":
            print("Transaction ended.")
            break
        else:
            print("Invalid option, please choose 1-6.")
            continue

        # if the card got blocked in change PIN, stop here
        if account["blocked"] == True:
            print("Your card is kept by the ATM. Please contact our customer service.")
            return

        print()
        if ask_yes_no("Continue to another transaction?") == False:
            print()
            print("Thank you for using " + bank_name + " ATM!")
            break

    print("Please take your card.")


# ------------------------------------------------------------------
#  BALANCE INQUIRY
# ------------------------------------------------------------------

def balance_inquiry(account):
    print()
    loading("Retrieving balance from database")

    # check if the data can be found in the database
    if account["number"] not in accounts:
        print("Error: failed to retrieve your account data.")
        return

    balance = accounts[account["number"]]["balance"]
    print("Your current balance: " + rupiah(balance))

    if ask_yes_no("Print receipt?"):
        print_receipt("BALANCE INQUIRY", [
            "Account         : " + hide_number(account["number"]),
            "Name            : " + account["name"],
            "Balance         : " + rupiah(balance)
        ])


# ------------------------------------------------------------------
#  CASH WITHDRAWAL
# ------------------------------------------------------------------

def cash_withdrawal(account):
    print()
    line()
    print("QUICK WITHDRAWAL".center(46))
    line()
    print("1. Rp 50,000         3. Rp 500,000")
    print("2. Rp 200,000        4. Rp 1,000,000")
    print("5. Other amount")
    option = input("Select withdrawal option: ").strip()

    if option == "1":
        amount = 50000
    elif option == "2":
        amount = 200000
    elif option == "3":
        amount = 500000
    elif option == "4":
        amount = 1000000
    elif option == "5":
        print("Amount must be a multiple of Rp 50,000 (max Rp 1,250,000)")
        amount = ask_number("Input withdrawal amount: Rp ")
        # check if the amount is valid
        if amount < 50000 or amount > 1250000 or amount % 50000 != 0:
            print("Invalid amount! Transaction failed.")
            return
    else:
        print("Invalid option! Transaction failed.")
        return

    if account["balance"] < amount:
        print("Insufficient balance! Transaction failed.")
        return

    loading("Processing")
    account["balance"] = account["balance"] - amount
    save_history(account, "Cash withdrawal " + rupiah(amount))

    print("Please take your cash.")
    print("Amount withdrawn  : " + rupiah(amount))
    print("Remaining balance : " + rupiah(account["balance"]))

    if ask_yes_no("Print receipt?"):
        print_receipt("CASH WITHDRAWAL", [
            "Account         : " + hide_number(account["number"]),
            "Amount          : " + rupiah(amount),
            "Balance         : " + rupiah(account["balance"])
        ])


# ------------------------------------------------------------------
#  INTERBANK TRANSFER
# ------------------------------------------------------------------

def transfer(account):
    print()
    line()
    print("TRANSFER".center(46))
    line()
    print("Bank list:")
    for i in range(len(bank_list)):
        print(str(i + 1) + ". " + bank_list[i])

    # select bank & account number, then look for it in the database
    while True:
        bank_choice = ask_number("Select bank (1-" + str(len(bank_list)) + "): ")
        if bank_choice < 1 or bank_choice > len(bank_list):
            print("Invalid bank option.")
            continue

        bank = bank_list[bank_choice - 1]
        destination = input("Destination account number: ").strip()
        loading("Searching account")

        recipient = None
        if bank == bank_name:
            if destination == account["number"]:
                print("You cannot transfer to your own account.")
                continue
            if destination in accounts:
                recipient = accounts[destination]
        else:
            if destination in other_banks[bank]:
                recipient = other_banks[bank][destination]

        if recipient != None:
            break
        else:
            print("Account not found! Please check the bank and account number.\n")

    print("Recipient name: " + recipient["name"])

    # enter transfer amount
    print("Transfer limit: " + rupiah(min_transfer) + " - " + rupiah(max_transfer))
    print("(type 0 to cancel)")
    while True:
        amount = ask_number("Enter transfer amount: Rp ")
        if amount == 0:
            print("Transfer cancelled.")
            return
        if amount < min_transfer or amount > max_transfer:
            print("Amount is outside the transfer limit. Try again.")
        elif amount > account["balance"]:
            print("Insufficient balance. Try again.")
        else:
            break

    # transfer summary
    print()
    print("------------- TRANSFER SUMMARY -------------")
    print("Destination bank : " + bank)
    print("Account number   : " + destination)
    print("Recipient name   : " + recipient["name"])
    print("Amount           : " + rupiah(amount))
    print("--------------------------------------------")

    if ask_yes_no("Confirm transfer?") == False:
        print("Transfer cancelled.")
        return

    # enter PIN again before the money is sent
    attempts = 0
    while True:
        pin = input("Enter your PIN to confirm: ").strip()
        if pin == account["pin"]:
            break
        attempts = attempts + 1
        print("Incorrect PIN!")
        if attempts >= 3:
            print("Wrong PIN 3 times. Transfer cancelled.")
            return

    loading("Processing transfer")

    # debit and credit accounts
    account["balance"] = account["balance"] - amount
    recipient["balance"] = recipient["balance"] + amount

    # save transaction log
    save_history(account, "Transfer " + rupiah(amount) + " to " + recipient["name"] + " (" + bank + ")")
    if "history" in recipient:
        save_history(recipient, "Received " + rupiah(amount) + " from " + account["name"])

    print("Transfer successful!")
    print("Remaining balance: " + rupiah(account["balance"]))

    if ask_yes_no("Print receipt?"):
        ref_number = str(random.randint(100000000, 999999999))
        print_receipt("TRANSFER", [
            "Ref. number     : " + ref_number,
            "From            : " + hide_number(account["number"]),
            "To bank         : " + bank,
            "To account      : " + destination,
            "Recipient       : " + recipient["name"],
            "Amount          : " + rupiah(amount),
            "Balance         : " + rupiah(account["balance"])
        ])


# ------------------------------------------------------------------
#  PAYMENT / PURCHASE
# ------------------------------------------------------------------

def payment_menu(account):
    print()
    line()
    print("PAYMENT / PURCHASE".center(46))
    line()
    print("1. Mobile phone top up")
    print("2. Electricity token")
    print("3. PDAM water bill")
    option = input("Choose payment type: ").strip()

    if option == "1":
        phone_topup(account)
    elif option == "2":
        electricity_token(account)
    elif option == "3":
        pdam_payment(account)
    else:
        print("Invalid option.")


def phone_topup(account):
    print()
    print("--- MOBILE PHONE TOP UP ---")

    # phone number must start with 08 and have 10-13 digits
    while True:
        phone = input("Enter the mobile phone number: ").strip()
        if phone.isdigit() and phone[:2] == "08" and len(phone) >= 10 and len(phone) <= 13:
            break
        print("Invalid phone number. Example: 081234567890")

    topup_list = [20000, 30000, 50000, 100000, 150000, 200000, 300000]

    print()
    print("Select top up amount:")
    print("1. Rp 20,000         5. Rp 150,000")
    print("2. Rp 30,000         6. Rp 200,000")
    print("3. Rp 50,000         7. Rp 300,000")
    print("4. Rp 100,000        8. Other amount")
    pick = ask_number("Your choice: ")

    if pick >= 1 and pick <= 7:
        amount = topup_list[pick - 1]
    elif pick == 8:
        while True:
            amount = ask_number("Enter custom amount (Rp 5,000 - Rp 1,000,000): Rp ")
            if amount >= 5000 and amount <= 1000000:
                break
            print("Amount is not allowed.")
    else:
        print("Invalid option. Transaction failed.")
        return

    # calculate total payment
    admin_fee = 1500
    total = amount + admin_fee

    if account["balance"] < total:
        print("Insufficient balance! Transaction failed.")
        return

    # payment confirmation
    print()
    print("---------- PAYMENT CONFIRMATION ----------")
    print("Phone number : " + phone)
    print("Top up       : " + rupiah(amount))
    print("Admin fee    : " + rupiah(admin_fee))
    print("Total        : " + rupiah(total))
    print("------------------------------------------")

    if ask_yes_no("Confirm payment?") == False:
        print("Transaction cancelled.")
        return

    loading("Processing")
    account["balance"] = account["balance"] - total
    save_history(account, "Phone top up " + rupiah(amount) + " to " + phone)
    print("Top up successful!")

    print_receipt("MOBILE PHONE TOP UP", [
        "Phone number    : " + phone,
        "Top up          : " + rupiah(amount),
        "Admin fee       : " + rupiah(admin_fee),
        "Total paid      : " + rupiah(total),
        "Balance         : " + rupiah(account["balance"])
    ])


def electricity_token(account):
    print()
    print("--- ELECTRICITY TOKEN ---")

    while True:
        meter = input("Enter electricity meter number (11 digits): ").strip()
        if meter.isdigit() and len(meter) == 11:
            break
        print("Meter number must be 11 digits.")

    token_list = [20000, 50000, 100000, 200000, 500000, 1000000, 5000000, 10000000]

    print()
    print("Select token amount:")
    print("1. Rp 20,000         5. Rp 500,000")
    print("2. Rp 50,000         6. Rp 1,000,000")
    print("3. Rp 100,000        7. Rp 5,000,000")
    print("4. Rp 200,000        8. Rp 10,000,000")
    pick = ask_number("Your choice: ")

    if pick < 1 or pick > 8:
        print("Invalid option. Transaction failed.")
        return

    amount = token_list[pick - 1]
    admin_fee = 2500
    total = amount + admin_fee

    if account["balance"] < total:
        print("Insufficient balance! Transaction failed.")
        return

    print()
    print("---------- PAYMENT CONFIRMATION ----------")
    print("Meter number : " + meter)
    print("Token        : " + rupiah(amount))
    print("Admin fee    : " + rupiah(admin_fee))
    print("Total        : " + rupiah(total))
    print("------------------------------------------")

    if ask_yes_no("Confirm payment?") == False:
        print("Transaction cancelled.")
        return

    loading("Processing")
    account["balance"] = account["balance"] - total
    save_history(account, "Electricity token " + rupiah(amount) + " for meter " + meter)

    # make a random 20 digit token, shown in groups of 4
    token = ""
    for i in range(5):
        token = token + str(random.randint(1000, 9999)) + " "
    token = token.strip()

    print("Payment successful!")

    print_receipt("ELECTRICITY TOKEN", [
        "Meter number    : " + meter,
        "Token amount    : " + rupiah(amount),
        "Admin fee       : " + rupiah(admin_fee),
        "Total paid      : " + rupiah(total),
        "TOKEN           : " + token,
        "Balance         : " + rupiah(account["balance"])
    ])


def pdam_payment(account):
    print()
    print("--- PDAM WATER BILL ---")

    if ask_yes_no("View PDAM code list?"):
        print()
        print("PDAM CODE LIST")
        for code in pdam_regions:
            print(code + " : " + pdam_regions[code])
        print("Customer number = PDAM code + 6 digits (example: 11004521)")
        print()

    # enter customer number and check it in the billing database
    print("(type 0 to cancel)")
    while True:
        customer_number = input("Enter customer number: ").strip()
        if customer_number == "0":
            print("Transaction cancelled.")
            return
        loading("Checking billing data")
        if customer_number in pdam_bills:
            break
        print("Invalid number! Customer number is not found.\n")

    bill_data = pdam_bills[customer_number]
    region = pdam_regions[customer_number[:2]]

    if bill_data["paid"] == True:
        print("This bill has already been paid. No payment needed.")
        return

    admin_fee = 2500
    total = bill_data["bill"] + admin_fee

    # display transaction data (bill and more)
    print()
    print("--------------- BILL DATA ---------------")
    print("PDAM            : " + region)
    print("Customer number : " + customer_number)
    print("Customer name   : " + bill_data["name"])
    print("Period          : " + bill_data["period"])
    print("Water usage     : " + str(bill_data["usage"]) + " m3")
    print("Bill            : " + rupiah(bill_data["bill"]))
    print("Admin fee       : " + rupiah(admin_fee))
    print("Total           : " + rupiah(total))
    print("-----------------------------------------")

    if ask_yes_no("Continue payment?") == False:
        print("Payment cancelled.")
        return

    if account["balance"] < total:
        print("Insufficient balance! Transaction failed.")
        return

    loading("Processing")
    # deduct balance from account
    account["balance"] = account["balance"] - total
    # record bill as paid
    pdam_bills[customer_number]["paid"] = True
    save_history(account, "PDAM bill " + customer_number + " " + rupiah(total))

    print("Payment successful!")

    print_receipt("PDAM WATER BILL", [
        "PDAM            : " + region,
        "Customer number : " + customer_number,
        "Customer name   : " + bill_data["name"],
        "Period          : " + bill_data["period"],
        "Bill            : " + rupiah(bill_data["bill"]),
        "Admin fee       : " + rupiah(admin_fee),
        "Total paid      : " + rupiah(total),
        "Balance         : " + rupiah(account["balance"])
    ])


# ------------------------------------------------------------------
#  CHANGE PIN
# ------------------------------------------------------------------

def change_pin(account):
    print()
    print("--- CHANGE PIN ---")

    attempts = 0   # set attempt counter to 0
    while True:
        current_pin = input("Enter current PIN: ").strip()
        if current_pin == account["pin"]:
            break
        print("Incorrect PIN!")
        attempts = attempts + 1
        if attempts >= 3:
            account["blocked"] = True
            print("Card blocked for security reason.")
            return

    while True:
        new_pin = input("Enter new PIN (6 digits): ").strip()
        if pin_is_valid(new_pin) == False:
            print("PIN must be 6 digits.")
            continue
        if new_pin == account["pin"]:
            print("New PIN cannot be the same as your current PIN.")
            continue

        confirm_pin = input("Re-enter new PIN: ").strip()
        if confirm_pin == new_pin:
            break
        else:
            print("PIN does not match. Please enter your new PIN again.")

    # update PIN in the database
    accounts[account["number"]]["pin"] = new_pin
    save_history(account, "Changed PIN")
    print("PIN changed successfully!")


# ------------------------------------------------------------------
#  PROGRAM STARTS HERE
# ------------------------------------------------------------------

running = True
while running:
    print()
    line()
    print(("WELCOME TO " + bank_name + " ATM").center(46))
    line()
    print("1. Create a new account")
    print("2. Insert ATM card")
    print("3. Exit")
    menu = input("Choose (1-3): ").strip()

    if menu == "1":
        create_account()
    elif menu == "2":
        atm_session()
    elif menu == "3":
        print("Goodbye!")
        running = False
    else:
        print("Invalid option.")
