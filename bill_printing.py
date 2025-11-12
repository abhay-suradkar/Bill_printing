#!/usr/bin/env python
# coding: utf-8

# In[2]:


import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Abhay@123", 
    database="hotel_billing"
)
cur = conn.cursor(dictionary=True)


# In[ ]:


cur.execute("SELECT table_no FROM tables ORDER BY table_no;")
tables = [str(row['table_no']) for row in cur.fetchall()]

print("\nAvailable Tables:")
for t in tables:
    print(f"• Table {t}")

table_no = input("\nEnter Table Number: ").strip()
while table_no not in tables:
    print("Invalid table number. Try again.")
    table_no = input("Enter Table Number: ").strip()

cur.execute("SELECT table_id FROM tables WHERE table_no = %s", (table_no,))
table_id = cur.fetchone()['table_id']

cur.execute("SELECT menu_id, menu_name, price_per_item FROM menu;")
menu = cur.fetchall()

print("\nAvailable Menu:")
for idx, item in enumerate(menu, start=1):
    print(f"{idx}. {item['menu_name']:<15} ₹{int(item['price_per_item'])}")

cur.execute("INSERT INTO bills (table_id, total_amount, bill_date) VALUES (%s, %s, %s)",
            (table_id, 0, datetime.now()))
conn.commit()
bill_id = cur.lastrowid

orders = []
total_amount = 0

while True:
    item_name = input("\nEnter Menu Item Name (or 'done' to finish): ").strip().capitalize()
    if item_name.lower() == 'done':
        break

    cur.execute("SELECT menu_id, price_per_item FROM menu WHERE menu_name = %s", (item_name,))
    item = cur.fetchone()
    if not item:
        print("Invalid item name, please choose from menu.")
        continue

    while True:
        qty_input = input("Enter Quantity: ").strip()
        if qty_input.isdigit():
            qty = int(qty_input)
            if qty > 0:
                break
            else:
                print("Quantity must be greater than 0.")
        else:
            print("Please enter a valid number (e.g. 2, 5, 10).")

    item_total = item['price_per_item'] * qty
    total_amount += item_total

    cur.execute("INSERT INTO bill_items (bill_id, menu_id, quantity, item_total) VALUES (%s, %s, %s, %s)",
                (bill_id, item['menu_id'], qty, item_total))
    conn.commit()

    orders.append({"menu": item_name, "qty": qty, "price": item_total})

cur.execute("UPDATE bills SET total_amount = %s WHERE bill_id = %s", (total_amount, bill_id))
conn.commit()

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_path = r"C:\Users\Abhay Suradkar\OneDrive\Desktop\Hotel.txt"

with open(file_path, 'w', encoding='utf-8') as f:
    def write_print(line=""):
        print(line)
        f.write(line + "\n")

    write_print("_" * 54)
    write_print("|{:^54}|".format("Welcome to Taj"))
    write_print("|" + "-" * 52 + "|")
    write_print("| Table No: {:<41}|".format(table_no))
    write_print("|" + "-" * 52 + "|")
    write_print("| {:<3} {:<20} {:<10} {:>10}|".format("Sr", "Menu", "Quantity", "Price"))
    write_print("|" + "-" * 52 + "|")

    for i, o in enumerate(orders, start=1):
        write_print("| {:<3} {:<20} {:<10} {:>10}|".format(i, o['menu'], o['qty'], int(o['price'])))

    write_print("|" + "_" * 52 + "|")
    write_print("| Total Amount {:>33} |".format(int(total_amount)))
    write_print("|" + "_" * 52 + "|")

print(f"\nBill saved successfully {file_path}")

cur.close()
conn.close()

