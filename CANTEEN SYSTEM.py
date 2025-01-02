import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3


def initialize_db():
    conn = sqlite3.connect('basedata.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    address TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS login (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL)''')
    conn.commit()
    conn.close()


def switch_frame(to_frame):
    for frame in (login_frame, register_frame):
        frame.pack_forget()
    to_frame.pack()


def db_execute(query, params=(), fetch=False):

    try:
        conn = sqlite3.connect('basedata.db')
        c = conn.cursor()
        c.execute(query, params)
        if fetch:
            return c.fetchall()
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()


def register_user():
    email = entry_reg_email.get().strip()
    password = entry_reg_password.get().strip()
    address = entry_reg_address.get().strip()

    if email and password and address:
        if db_execute("SELECT email FROM registration WHERE email = ?", (email,), fetch=True):
            messagebox.showwarning("Registration Error", "Email is already registered.")
        else:
            db_execute("INSERT INTO registration (email, password, address) VALUES (?, ?, ?)", (email, password, address))
            db_execute("INSERT INTO login (email, password) VALUES (?, ?)", (email, password))
            messagebox.showinfo("Registration Successful", "You can now log in.")
            switch_frame(login_frame)
    else:
        messagebox.showwarning("Input Error", "All fields are required!")


def log_in_user():
    email = entry_login_email.get().strip()
    password = entry_login_password.get().strip()

    if email and password:
        result = db_execute("SELECT password FROM login WHERE email = ?", (email,), fetch=True)
        if result and password == result[0][0]:
            messagebox.showinfo("Login Successful", "Welcome!")
            show_main_menu()
        else:
            messagebox.showwarning("Login Error", "Invalid email or password.")
    else:
        messagebox.showwarning("Input Error", "All fields are required!")


def show_main_menu():
    app.withdraw()
    menu_app = tk.Toplevel()
    menu_app.title("Food and Drink Selector")
    menu_app.geometry("800x800")
    menu_app.config(bg="#8cb0ed")

    menu_bar = tk.Menu(menu_app)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=menu_app.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    menu_app.config(menu=menu_bar)

    frame_food = tk.Frame(menu_app, padx=10, pady=10, bg="#e0f7fa")
    frame_food.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_drinks = tk.Frame(menu_app, padx=10, pady=10, bg="#f1f8e9")
    frame_drinks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_history = tk.Frame(menu_app, padx=10, pady=10, bg="#ffecb3")
    frame_history.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    
    tk.Label(frame_food, text="Select Your Food", font=('Consolas', 16), bg="#e0f7fa").pack(pady=10)

    food_items = ["Turon", "Banana Cue", "Banana Fries", "Banana Chips", "Popcorn", "Bingo", "Fudgee Bar", "Combi", "Rebisco"]
    food_prices = {item: 5 for item in food_items}
    food_qty_vars = {item: tk.StringVar(value="0") for item in food_items}

    tk.Label(frame_drinks, text="Select Your Drinks", font=('Consolas', 16), bg="#f1f8e9").pack(pady=7)

    drink_items = ["Coke", "Royal", "Juice", "Mineral Water", "Sprite"]
    drink_prices = {item: 15 if item != "Juice" else 5 for item in drink_items}
    drink_qty_vars = {item: tk.StringVar(value="0") for item in drink_items}

    def create_food_drinks_ui():
        for food in food_items:
            tk.Label(frame_food, text=f"{food} (P{food_prices[food]})", bg="#e0f7fa").pack(anchor=tk.W)
            tk.Spinbox(frame_food, from_=0, to=10, textvariable=food_qty_vars[food], width=5).pack(anchor=tk.W)

        for drink in drink_items:
            tk.Label(frame_drinks, text=f"{drink} (P{drink_prices[drink]})", bg="#f1f8e9").pack(anchor=tk.W)
            tk.Spinbox(frame_drinks, from_=0, to=10, textvariable=drink_qty_vars[drink], width=5).pack(anchor=tk.W)

    create_food_drinks_ui()

    order_history_label = tk.Label(frame_history, text="Order History: ", font=("Arial", 12), anchor="w", bg="#ffecb3")
    order_history_label.pack(pady=10, padx=10)

    total_label = tk.Label(frame_food, text="Total Price: P0.00", font=("Arial", 12), bg="#e0f7fa")
    total_label.pack(pady=10)

    order_history = []
    order_listbox = tk.Listbox(frame_history, height=10, width=40, bg="#fff9c4")  # Light yellow for the Listbox
    order_listbox.pack(pady=10)

    def update_order_history():
        order_listbox.delete(0, tk.END)
        email = entry_login_email.get().strip()
        orders = db_execute("SELECT item_name, quantity, total_price FROM orders WHERE email = ?", (email,), fetch=True)
        for item_name, qty, total_price in orders:
            order_listbox.insert(tk.END, f"{item_name} x{qty} - P{total_price:.2f}")

    def calculate_total():
        selected_items = {**{k: int(v.get()) for k, v in food_qty_vars.items()}, **{k: int(v.get()) for k, v in drink_qty_vars.items()}}
        
        try:
            email = entry_login_email.get().strip()
            db_execute("DELETE FROM orders WHERE email = ?", (email,))
            for item, qty in selected_items.items():
                if qty > 0:
                    price = food_prices.get(item, drink_prices.get(item))
                    db_execute("INSERT INTO orders (email, item_name, quantity, total_price) VALUES (?, ?, ?, ?)", (email, item, qty, qty * price))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        update_order_history()

    def update_order_item():
        selected_index = order_listbox.curselection()
        if selected_index:
            selected_item = order_listbox.get(selected_index)
            item_name, qty = selected_item.split(" x")
            qty = int(qty.split(" -")[0])
            new_qty = simpledialog.askinteger("Update Quantity", f"Enter new quantity for {item_name}:", minvalue=1, maxvalue=10)
            if new_qty:
                email = entry_login_email.get().strip()
                price = food_prices.get(item_name, drink_prices.get(item_name))
                db_execute("UPDATE orders SET quantity = ?, total_price = ? WHERE email = ? AND item_name = ?", (new_qty, new_qty * price, email, item_name))
                update_order_history()

    def delete_order_item():
        selected_index = order_listbox.curselection()
        if selected_index:
            item_name = order_listbox.get(selected_index).split(" x")[0]
            email = entry_login_email.get().strip()
            db_execute("DELETE FROM orders WHERE email = ? AND item_name = ?", (email, item_name))
            update_order_history()

    tk.Button(frame_food, text="Calculate Total", command=calculate_total,bg="blue", fg="white").pack(pady=10)
    tk.Button(frame_history, text="Update Item", command=update_order_item,bg="blue", fg="white").pack(pady=10)
    tk.Button(frame_history, text="Delete Item", command=delete_order_item,bg="blue",  fg="white").pack(pady=10)
    tk.Button(frame_food, text="Exit", command=menu_app.destroy,bg="black", fg="violet").pack(pady=5)

    update_order_history()


