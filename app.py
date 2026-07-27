from tkinter import Button, Entry, Frame, Label, Toplevel, Tk, messagebox, ttk, Text, Scrollbar
import mysql.connector
import os
from PIL import Image, ImageTk

# --- DATABASE CONNECTION
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Dev@1245789",  # Update with your MySQL password
            database="inventory_management_1_db"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Could not connect to database:\n{err}\nMake sure 'inventory_management_1_db' exists.")
        return None

# --- MAIN APPLICATION CONTROLLER ---
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise Inventory & Financial Management System (Advanced)")
        self.root.geometry("1250x750")
        self.root.minsize(1050, 650)
        
        # Theme state: "light" or "dark"
        self.current_theme = "light"
        self.theme_colors = {
            "light": {
                "bg_main": "#ffffff",
                "bg_container": "#f4f6f9",
                "bg_sidebar": "#002b66",
                "sidebar_fg": "white",
                "sidebar_active": "#001a40",
                "header_bg": "#001f3f",
                "header_fg": "white",
                "text_main": "#333333",
                "card_bg": "#f8f9fa",
                "card_fg": "#555555"
            },
            "dark": {
                "bg_main": "#1e1e1e",
                "bg_container": "#121212",
                "bg_sidebar": "#2d2d2d",
                "sidebar_fg": "#e0e0e0",
                "sidebar_active": "#3d3d3d",
                "header_bg": "#111111",
                "header_fg": "#ffffff",
                "text_main": "#e0e0e0",
                "card_bg": "#252525",
                "card_fg": "#cccccc"
            }
        }
        self.setup_database_tables()
        self.apply_theme_styles()
        self.show_login_screen()

    def get_color(self, key):
        return self.theme_colors[self.current_theme][key]

    def apply_theme_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        if self.current_theme == "dark":
            style.configure("Treeview", 
                            background="#252525", 
                            foreground="#e0e0e0", 
                            fieldbackground="#252525",
                            borderwidth=0)
            style.configure("Treeview.Heading", 
                            background="#333333", 
                            foreground="#ffffff", 
                            relief="flat")
            style.map("Treeview", 
                      background=[('selected', '#007acc')],
                      foreground=[('selected', '#ffffff')])
        else:
            style.configure("Treeview", 
                            background="#ffffff", 
                            foreground="#333333", 
                            fieldbackground="#ffffff",
                            borderwidth=1)
            style.configure("Treeview.Heading", 
                            background="#e1e1e1", 
                            foreground="#000000", 
                            relief="raised")
            style.map("Treeview", 
                      background=[('selected', '#0078d7')],
                      foreground=[('selected', '#ffffff')])

    def setup_database_tables(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(50) NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    brand VARCHAR(100),
                    category VARCHAR(50),
                    price DECIMAL(10,2) NOT NULL,
                    quantity INT NOT NULL,
                    image_path VARCHAR(255)
                )
            """)
            for col_name, col_type in [("brand", "VARCHAR(100)"), ("image_path", "VARCHAR(255)")]:
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
                except mysql.connector.Error:
                    pass
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    contact VARCHAR(50),
                    email VARCHAR(100),
                    address TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_name VARCHAR(100) NOT NULL,
                    supplier_name VARCHAR(100),
                    cost_price DECIMAL(10,2) NOT NULL,
                    quantity INT NOT NULL,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_name VARCHAR(100) NOT NULL,
                    selling_price DECIMAL(10,2) NOT NULL,
                    quantity_sold INT NOT NULL,
                    total_revenue DECIMAL(10,2) NOT NULL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("INSERT IGNORE INTO users (username, password) VALUES ('admin', 'admin123')")
            conn.commit()
            conn.close()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- 1. LOGIN SCREEN ---
    def show_login_screen(self):
        self.clear_window()
        login_frame = Frame(self.root, bg="#001f3f")
        login_frame.pack(fill="both", expand=True)

        card = Frame(login_frame, bg="white", padx=50, pady=40, relief="raised", bd=2)
        card.place(relx=0.5, rely=0.5, anchor="center")

        Label(card, text="INVENTORY LOGIN", font=("Arial", 18, "bold"), bg="white", fg="#001f3f").pack(pady=(0, 20))

        Label(card, text="Username", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(anchor="w")
        self.username_entry = ttk.Entry(card, font=("Arial", 12), width=28)
        self.username_entry.pack(pady=(5, 15))

        Label(card, text="Password", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(anchor="w")
        self.password_entry = ttk.Entry(card, font=("Arial", 12), width=28, show="*")
        self.password_entry.pack(pady=(5, 20))

        Button(card, text="Secure Login", bg="#001f3f", fg="white", font=("Arial", 10, "bold"), width=22, command=self.authenticate_user).pack(pady=5)

    def authenticate_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                self.logged_in_username = user['username']
                self.show_dashboard_screen(self.logged_in_username)
            else:
                messagebox.showerror("Error", "Invalid Username or Password")
        except Exception as e:
            messagebox.showerror("Database Error", f"Details: {e}")

    # --- 2. MAIN DASHBOARD LAYOUT & NAVIGATION ---
    def show_dashboard_screen(self, logged_in_user):
        self.clear_window()
        self.apply_theme_styles()

        header_bg = self.get_color("header_bg")
        header_fg = self.get_color("header_fg")

        header_frame = Frame(self.root, bg=header_bg, height=55)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)

        Label(header_frame, text="INVENTORY & FINANCIAL CONTROL SYSTEM", bg=header_bg, fg=header_fg, font=("Arial", 13, "bold")).pack(side="left", padx=20, pady=12)
        Label(header_frame, text=f"Logged in as: {logged_in_user} (Administrator)", bg=header_bg, fg=header_fg, font=("Arial", 9)).pack(side="right", padx=20, pady=12)

        container_bg = self.get_color("bg_container")
        container = Frame(self.root, bg=container_bg)
        container.pack(side="top", fill="both", expand=True)

        sidebar_bg = self.get_color("bg_sidebar")
        sidebar_frame = Frame(container, bg=sidebar_bg, width=230)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.pack_propagate(False)

        content_bg = self.get_color("bg_main")
        self.content_area = Frame(container, bg=content_bg)
        self.content_area.pack(side="right", fill="both", expand=True)

        nav_buttons = [
            ("Dashboard", lambda: self.load_content("Dashboard")),
            ("Product Catalog", lambda: self.load_content("Product Catalog")),
            ("Product Image View", lambda: self.load_content("Product Image View")),
            ("Suppliers Directory", lambda: self.load_content("Suppliers Directory")),
            ("Stock Purchases (Cost)", lambda: self.load_content("Stock Purchases")),
            ("Sales History", lambda: self.load_content("Sales History")),
            ("Low Stock Alerts", lambda: self.load_content("Low Stock Alerts")),
            ("Annual Profit & Loss", lambda: self.load_content("Annual Profit & Loss")),
            ("Settings", lambda: self.load_content("Settings"))
        ]

        sidebar_fg = self.get_color("sidebar_fg")
        sidebar_active = self.get_color("sidebar_active")

        for text, command in nav_buttons:
            Button(sidebar_frame, text=text, bg=sidebar_bg, fg=sidebar_fg, activebackground=sidebar_active, activeforeground=sidebar_fg, font=("Arial", 10, "bold"), bd=0, anchor="w", padx=20, pady=12, command=command).pack(fill="x")

        self.load_content("Dashboard")

    def load_content(self, page_name):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        content_bg = self.get_color("bg_main")
        text_main = self.get_color("text_main")
        self.content_area.config(bg=content_bg)

        if page_name != "Dashboard":
            Label(self.content_area, text=page_name, font=("Arial", 18, "bold"), bg=content_bg, fg=text_main).pack(anchor="nw", padx=35, pady=20)

        if page_name == "Dashboard":
            self.render_dashboard_analytics()
        elif page_name == "Product Catalog":
            self.render_product_catalog()
        elif page_name == "Product Image View":
            self.render_product_image_view()
        elif page_name == "Suppliers Directory":
            self.render_suppliers_directory()
        elif page_name == "Stock Purchases":
            self.render_stock_purchases()
        elif page_name == "Sales History":
            self.render_sales_history()
        elif page_name == "Low Stock Alerts":
            self.render_low_stock_alerts()
        elif page_name == "Annual Profit & Loss":
            self.render_annual_profit_loss()
        elif page_name == "Settings":
            self.render_settings_page()

    # --- 3. ADVANCED DASHBOARD ANALYTICS ---
    def render_dashboard_analytics(self):
        conn = connect_db()
        prod_count, supp_count, raised_requests_count = 0, 0, 0
        total_revenue, total_expenses, net_profit = 0.0, 0.0, 0.0
        low_stock_items = []

        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            prod_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM suppliers")
            supp_count = cursor.fetchone()[0]

            cursor.execute("SELECT name, quantity FROM products WHERE quantity < 5")
            low_stock_items = cursor.fetchall()
            raised_requests_count = len(low_stock_items)

            cursor.execute("SELECT SUM(total_revenue) FROM sales")
            res_rev = cursor.fetchone()[0]
            if res_rev:
                total_revenue = float(res_rev)

            cursor.execute("SELECT SUM(cost_price * quantity) FROM purchases")
            res_exp = cursor.fetchone()[0]
            if res_exp:
                total_expenses = float(res_exp)

            net_profit = total_revenue - total_expenses
            conn.close()

        content_bg = self.get_color("bg_main")
        text_main = self.get_color("text_main")

        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=15)

        Label(body, text="Dashboard Analytics", font=("Arial", 16, "bold"), bg=content_bg, fg=text_main).pack(anchor="nw", pady=(0, 10))

        metrics_grid = Frame(body, bg=content_bg)
        metrics_grid.pack(fill="x", pady=5)

        def create_colored_metric_card(parent, title, value, row, col, bg_card_color):
            card = Frame(parent, bg=bg_card_color, bd=1, relief="solid", padx=15, pady=12, width=220, height=80)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.pack_propagate(False)
            Label(card, text=title, font=("Arial", 9, "bold"), bg=bg_card_color, fg="white").pack(anchor="center")
            Label(card, text=str(value), font=("Arial", 16, "bold"), bg=bg_card_color, fg="white").pack(anchor="center", pady=(5, 0))

        create_colored_metric_card(metrics_grid, "Total Products", prod_count, 0, 0, "#2980b9")
        create_colored_metric_card(metrics_grid, "Total Suppliers", supp_count, 0, 1, "#8e44ad")
        create_colored_metric_card(metrics_grid, "Raised Purchase Requests", raised_requests_count, 0, 2, "#d35400")
        create_colored_metric_card(metrics_grid, "Annual Revenue", f"${total_revenue:,.2f}", 1, 0, "#27ae60")
        create_colored_metric_card(metrics_grid, "Annual Expenses", f"${total_expenses:,.2f}", 1, 1, "#c0392b")
        
        net_box_color = "#16a085" if net_profit >= 0 else "#e74c3c"
        create_colored_metric_card(metrics_grid, "Annual Net Profit", f"${net_profit:,.2f}", 1, 2, net_box_color)

        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)
        metrics_grid.columnconfigure(2, weight=1)

        sms_outer_frame = Frame(body, bg=content_bg, bd=1, relief="solid")
        sms_outer_frame.pack(fill="both", expand=True, pady=(15, 5))

        sms_title_frame = Frame(sms_outer_frame, bg=self.get_color("card_bg"), height=30)
        sms_title_frame.pack(fill="x", side="top")
        sms_title_frame.pack_propagate(False)
        Label(sms_title_frame, text="SMS Notification Alert Box", font=("Arial", 9, "bold"), bg=self.get_color("card_bg"), fg=text_main).pack(side="left", padx=10, pady=5)

        text_container = Frame(sms_outer_frame, bg=content_bg)
        text_container.pack(fill="both", expand=True, padx=5, pady=5)

        sms_scroll = Scrollbar(text_container)
        sms_scroll.pack(side="right", fill="y")

        sms_text_box = Text(text_container, font=("Consolas", 10), bg=content_bg, fg=text_main, bd=0, yscrollcommand=sms_scroll.set, wrap="word", height=12)
        sms_text_box.pack(side="left", fill="both", expand=True)
        sms_scroll.config(command=sms_text_box.yview)

        if low_stock_items:
            sms_text_box.insert("end", "[SMS Notification] Low Stock Purchase Requests Raised:\n\n")
            for item_name, qty in low_stock_items:
                sms_text_box.insert("end", f"ALERT: Product '{item_name}' has fallen to {qty} units. Restock request sent to suppliers.\n")
        else:
            sms_text_box.insert("end", "[SMS Inbox Empty] No low stock purchase request messages generated yet.\n")
        sms_text_box.config(state="disabled")

    # --- 4. ANNUAL PROFIT & LOSS MODULE ---
    def render_annual_profit_loss(self):
        content_bg = self.get_color("bg_main")
        text_main = self.get_color("text_main")

        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=10)

        Label(body, text="Annual Financial Performance (Profit & Loss Statement)", font=("Arial", 14, "bold"), bg=content_bg, fg=text_main).pack(anchor="nw", pady=(0, 15))

        conn = connect_db()
        total_rev = 0.0
        total_exp = 0.0
        sales_records = []
        purchase_records = []

        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT SUM(total_revenue) as rev FROM sales")
            res_rev = cursor.fetchone()
            if res_rev and res_rev['rev']:
                total_rev = float(res_rev['rev'])

            cursor.execute("SELECT SUM(cost_price * quantity) as exp FROM purchases")
            res_exp = cursor.fetchone()
            if res_exp and res_exp['exp']:
                total_exp = float(res_exp['exp'])

            cursor.execute("SELECT item_name, selling_price, quantity_sold, total_revenue, sale_date FROM sales")
            sales_records = cursor.fetchall()

            cursor.execute("SELECT item_name, supplier_name, cost_price, quantity, purchase_date FROM purchases")
            purchase_records = cursor.fetchall()
            conn.close()

        net_income = total_rev - total_exp

        summary_frame = Frame(body, bg=content_bg)
        summary_frame.pack(fill="x", pady=10)

        def make_pl_card(parent, title, val, color):
            card = Frame(parent, bg=color, padx=15, pady=15)
            card.pack(side="left", padx=10, expand=True, fill="x")
            Label(card, text=title, font=("Arial", 10, "bold"), bg=color, fg="white").pack(anchor="w")
            Label(card, text=f"${val:,.2f}", font=("Arial", 18, "bold"), bg=color, fg="white").pack(anchor="w", pady=(5, 0))

        make_pl_card(summary_frame, "Total Revenue", total_rev, "#27ae60")
        make_pl_card(summary_frame, "Total Expenses (Cost)", total_exp, "#c0392b")
        net_color = "#2980b9" if net_income >= 0 else "#d35400"
        make_pl_card(summary_frame, "Net Profit / Loss", net_income, net_color)

        tables_frame = Frame(body, bg=content_bg)
        tables_frame.pack(fill="both", expand=True, pady=15)

        rev_frame = Frame(tables_frame, bg=content_bg)
        rev_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        Label(rev_frame, text="Revenue Breakdown (Sales)", font=("Arial", 11, "bold"), bg=content_bg, fg="#27ae60").pack(anchor="nw", pady=5)
        rev_tree = ttk.Treeview(rev_frame, columns=("Item", "Price", "Qty", "Total", "Date"), show="headings", height=8)
        for col in ("Item", "Price", "Qty", "Total", "Date"):
            rev_tree.heading(col, text=col)
            rev_tree.column(col, width=90, anchor="center")
        rev_tree.pack(fill="both", expand=True)

        for s in sales_records:
            rev_tree.insert("", "end", values=(s['item_name'], f"${s['selling_price']:.2f}", s['quantity_sold'], f"${s['total_revenue']:.2f}", str(s['sale_date'])[:10]))

        exp_frame = Frame(tables_frame, bg=content_bg)
        exp_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        Label(exp_frame, text="Expense Breakdown (Purchases)", font=("Arial", 11, "bold"), bg=content_bg, fg="#c0392b").pack(anchor="nw", pady=5)
        exp_tree = ttk.Treeview(exp_frame, columns=("Item", "Supplier", "Cost", "Qty", "Date"), show="headings", height=8)
        for col in ("Item", "Supplier", "Cost", "Qty", "Date"):
            exp_tree.heading(col, text=col)
            exp_tree.column(col, width=90, anchor="center")
        exp_tree.pack(fill="both", expand=True)

        for p in purchase_records:
            exp_tree.insert("", "end", values=(p['item_name'], p['supplier_name'], f"${p['cost_price']:.2f}", p['quantity'], str(p['purchase_date'])[:10]))

    # --- 5. SETTINGS MODULE & PASSWORD CHANGE ---
    def open_change_password_popup(self):
        popup = Toplevel(self.root)
        popup.title("Change Password")
        popup.geometry("380x300")
        popup.config(bg="white")
        popup.grab_set()

        Label(popup, text="Change Account Password", font=("Arial", 13, "bold"), bg="white", fg="#001f3f").pack(pady=15)

        form_frame = Frame(popup, bg="white")
        form_frame.pack(pady=5)

        fields = [
            ("Old Password:", "old_pass"),
            ("New Password:", "new_pass"),
            ("Confirm New Password:", "confirm_pass")
        ]
        entries = {}
        for i, (label_text, key) in enumerate(fields):
            Label(form_frame, text=label_text, font=("Arial", 9, "bold"), bg="white").grid(row=i, column=0, padx=8, pady=8, sticky="e")
            ent = Entry(form_frame, font=("Arial", 10), width=18, show="*")
            ent.grid(row=i, column=1, padx=8, pady=8, sticky="w")
            entries[key] = ent

        def save_new_password():
            old_p = entries["old_pass"].get().strip()
            new_p = entries["new_pass"].get().strip()
            confirm_p = entries["confirm_pass"].get().strip()

            if not old_p or not new_p or not confirm_p:
                messagebox.showerror("Error", "All password fields are required.", parent=popup)
                return
            if new_p != confirm_p:
                messagebox.showerror("Error", "New passwords do not match.", parent=popup)
                return

            current_user = getattr(self, "logged_in_username", "admin")
            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (current_user, old_p))
                    user = cursor.fetchone()
                    if not user:
                        messagebox.showerror("Error", "Incorrect old password entered.", parent=popup)
                        conn.close()
                        return

                    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_p, current_user))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Password changed successfully!", parent=popup)
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Details: {e}", parent=popup)

        Button(popup, text="Update Password", bg="#0275d8", fg="white", font=("Arial", 10, "bold"), width=18, command=save_new_password).pack(pady=15)

    def render_settings_page(self):
        content_bg = self.get_color("bg_main")
        text_main = self.get_color("text_main")
        card_bg = self.get_color("card_bg")

        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=20)

        Label(body, text="System Preferences & Controls", font=("Arial", 14, "bold"), bg=content_bg, fg=text_main).pack(anchor="nw", pady=(0, 20))

        theme_card = Frame(body, bg=card_bg, bd=1, relief="solid", padx=20, pady=20)
        theme_card.pack(fill="x", pady=10)

        Label(theme_card, text="Appearance Theme", font=("Arial", 11, "bold"), bg=card_bg, fg=text_main).pack(anchor="nw", pady=(0, 5))
        Label(theme_card, text=f"Current Theme: {self.current_theme.capitalize()} Mode", font=("Arial", 9), bg=card_bg, fg=text_main).pack(anchor="nw", pady=(0, 15))

        def toggle_theme():
            self.current_theme = "dark" if self.current_theme == "light" else "light"
            self.show_dashboard_screen(getattr(self, 'logged_in_username', 'admin'))
            self.load_content("Settings")

        theme_btn_text = "Switch to Dark Theme" if self.current_theme == "light" else "Switch to Light Theme"
        Button(theme_card, text=theme_btn_text, bg="#0275d8", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8, command=toggle_theme).pack(anchor="nw")

        security_card = Frame(body, bg=card_bg, bd=1, relief="solid", padx=20, pady=20)
        security_card.pack(fill="x", pady=10)

        Label(security_card, text="Account Security", font=("Arial", 11, "bold"), bg=card_bg, fg=text_main).pack(anchor="nw", pady=(0, 5))
        Label(security_card, text="Update your account login password securely.", font=("Arial", 9), bg=card_bg, fg=text_main).pack(anchor="nw", pady=(0, 15))
        Button(security_card, text="Change Password", bg="#f0ad4e", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8, command=self.open_change_password_popup).pack(anchor="nw")

        account_card = Frame(body, bg=card_bg, bd=1, relief="solid", padx=20, pady=20)
        account_card.pack(fill="x", pady=10)

        Label(account_card, text="Session Management", font=("Arial", 11, "bold"), bg=card_bg, fg=text_main).pack(anchor="nw", pady=(0, 5))
        Label(account_card, text="Sign out of your active administrative session securely.", font=("Arial", 9), bg=card_bg, fg=text_main).pack(anchor="nw", pady=(0, 15))
        Button(account_card, text="Logout from System", bg="#c9302c", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8, command=self.show_login_screen).pack(anchor="nw")

    # --- 6. PRODUCT CATALOG MANAGEMENT ---
    def render_product_catalog(self):
        content_bg = self.get_color("bg_main")
        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=5)

        toolbar = Frame(body, bg=content_bg)
        toolbar.pack(fill="x", pady=10)

        Button(toolbar, text="+ Add Product", bg="#5cb85c", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=lambda: self.open_product_popup("Add")).pack(side="left", padx=(0, 5))
        Button(toolbar, text="Edit Product", bg="#f0ad4e", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=lambda: self.open_product_popup("Edit")).pack(side="left", padx=5)
        Button(toolbar, text="Delete Product", bg="#d9534f", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=self.delete_product).pack(side="left", padx=5)

        search_frame = Frame(toolbar, bg=content_bg)
        search_frame.pack(side="right")

        Label(search_frame, text="Search Product:", font=("Arial", 9, "bold"), bg=content_bg, fg=self.get_color("text_main")).pack(side="left", padx=5)
        self.prod_search_ent = Entry(search_frame, font=("Arial", 10), width=20)
        self.prod_search_ent.pack(side="left", padx=5)
        self.prod_search_ent.bind("<KeyRelease>", self.filter_products)

        columns = ("ID", "Name", "Brand", "Category", "Price ($)", "Quantity", "Total Value ($)", "Image Path")
        self.prod_tree = ttk.Treeview(body, columns=columns, show="headings", height=14)
        for col in columns:
            self.prod_tree.heading(col, text=col)
            self.prod_tree.column(col, width=110, anchor="center")
        self.prod_tree.pack(fill="both", expand=True, pady=5)
        # Note: The automatic image popup binding has been removed here.

        self.load_product_data()

    # --- 7. PRODUCT IMAGE VIEW MODULE ---
    def render_product_image_view(self):
        content_bg = self.get_color("bg_main")
        text_main = self.get_color("text_main")

        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=10)

        Label(body, text="Select a product below to view its associated image:", font=("Arial", 10), bg=content_bg, fg=text_main).pack(anchor="nw", pady=(0, 10))

        control_frame = Frame(body, bg=content_bg)
        control_frame.pack(fill="x", pady=5)

        Label(control_frame, text="Choose Product:", font=("Arial", 10, "bold"), bg=content_bg, fg=text_main).pack(side="left", padx=(0, 10))

        product_names = []
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM products")
            product_names = [row[0] for row in cursor.fetchall()]
            conn.close()

        self.img_combo_var = ttk.Combobox(control_frame, values=product_names, font=("Arial", 10), width=25, state="readonly")
        if product_names:
            self.img_combo_var.current(0)
        self.img_combo_var.pack(side="left", padx=5)

        Button(control_frame, text="Show Image", bg="#0275d8", fg="white", font=("Arial", 9, "bold"), padx=15, pady=5, command=self.load_selected_product_image).pack(side="left", padx=10)

        self.image_display_container = Frame(body, bg=self.get_color("card_bg"), bd=1, relief="solid", width=500, height=400)
        self.image_display_container.pack(fill="both", expand=True, pady=15)
        self.image_display_container.pack_propagate(False)

        self.inline_img_label = Label(self.image_display_container, text="[No Image Loaded. Select a product and click 'Show Image']", font=("Arial", 10), bg=self.get_color("card_bg"), fg=text_main)
        self.inline_img_label.pack(expand=True)

    def load_selected_product_image(self):
        selected_prod_name = self.img_combo_var.get()
        if not selected_prod_name:
            messagebox.showerror("Selection Error", "Please select a product from the dropdown list.")
            return

        conn = connect_db()
        img_path = None
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT image_path FROM products WHERE name = %s", (selected_prod_name,))
            res = cursor.fetchone()
            if res:
                img_path = res[0]
            conn.close()

        text_main = self.get_color("text_main")
        card_bg = self.get_color("card_bg")

        for widget in self.image_display_container.winfo_children():
            widget.destroy()

        if not img_path or img_path == "No Image" or not os.path.exists(img_path):
            Label(self.image_display_container, text=f"No image file configured or found for '{selected_prod_name}'.", font=("Arial", 10, "bold"), bg=card_bg, fg="#d9534f").pack(expand=True)
            return

        try:
            pil_img = Image.open(img_path)
            pil_img.thumbnail((420, 350))
            self.current_inline_img = ImageTk.PhotoImage(pil_img)
            Label(self.image_display_container, text=f"Product: {selected_prod_name}", font=("Arial", 11, "bold"), bg=card_bg, fg=text_main).pack(pady=(10, 5))
            img_lbl = Label(self.image_display_container, image=self.current_inline_img, bg=card_bg)
            img_lbl.pack(expand=True, pady=5)
        except Exception as e:
            Label(self.image_display_container, text=f"Error loading image file:\n{e}", font=("Arial", 10), bg=card_bg, fg="red").pack(expand=True)

    def load_product_data(self, search_query=""):
        for item in self.prod_tree.get_children():
            self.prod_tree.delete(item)

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            if search_query:
                query = "SELECT id, name, brand, category, price, quantity, image_path FROM products WHERE name LIKE %s OR brand LIKE %s OR category LIKE %s"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute("SELECT id, name, brand, category, price, quantity, image_path FROM products")

            for row in cursor.fetchall():
                prod_id, name, brand, cat, price, qty, img = row
                brand_str = brand if brand else "N/A"
                img_str = img if img else "No Image"
                total_val = float(price) * int(qty)
                self.prod_tree.insert("", "end", values=(prod_id, name, brand_str, cat, f"{price:.2f}", qty, f"{total_val:.2f}", img_str))
            conn.close()

    def filter_products(self, event):
        query = self.prod_search_ent.get().strip()
        self.load_product_data(query)

    def open_product_popup(self, mode):
        from tkinter import filedialog
        selected_item = self.prod_tree.focus()
        if mode == "Edit" and not selected_item:
            messagebox.showerror("Error", "Please select a product record from the table to modify.")
            return

        popup = Toplevel(self.root)
        popup.title(f"{mode} Product Record")
        popup.geometry("480x500")
        popup.config(bg="white")
        popup.grab_set()

        Label(popup, text=f"{mode} Product Details", font=("Arial", 13, "bold"), bg="white", fg="#001f3f").pack(pady=15)

        form_frame = Frame(popup, bg="white")
        form_frame.pack(pady=5)

        Label(form_frame, text="Product Name:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        name_ent = Entry(form_frame, font=("Arial", 10), width=22)
        name_ent.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        Label(form_frame, text="Brand Name:", font=("Arial", 9, "bold"), bg="white").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        brand_ent = Entry(form_frame, font=("Arial", 10), width=22)
        brand_ent.grid(row=1, column=1, padx=8, pady=8, sticky="w")

        Label(form_frame, text="Category:", font=("Arial", 9, "bold"), bg="white").grid(row=2, column=0, padx=8, pady=8, sticky="e")
        cat_ent = Entry(form_frame, font=("Arial", 10), width=22)
        cat_ent.grid(row=2, column=1, padx=8, pady=8, sticky="w")

        Label(form_frame, text="Unit Price ($):", font=("Arial", 9, "bold"), bg="white").grid(row=3, column=0, padx=8, pady=8, sticky="e")
        price_ent = Entry(form_frame, font=("Arial", 10), width=22)
        price_ent.grid(row=3, column=1, padx=8, pady=8, sticky="w")

        Label(form_frame, text="Initial Quantity:", font=("Arial", 9, "bold"), bg="white").grid(row=4, column=0, padx=8, pady=8, sticky="e")
        qty_ent = Entry(form_frame, font=("Arial", 10), width=22)
        qty_ent.grid(row=4, column=1, padx=8, pady=8, sticky="w")

        Label(form_frame, text="Image File Path:", font=("Arial", 9, "bold"), bg="white").grid(row=5, column=0, padx=8, pady=8, sticky="e")
        img_ent = Entry(form_frame, font=("Arial", 10), width=22)
        img_ent.grid(row=5, column=1, padx=8, pady=8, sticky="w")

        def browse_image():
            file_path = filedialog.askopenfilename(title="Select Product Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")])
            if file_path:
                img_ent.delete(0, "end")
                img_ent.insert(0, file_path)

        Button(form_frame, text="Browse...", bg="#0275d8", fg="white", font=("Arial", 8, "bold"), command=browse_image).grid(row=5, column=2, padx=5, sticky="w")

        prod_id = None
        if mode == "Edit":
            values = self.prod_tree.item(selected_item, "values")
            prod_id = values[0]
            name_ent.insert(0, values[1])
            if values[2] != "N/A":
                brand_ent.insert(0, values[2])
            cat_ent.insert(0, values[3])
            price_ent.insert(0, values[4])
            qty_ent.insert(0, values[5])
            if values[7] != "No Image":
                img_ent.insert(0, values[7])

        def save_action():
            name = name_ent.get().strip()
            brand = brand_ent.get().strip()
            cat = cat_ent.get().strip()
            price = price_ent.get().strip()
            qty = qty_ent.get().strip()
            img_path = img_ent.get().strip()

            if not name or not price or not qty:
                messagebox.showerror("Validation Error", "Name, Price, and Quantity fields cannot be empty.", parent=popup)
                return
            try:
                float(price)
                int(qty)
            except ValueError:
                messagebox.showerror("Validation Error", "Price must be a valid number and quantity must be an integer.", parent=popup)
                return

            conn = connect_db()
            if not conn:
                messagebox.showerror("Database Error", "Unable to connect to MySQL database.", parent=popup)
                return

            try:
                cursor = conn.cursor()
                if mode == "Add":
                    cursor.execute("INSERT INTO products (name, brand, category, price, quantity, image_path) VALUES (%s, %s, %s, %s, %s, %s)", (name, brand, cat, price, qty, img_path))
                else:
                    cursor.execute("UPDATE products SET name = %s, brand = %s, category = %s, price = %s, quantity = %s, image_path = %s WHERE id = %s", (name, brand, cat, price, qty, img_path, prod_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Product record successfully {mode.lower()}ed!", parent=popup)
                popup.destroy()
                self.load_product_data()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to save record:\n{err}", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred:\n{e}", parent=popup)

        Button(popup, text="Save Record", bg="#5cb85c", fg="white", font=("Arial", 10, "bold"), width=18, command=save_action).pack(pady=15)

    def delete_product(self):
        selected = self.prod_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a product record from the table first.")
            return

        values = self.prod_tree.item(selected, "values")
        prod_id = values[0]

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to permanently delete this product?"):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = %s", (prod_id,))
                conn.commit()
                conn.close()
                self.load_product_data()

    # --- 8. SUPPLIERS DIRECTORY MANAGEMENT ---
    def render_suppliers_directory(self):
        content_bg = self.get_color("bg_main")
        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=5)

        toolbar = Frame(body, bg=content_bg)
        toolbar.pack(fill="x", pady=10)

        Button(toolbar, text="+ Add Supplier", bg="#5cb85c", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=lambda: self.open_supplier_popup("Add")).pack(side="left", padx=(0, 5))
        Button(toolbar, text="Edit Supplier", bg="#f0ad4e", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=lambda: self.open_supplier_popup("Edit")).pack(side="left", padx=5)
        Button(toolbar, text="Delete Supplier", bg="#d9534f", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=self.delete_supplier).pack(side="left", padx=5)
        Button(toolbar, text="Show Purchase History", bg="#0275d8", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=self.show_supplier_purchase_history).pack(side="left", padx=5)

        search_frame = Frame(toolbar, bg=content_bg)
        search_frame.pack(side="right")

        Label(search_frame, text="Search Supplier:", font=("Arial", 9, "bold"), bg=content_bg, fg=self.get_color("text_main")).pack(side="left", padx=5)
        self.supp_search_ent = Entry(search_frame, font=("Arial", 10), width=20)
        self.supp_search_ent.pack(side="left", padx=5)
        self.supp_search_ent.bind("<KeyRelease>", self.filter_suppliers)

        columns = ("ID", "Supplier Name", "Contact No", "Email Address", "Physical Address")
        self.supp_tree = ttk.Treeview(body, columns=columns, show="headings", height=15)
        for col in columns:
            self.supp_tree.heading(col, text=col)
            self.supp_tree.column(col, width=140, anchor="center")
        self.supp_tree.pack(fill="both", expand=True, pady=5)

        self.load_supplier_data()

    def show_supplier_purchase_history(self):
        selected_item = self.supp_tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a supplier from the directory table first.")
            return

        values = self.supp_tree.item(selected_item, "values")
        supplier_name = values[1]

        conn = connect_db()
        purchase_records = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, item_name, cost_price, quantity, purchase_date FROM purchases WHERE supplier_name = %s", (supplier_name,))
            purchase_records = cursor.fetchall()
            conn.close()

        history_popup = Toplevel(self.root)
        history_popup.title(f"Purchase History: {supplier_name}")
        history_popup.geometry("600x400")
        history_popup.config(bg="white")
        history_popup.grab_set()

        Label(history_popup, text=f"Purchase History for Supplier: {supplier_name}", font=("Arial", 12, "bold"), bg="white", fg="#001f3f").pack(pady=15)

        table_frame = Frame(history_popup, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        columns = ("ID", "Item Name", "Cost Price ($)", "Quantity", "Purchase Date")
        hist_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns:
            hist_tree.heading(col, text=col)
            hist_tree.column(col, width=105, anchor="center")
        hist_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=hist_tree.yview)
        scrollbar.pack(side="right", fill="y")
        hist_tree.configure(yscrollcommand=scrollbar.set)

        if purchase_records:
            for p in purchase_records:
                hist_tree.insert("", "end", values=(p['id'], p['item_name'], f"${p['cost_price']:.2f}", p['quantity'], str(p['purchase_date'])[:19]))
        else:
            Label(history_popup, text="No purchase transactions recorded for this supplier.", font=("Arial", 10, "italic"), bg="white", fg="gray").pack(pady=20)

    def load_supplier_data(self, search_query=""):
        for item in self.supp_tree.get_children():
            self.supp_tree.delete(item)

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            if search_query:
                query = "SELECT id, name, contact, email, address FROM suppliers WHERE name LIKE %s OR contact LIKE %s OR email LIKE %s"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute("SELECT id, name, contact, email, address FROM suppliers")

            for row in cursor.fetchall():
                self.supp_tree.insert("", "end", values=row)
            conn.close()

    def filter_suppliers(self, event):
        query = self.supp_search_ent.get().strip()
        self.load_supplier_data(query)

    def open_supplier_popup(self, mode):
        selected_item = self.supp_tree.focus()
        if mode == "Edit" and not selected_item:
            messagebox.showerror("Error", "Please select a supplier record from the table to modify.")
            return

        popup = Toplevel(self.root)
        popup.title(f"{mode} Supplier Record")
        popup.geometry("420x420")
        popup.config(bg="white")
        popup.grab_set()

        Label(popup, text=f"{mode} Supplier Details (Detailed)", font=("Arial", 13, "bold"), bg="white", fg="#001f3f").pack(pady=15)

        form_frame = Frame(popup, bg="white")
        form_frame.pack(pady=5)

        fields = [
            ("Supplier Name:", "name"),
            ("Contact No:", "contact"),
            ("Email Address:", "email"),
            ("Physical Address:", "address")
        ]
        entries = {}
        for i, (label_text, key) in enumerate(fields):
            Label(form_frame, text=label_text, font=("Arial", 9, "bold"), bg="white").grid(row=i, column=0, padx=8, pady=8, sticky="e")
            ent = Entry(form_frame, font=("Arial", 10), width=22)
            ent.grid(row=i, column=1, padx=8, pady=8, sticky="w")
            entries[key] = ent

        supp_id = None
        if mode == "Edit":
            values = self.supp_tree.item(selected_item, "values")
            supp_id = values[0]
            entries["name"].insert(0, values[1])
            entries["contact"].insert(0, values[2])
            entries["email"].insert(0, values[3])
            entries["address"].insert(0, values[4])

        def save_action():
            name = entries["name"].get().strip()
            contact = entries["contact"].get().strip()
            email = entries["email"].get().strip()
            address = entries["address"].get().strip()

            if not name:
                messagebox.showerror("Validation Error", "Supplier Name field is required.", parent=popup)
                return

            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    if mode == "Add":
                        cursor.execute("INSERT INTO suppliers (name, contact, email, address) VALUES (%s, %s, %s, %s)", (name, contact, email, address))
                    else:
                        cursor.execute("UPDATE suppliers SET name = %s, contact = %s, email = %s, address = %s WHERE id = %s", (name, contact, email, address, supp_id))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", f"Supplier record successfully {mode.lower()}ed!", parent=popup)
                    popup.destroy()
                    self.load_supplier_data()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Failed to save supplier:\n{e}", parent=popup)

        Button(popup, text="Save Record", bg="#5cb85c", fg="white", font=("Arial", 10, "bold"), width=18, command=save_action).pack(pady=15)

    def delete_supplier(self):
        selected = self.supp_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a supplier record from the table first.")
            return

        values = self.supp_tree.item(selected, "values")
        supp_id = values[0]

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to permanently delete this supplier?"):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM suppliers WHERE id = %s", (supp_id,))
                conn.commit()
                conn.close()
                self.load_supplier_data()

    # --- 9. STOCK PURCHASES MODULE & PURCHASE INVOICE FEATURE ---
    def render_stock_purchases(self):
        content_bg = self.get_color("bg_main")
        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=5)

        toolbar = Frame(body, bg=content_bg)
        toolbar.pack(fill="x", pady=10)

        Button(toolbar, text="+ Record Purchase (Restock)", font=("Arial", 9, "bold"), padx=10, pady=5, bg="#0275d8", fg="white", command=self.open_purchase_popup).pack(side="left", padx=(0, 5))
        Button(toolbar, text="Print Purchase Invoice", bg="#f0ad4e", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=self.show_purchase_invoice).pack(side="left", padx=5)

        columns = ("ID", "Item Name", "Supplier", "Cost Price ($)", "Quantity Purchased", "Date Logged")
        self.purch_tree = ttk.Treeview(body, columns=columns, show="headings", height=15)
        for col in columns:
            self.purch_tree.heading(col, text=col)
            self.purch_tree.column(col, width=140, anchor="center")
        self.purch_tree.pack(fill="both", expand=True, pady=5)

        self.load_purchase_data()

    def show_purchase_invoice(self):
        selected_item = self.purch_tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a purchase record from the table first to generate an invoice.")
            return

        values = self.purch_tree.item(selected_item, "values")
        p_id, item_name, supplier_name, cost_price, quantity, purchase_date = values

        try:
            total_cost = float(str(cost_price).replace('$', '')) * int(quantity)
        except ValueError:
            total_cost = 0.0

        invoice_popup = Toplevel(self.root)
        invoice_popup.title(f"Purchase Invoice #{p_id}")
        invoice_popup.geometry("460x520")
        invoice_popup.config(bg="white")
        invoice_popup.grab_set()

        Header_frame = Frame(invoice_popup, bg="#001f3f", pady=15)
        Header_frame.pack(fill="x")
        Label(Header_frame, text="OFFICIAL PURCHASE INVOICE", font=("Arial", 14, "bold"), bg="#001f3f", fg="white").pack()
        Label(Header_frame, text="Enterprise Inventory & Financial Management System", font=("Arial", 9), bg="#001f3f", fg="#cccccc").pack(pady=(3, 0))

        content_frame = Frame(invoice_popup, bg="white", padx=25, pady=15)
        content_frame.pack(fill="both", expand=True)

        details = [
            ("Invoice ID:", f"#INV-PUR-{p_id}"),
            ("Purchase Date:", str(purchase_date)),
            ("Supplier Name:", str(supplier_name)),
            ("Item Restocked:", str(item_name)),
            ("Quantity Purchased:", str(quantity)),
            ("Unit Cost Price:", f"${cost_price}")
        ]

        for i, (label, val) in enumerate(details):
            Label(content_frame, text=label, font=("Arial", 10, "bold"), bg="white", fg="#555555").grid(row=i, column=0, sticky="w", pady=5)
            Label(content_frame, text=val, font=("Arial", 10), bg="white", fg="#333333").grid(row=i, column=1, sticky="w", pady=5, padx=15)

        ttk.Separator(content_frame, orient="horizontal").grid(row=len(details), column=0, columnspan=2, sticky="ew", pady=15)

        Label(content_frame, text="Total Amount Due:", font=("Arial", 11, "bold"), bg="white", fg="#001f3f").grid(row=len(details)+1, column=0, sticky="w", pady=5)
        Label(content_frame, text=f"${total_cost:,.2f}", font=("Arial", 12, "bold"), bg="white", fg="#27ae60").grid(row=len(details)+1, column=1, sticky="w", pady=5, padx=15)

        footer_frame = Frame(invoice_popup, bg="white", pady=15)
        footer_frame.pack(fill="x")

        def print_invoice_action():
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"Invoice_PUR_{p_id}.pdf",
                title="Save Purchase Invoice"
            )
            if not file_path:
                return
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                
                c.setFillColorRGB(0, 0.12, 0.25)
                c.rect(0, height - 100, width, 100, fill=1, stroke=0)
                
                c.setFillColorRGB(1, 1, 1)
                c.setFont("Helvetica-Bold", 20)
                c.drawString(40, height - 45, "OFFICIAL PURCHASE INVOICE")
                c.setFont("Helvetica", 10)
                c.drawString(40, height - 65, "Enterprise Inventory & Financial Management System")

                c.setFillColorRGB(0.2, 0.2, 0.2)
                c.setFont("Helvetica-Bold", 11)
                c.drawString(40, height - 140, f"Invoice ID: #INV-PUR-{p_id}")
                c.drawString(40, height - 160, f"Purchase Date: {purchase_date}")
                c.drawString(350, height - 140, f"Supplier: {supplier_name}")

                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(40, height - 220, width - 80, 25, fill=1, stroke=0)
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, height - 213, "Item Description")
                c.drawString(250, height - 213, "Quantity")
                c.drawString(350, height - 213, "Unit Cost")
                c.drawString(470, height - 213, "Total")

                c.setFont("Helvetica", 10)
                c.drawString(50, height - 250, str(item_name))
                c.drawString(250, height - 250, str(quantity))
                c.drawString(350, height - 250, f"${cost_price}")
                c.drawString(470, height - 250, f"${total_cost:,.2f}")

                c.setStrokeColorRGB(0.7, 0.7, 0.7)
                c.line(40, height - 280, width - 40, height - 280)

                c.setFont("Helvetica-Bold", 12)
                c.drawString(350, height - 310, "Total Amount Due:")
                c.setFillColorRGB(0.15, 0.5, 0.2)
                c.drawString(470, height - 310, f"${total_cost:,.2f}")

                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.setFont("Helvetica-Oblique", 9)
                c.drawString(40, 50, "This is a computer-generated document. No signature is required.")
                
                c.save()
                messagebox.showinfo("Export Success", f"Invoice successfully exported and saved to:\n{file_path}", parent=invoice_popup)
                invoice_popup.destroy()
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to generate PDF invoice:\n{e}", parent=invoice_popup)

        Button(footer_frame, text="Print / Export Invoice", bg="#5cb85c", fg="white", font=("Arial", 10, "bold"), width=20, command=print_invoice_action).pack()

    def load_purchase_data(self):
        for item in self.purch_tree.get_children():
            self.purch_tree.delete(item)

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, item_name, supplier_name, cost_price, quantity, purchase_date FROM purchases")
            for row in cursor.fetchall():
                self.purch_tree.insert("", "end", values=row)
            conn.close()

    def open_purchase_popup(self, prefill_item="", prefill_qty=""):
        popup = Toplevel(self.root)
        popup.title("Record Stock Purchase / Cost")
        popup.geometry("380x320")
        popup.config(bg="white")
        popup.grab_set()

        Label(popup, text="New Stock Purchase Record", font=("Arial", 13, "bold"), bg="white", fg="#001f3f").pack(pady=15)

        form_frame = Frame(popup, bg="white")
        form_frame.pack(pady=5)

        fields = [
            ("Item Name:", "item_name"),
            ("Supplier Name:", "supplier_name"),
            ("Cost Price ($):", "cost_price"),
            ("Quantity Needed:", "quantity")
        ]
        entries = {}
        for i, (label_text, key) in enumerate(fields):
            Label(form_frame, text=label_text, font=("Arial", 9, "bold"), bg="white").grid(row=i, column=0, padx=8, pady=8, sticky="e")
            ent = Entry(form_frame, font=("Arial", 10), width=20)
            ent.grid(row=i, column=1, padx=8, pady=8, sticky="w")
            entries[key] = ent

        if prefill_item:
            entries["item_name"].insert(0, prefill_item)
        if prefill_qty:
            entries["quantity"].insert(0, prefill_qty)

        def save_purchase():
            item = entries["item_name"].get().strip()
            supp = entries["supplier_name"].get().strip()
            cost = entries["cost_price"].get().strip()
            qty = entries["quantity"].get().strip()

            if not item or not cost or not qty:
                messagebox.showerror("Error", "Item Name, Cost Price, and Quantity are required.", parent=popup)
                return

            try:
                float(cost)
                int(qty)
            except ValueError:
                messagebox.showerror("Error", "Cost must be a valid number and quantity must be an integer.", parent=popup)
                return

            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO purchases (item_name, supplier_name, cost_price, quantity) VALUES (%s, %s, %s, %s)", (item, supp, cost, qty))
                
                cursor.execute("SELECT id, quantity FROM products WHERE name = %s", (item,))
                prod = cursor.fetchone()

                if prod:
                    new_qty = prod[1] + int(qty)
                    cursor.execute("UPDATE products SET quantity = %s WHERE id = %s", (new_qty, prod[0]))
                else:
                    cursor.execute("INSERT INTO products (name, category, price, quantity, brand, image_path) VALUES (%s, %s, %s, %s, %s, %s)", 
                                   (item, "General", cost, qty, supp if supp else "N/A", "No Image"))

                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Purchase saved and product catalog updated successfully!", parent=popup)
                popup.destroy()
                self.load_purchase_data()

        Button(popup, text="Save Purchase", bg="#5cb85c", fg="white", font=("Arial", 10, "bold"), width=18, command=save_purchase).pack(pady=15)

    # --- 10. SALES HISTORY MODULE ---
    def render_sales_history(self):
        content_bg = self.get_color("bg_main")
        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=5)

        toolbar = Frame(body, bg=content_bg)
        toolbar.pack(fill="x", pady=10)

        Button(toolbar, text="+ Record Sale", bg="#5cb85c", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=self.open_sale_popup).pack(side="left")

        columns = ("ID", "Item Sold", "Selling Price ($)", "Qty Sold", "Total Revenue ($)", "Sale Timestamp")
        self.sales_tree = ttk.Treeview(body, columns=columns, show="headings", height=15)
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=140, anchor="center")
        self.sales_tree.pack(fill="both", expand=True, pady=5)

        self.load_sales_data()

    def load_sales_data(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, item_name, selling_price, quantity_sold, total_revenue, sale_date FROM sales")
            for row in cursor.fetchall():
                self.sales_tree.insert("", "end", values=row)
            conn.close()

    def open_sale_popup(self):
        popup = Toplevel(self.root)
        popup.title("Record New Sale")
        popup.geometry("380x280")
        popup.config(bg="white")
        popup.grab_set()

        Label(popup, text="Record Sales Entry", font=("Arial", 13, "bold"), bg="white", fg="#001f3f").pack(pady=15)

        form_frame = Frame(popup, bg="white")
        form_frame.pack(pady=5)

        fields = [
            ("Item Name:", "item_name"),
            ("Selling Price ($):", "selling_price"),
            ("Quantity Sold:", "quantity_sold")
        ]
        entries = {}
        for i, (label_text, key) in enumerate(fields):
            Label(form_frame, text=label_text, font=("Arial", 9, "bold"), bg="white").grid(row=i, column=0, padx=8, pady=8, sticky="e")
            ent = Entry(form_frame, font=("Arial", 10), width=20)
            ent.grid(row=i, column=1, padx=8, pady=8, sticky="w")
            entries[key] = ent

        def save_sale():
            item = entries["item_name"].get().strip()
            price = entries["selling_price"].get().strip()
            qty_sold = entries["quantity_sold"].get().strip()

            if not item or not price or not qty_sold:
                messagebox.showerror("Error", "All fields are required.", parent=popup)
                return

            try:
                p_val = float(price)
                q_val = int(qty_sold)
            except ValueError:
                messagebox.showerror("Error", "Price must be a number and quantity must be an integer.", parent=popup)
                return

            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, quantity FROM products WHERE name = %s", (item,))
                prod = cursor.fetchone()

                if not prod:
                    messagebox.showerror("Error", "Item not found in your product catalog!", parent=popup)
                    conn.close()
                    return

                current_stock = prod[1]
                if current_stock < q_val:
                    messagebox.showerror("Stock Error", f"Insufficient inventory! Current stock available: {current_stock}", parent=popup)
                    conn.close()
                    return

                total_rev = p_val * q_val
                new_stock = current_stock - q_val

                cursor.execute("UPDATE products SET quantity = %s WHERE id = %s", (new_stock, prod[0]))
                cursor.execute("INSERT INTO sales (item_name, selling_price, quantity_sold, total_revenue) VALUES (%s, %s, %s, %s)", (item, p_val, q_val, total_rev))
                
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Sale recorded successfully!\nTotal Revenue: ${total_rev:.2f}", parent=popup)
                popup.destroy()
                self.load_sales_data()

        Button(popup, text="Complete Sale", bg="#5cb85c", fg="white", font=("Arial", 10, "bold"), width=18, command=save_sale).pack(pady=15)

    # --- 11. LOW STOCK ALERTS MODULE ---
    def render_low_stock_alerts(self):
        content_bg = self.get_color("bg_main")
        body = Frame(self.content_area, bg=content_bg)
        body.pack(fill="both", expand=True, padx=35, pady=5)

        Label(body, text="Items requiring restock (Quantity less than 5)", font=("Arial", 10, "italic"), bg=content_bg, fg="#d9534f").pack(anchor="nw", pady=5)

        toolbar = Frame(body, bg=content_bg)
        toolbar.pack(fill="x", pady=5)

        def raise_selected_restock_request():
            selected = self.alert_tree.focus()
            if not selected:
                messagebox.showerror("Error", "Please select a low stock item from the table first.")
                return
            values = self.alert_tree.item(selected, "values")
            item_name = values[1]
            self.open_purchase_popup(prefill_item=item_name, prefill_qty="10")

        Button(toolbar, text="Raise Restock Request for Selected Item", bg="#f0ad4e", fg="white", font=("Arial", 9, "bold"), padx=10, pady=5, command=raise_selected_restock_request).pack(side="left")

        columns = ("ID", "Name", "Category", "Price ($)", "Current Quantity")
        self.alert_tree = ttk.Treeview(body, columns=columns, show="headings", height=14)
        for col in columns:
            self.alert_tree.heading(col, text=col)
            self.alert_tree.column(col, width=150, anchor="center")
        self.alert_tree.pack(fill="both", expand=True, pady=5)

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, category, price, quantity FROM products WHERE quantity < 5")
            for row in cursor.fetchall():
                self.alert_tree.insert("", "end", values=row)
            conn.close()

# --- APP INITIALIZATION ---
if __name__ == "__main__":
    root = Tk()
    app = InventoryApp(root)
    root.mainloop()