app = tk.Tk()
app.title("User Login & Registration")
app.geometry("400x400")
app.config(bg="#8cb0ed")


login_frame = tk.Frame(app, bg="#8cb0ed")
tk.Label(login_frame, text="Log In", font=("Helvetica", 16), bg="#8cb0ed").pack(pady=10)
tk.Label(login_frame, text="Email:", bg="#8cb0ed").pack()
entry_login_email = tk.Entry(login_frame)
entry_login_email.pack(pady=5)
tk.Label(login_frame, text="Password:", bg="#8cb0ed").pack()
entry_login_password = tk.Entry(login_frame, show="*")
entry_login_password.pack(pady=5)
tk.Button(login_frame, text="Log In", command=log_in_user,bg="blue", fg="white").pack(pady=10)
tk.Button(login_frame, text="Go to Registration", command=lambda: switch_frame(register_frame),bg="black", fg="violet").pack()

register_frame = tk.Frame(app, bg="#8cb0ed")
tk.Label(register_frame, text="Register", font=("Helvetica", 16), bg="#8cb0ed").pack(pady=10)
tk.Label(register_frame, text="Email:", bg="#8cb0ed").pack()
entry_reg_email = tk.Entry(register_frame)
entry_reg_email.pack(pady=5)
tk.Label(register_frame, text="Password:", bg="#8cb0ed").pack()
entry_reg_password = tk.Entry(register_frame, show="*")
entry_reg_password.pack(pady=5)
tk.Label(register_frame, text="Address:", bg="#8cb0ed").pack()
entry_reg_address = tk.Entry(register_frame)
entry_reg_address.pack(pady=5)
tk.Button(register_frame, text="Register", command=register_user,bg="blue", fg="white").pack(pady=10)
tk.Button(register_frame, text="Go to Log In", command=lambda: switch_frame(login_frame),bg="black", fg="violet").pack()


login_frame.pack()

initialize_db()

app.mainloop()


