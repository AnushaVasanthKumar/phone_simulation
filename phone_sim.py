import csv
import os
import random
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

#___importantVAR___#
#applc size x*y
APP_WIDTH = 360
APP_HEIGHT = 640
#file dir 
DATABASE_FILE = "database.csv"
LOG_FILE = "logs.csv"
#colors
BG_COLOR = "#0e1116"
CARD_COLOR = "#1b1f27"
ACCENT = "#5c6cff"
TEXT_PRIMARY = "#f5f6fa"
TEXT_SECONDARY = "#9aa3b2"


#if there is no file its gonna make new one with deafults values 
def ensure_files():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["user", "phone", "balance", "2fa_code"])
            writer.writerow(["abdullah", "966123456", "2450.00", ""])
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["timestamp", "user", "action", "amount", "balance_after"])

def read_users():
    with open(DATABASE_FILE, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def write_users(rows):
    with open(DATABASE_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["user", "phone", "balance", "2fa_code"])
        writer.writeheader()
        writer.writerows(rows)
#to apped the logs 
def append_log(user, action, amount, balance_after):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),#for more info check there docs :(
                user,
                action,
                f"{amount:.2f}",
                f"{balance_after:.2f}",
            ]
        )

class PhoneSim:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Phone sim")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)
        self.current_user = None
        self.login_time = None
        self.otp_user = None
        self.last_sms = None
        self.status_frame = None
        self.screen_container = None
        self.time_lbl = None
        self.user_assets = {}
        self.build_status_bar()
        self.build_container()
        self.show_home()
        self.check_session_periodically()

    def is_session_valid(self):
        if not self.current_user or not self.login_time:
            return False
        elapsed = time.time() - self.login_time
        return elapsed < 600

    def check_session_periodically(self):
        if self.current_user and not self.is_session_valid():
            self.current_user = None
            self.login_time = None
        self.root.after(1000, self.check_session_periodically)

    def build_status_bar(self):
        self.status_frame = tk.Frame(self.root, bg=BG_COLOR, height=40)
        self.status_frame.pack(fill="x")
        self.time_lbl = tk.Label(
            self.status_frame,
            text=datetime.now().strftime("%I:%M").lstrip("0"),
            fg=TEXT_PRIMARY,
            bg=BG_COLOR,
            font=("SF Pro Display", 12, "bold"),
        )
        self.time_lbl.pack(side="left", padx=16)
        signal = tk.Label(
            self.status_frame,
            text="STC",
            fg=TEXT_PRIMARY,
            bg=BG_COLOR,
            font=("SF Pro Display", 10),
        )
        signal.pack(side="right", padx=(0, 12))
        battery = tk.Label(
            self.status_frame,
            text="🔋 86%",
            fg=TEXT_PRIMARY,
            bg=BG_COLOR,
            font=("SF Pro Display", 10),
        )
        battery.pack(side="right", padx=12)
        self.update_clock()

    def update_clock(self):
        current_time = datetime.now().strftime("%I:%M").lstrip("0")
        self.time_lbl.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def build_container(self):
        self.screen_container = tk.Frame(self.root, bg=BG_COLOR)
        self.screen_container.pack(fill="both", expand=True)

    def clear_screen(self):
        for widget in self.screen_container.winfo_children():
            widget.destroy()

    def base_screen(self, title_text, back_cb=None):
        wrapper = tk.Frame(self.screen_container, bg=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)
        header = tk.Frame(wrapper, bg=BG_COLOR)
        header.pack(fill="x", pady=(0, 20))
        if back_cb:
            back_btn = tk.Button(
                header,
                text="←",
                command=back_cb,
                bg=BG_COLOR,
                fg=TEXT_PRIMARY,
                relief="flat",
                font=("SF Pro Display", 12, "bold"),
                activebackground=BG_COLOR,
                activeforeground=TEXT_PRIMARY,
                bd=0,
            )
            back_btn.pack(side="left")
        title = tk.Label(
            header,
            text=title_text,
            bg=BG_COLOR,
            fg=TEXT_PRIMARY,
            font=("SF Pro Display", 18, "bold"),
        )
        title.pack(side="left", padx=(10, 0))
        return wrapper

    def show_home(self):
        self.clear_screen()
        wrapper = self.base_screen("Home")
        grid = tk.Frame(wrapper, bg=BG_COLOR)
        grid.pack(pady=40)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)
        self.build_app_icon( #bug1: not in same size #
            grid,
            "SMS 📩",
            "Secure Messages",
            callback=self.show_sms_app,
            row=0,
            column=0,
        )
        self.build_app_icon(
            grid,
            "Bank 🏦",
            "Global Bank",
            callback=self.show_bank_login,
            row=0,
            column=1,
        )
        self.build_app_icon(
            grid,
            "Assets 💰",
            "Buy & Sell",
            callback=self.show_assets_app,
            row=0,
            column=2,
        )

    def build_app_icon(self, parent, title, subtitle, callback, row, column):
        card = tk.Frame(parent, bg=CARD_COLOR, width=100, height=140)
        card.grid(row=row, column=column, padx=8, pady=8, sticky="")
        card.grid_propagate(False)
        card.bind("<Button-1>", lambda _e: callback())
        label = tk.Label(
            card,
            text=title,
            bg=CARD_COLOR,
            fg=TEXT_PRIMARY,
            font=("SF Pro Display", 14, "bold"),
        )
        label.pack(pady=(20, 4))
        sub = tk.Label(
            card,
            text=subtitle,
            bg=CARD_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 8),
        )
        sub.pack()
        label.bind("<Button-1>", lambda _e: callback())
        sub.bind("<Button-1>", lambda _e: callback())

    def show_bank_login(self):
        if self.is_session_valid():
            self.show_bank_dashboard()
            return
        if self.otp_user and not self.current_user:
            self.show_bank_verify()
            return
        self.clear_screen()
        wrapper = self.base_screen("Global Bank", back_cb=self.show_home)
        form = tk.Frame(wrapper, bg=CARD_COLOR, padx=20, pady=20)
        form.pack(fill="x")
        tk.Label(
            form,
            text="Name",
            bg=CARD_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 10),
        ).pack(anchor="w")
        name_entry = tk.Entry(form, font=("SF Pro Display", 12), relief="flat")
        name_entry.pack(fill="x", pady=(0, 14))
        tk.Label(
            form,
            text="Phone",
            bg=CARD_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 10),
        ).pack(anchor="w")
        phone_entry = tk.Entry(form, font=("SF Pro Display", 12), relief="flat")
        phone_entry.pack(fill="x", pady=(0, 14))
        def login():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            rows = read_users()
            for row in rows:
                if row["user"].lower() == name.lower() and row["phone"] == phone:
                    code = f"{random.randint(0, 999999):06d}"
                    row["2fa_code"] = code
                    write_users(rows)
                    self.otp_user = row
                    messagebox.showinfo("Sent", "Code sent to SMS.")
                    self.show_bank_verify()
                    return
            messagebox.showerror("Not found", "User not found.")
        tk.Button(
            wrapper,
            text="Login",
            command=login,
            bg=ACCENT,
            fg="white",
            font=("SF Pro Display", 12, "bold"),
            relief="flat",
            padx=16,
            pady=10,
            cursor="hand2",
            activebackground="#7984ff",
        ).pack(pady=30)

    def show_bank_verify(self):
        self.clear_screen()
        wrapper = self.base_screen("Verify", back_cb=self.show_bank_login)
        prompt = tk.Label(
            wrapper,
            text="Enter the 6-digit code we texted you.",
            bg=BG_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 10),
            wraplength=320,
            justify="left",
        )
        prompt.pack(pady=10, anchor="w")
        otp_entry = tk.Entry(wrapper, font=("SF Pro Display", 14), justify="center")
        otp_entry.pack(fill="x", pady=10)
        def verify():
            code = otp_entry.get().strip()
            if not self.otp_user:
                messagebox.showerror("Error", "No login session.")
                return
            rows = read_users()
            for row in rows:
                if (
                    row["user"] == self.otp_user["user"]
                    and row["phone"] == self.otp_user["phone"]
                ):
                    if row["2fa_code"] == code:
                        row["2fa_code"] = ""
                        write_users(rows)
                        self.current_user = row
                        self.login_time = time.time()
                        self.otp_user = None
                        messagebox.showinfo("Success", "Welcome back!")
                        self.show_bank_dashboard()
                        return
                    break
            messagebox.showerror("Invalid", "Incorrect code.")
        tk.Button(
            wrapper,
            text="Verify",
            command=verify,
            bg=ACCENT,
            fg="white",
            font=("SF Pro Display", 12, "bold"),
            relief="flat",
            padx=16,
            pady=10,
            cursor="hand2",
            activebackground="#7984ff",
        ).pack(pady=20)
        tk.Button(
            wrapper,
            text="Open SMS",
            command=self.show_sms_app,
            bg=CARD_COLOR,
            fg=TEXT_PRIMARY,
            font=("SF Pro Display", 10, "bold"),
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            activebackground="#262b37",
        ).pack()

    def show_bank_dashboard(self):
        if not self.is_session_valid():
            if self.current_user:
                messagebox.showinfo("Session Expired", "Your session has expired. Please login again.")
            self.current_user = None
            self.login_time = None
            self.show_bank_login()
            return
        self.clear_screen()
        wrapper = self.base_screen("Accounts", back_cb=self.show_home)
        balance_card = tk.Frame(wrapper, bg=CARD_COLOR, padx=20, pady=20)
        balance_card.pack(fill="x")
        tk.Label(
            balance_card,
            text="Current Balance",
            bg=CARD_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 10),
        ).pack(anchor="w")
        tk.Label(
            balance_card,
            text=f"${float(self.current_user['balance']):,.2f}",
            bg=CARD_COLOR,
            fg=TEXT_PRIMARY,
            font=("SF Pro Display", 22, "bold"),
        ).pack(anchor="w", pady=(8, 0))
        actions = tk.Frame(wrapper, bg=BG_COLOR)
        actions.pack(pady=30)
        self.build_action(actions, "Check Balance", self.check_balance)
        self.build_action(actions, "Deposit", self.deposit)
        self.build_action(actions, "Withdraw", self.withdraw)

    def build_action(self, parent, title, callback):
        btn = tk.Button(
            parent,
            text=title,
            command=callback,
            width=20,
            bg=ACCENT if title != "Check Balance" else CARD_COLOR,
            fg="white" if title != "Check Balance" else TEXT_PRIMARY,
            font=("SF Pro Display", 12, "bold"),
            relief="flat",
            padx=16,
            pady=10,
            cursor="hand2",
            activebackground="#7984ff",
        )
        btn.pack(pady=8)

    def check_balance(self):
        if not self.is_session_valid():
            if self.current_user:
                messagebox.showinfo("Session Expired", "Your session has expired. Please login again.")
            self.current_user = None
            self.login_time = None
            self.show_bank_login()
            return
        messagebox.showinfo(
            "Balance",
            f"{self.current_user['user']}, your balance is ${float(self.current_user['balance']):,.2f}",
        )

    def deposit(self):
        self._process_transaction("Deposit")

    def withdraw(self):
        self._process_transaction("Withdraw")

    def _process_transaction(self, action):
        if not self.is_session_valid():
            if self.current_user:
                messagebox.showinfo("Session Expired", "Your session has expired. Please login again.")
            self.current_user = None
            self.login_time = None
            self.show_bank_login()
            return
        amt = simpledialog.askfloat(action, f"Amount to {action.lower()}:")
        if amt is None or amt <= 0:
            return
        rows = read_users()
        for row in rows:
            if row["user"] == self.current_user["user"] and row["phone"] == self.current_user["phone"]:
                balance = float(row["balance"])
                if action == "Withdraw" and amt > balance:
                    messagebox.showerror("Funds", "Insufficient funds.")
                    return
                if action == "Deposit":
                    balance += amt
                else:
                    balance -= amt
                row["balance"] = f"{balance:.2f}"
                write_users(rows)
                self.current_user = row
                append_log(row["user"], action, amt, balance)
                self.last_sms = (
                    f"Global Bank: {action} of ${amt:.2f} completed for {row['user']}. "
                    f"New balance: ${balance:.2f}."
                )
                messagebox.showinfo(action, f"{action} successful.\nSMS sent with details.")
                self.show_bank_dashboard()
                return

    def show_sms_app(self):
        self.clear_screen()
        wrapper = self.base_screen("Secure SMS", back_cb=self.show_home)
        bubble = tk.Frame(wrapper, bg=CARD_COLOR, padx=14, pady=14)
        bubble.pack(fill="both", expand=True, pady=20)
        tk.Label(
            bubble,
            text="Global Bank",
            bg=CARD_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 9, "bold"),
        ).pack(anchor="w")
        text_box = tk.Text(
            bubble,
            bg=CARD_COLOR,
            fg=TEXT_PRIMARY,
            font=("SF Pro Display", 12),
            relief="flat",
            wrap="word",
            height=5,
            cursor="xterm",
        )
        text_box.pack(fill="both", expand=True, pady=(8, 0))
        text_box.insert("1.0", self.sms_content())
        self.make_sms_copyable(text_box)
        copy_hint = tk.Label(
            wrapper,
            text="ez copy then switch back to the bank app",
            bg=BG_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 8),
            wraplength=320,
            justify="left",
        )
        copy_hint.pack(pady=(10, 0), anchor="w")

    def make_sms_copyable(self, widget):
        def on_key(event):
            ctrl = (event.state & 0x4) != 0
            if ctrl and event.keysym.lower() in ("c", "a", "insert"):
                return
            return "break"
        widget.bind("<KeyPress>", on_key)
        widget.bind("<<Paste>>", lambda _e: "break")
        widget.bind("<Control-v>", lambda _e: "break")
        widget.bind("<Button-2>", lambda _e: "break")
        widget.config(cursor="xterm")

    def sms_content(self):
        rows = read_users()
        latest_code = ""
        latest_user = ""
        for row in rows:
            if row["2fa_code"]:
                latest_user = row["user"]
                latest_code = row["2fa_code"]
        if latest_code:
            return (
                f"Hi {latest_user}, your 2FA code is {latest_code}. "
                "This code expires in 5 minutes. Copy it and confirm your login."
            )
        if self.last_sms:
            return self.last_sms
        return "No new messages. Launch the bank app to request a login code or make a transaction."

    def show_assets_app(self):
        if not self.is_session_valid():
            if self.current_user:
                messagebox.showinfo("Session Expired", "Your session has expired. Please login again.")
                self.current_user = None
                self.login_time = None
            else:
                messagebox.showinfo("Login Required", "Please login to the bank app first to access assets.")
            self.show_bank_login()
            return
        self.clear_screen()
        wrapper = self.base_screen("Assets", back_cb=self.show_home)
        balance_card = tk.Frame(wrapper, bg=CARD_COLOR, padx=20, pady=20)
        balance_card.pack(fill="x", pady=(0, 20))
        tk.Label(
            balance_card,
            text="Wallet Balance",
            bg=CARD_COLOR,
            fg=TEXT_SECONDARY,
            font=("SF Pro Display", 10),
        ).pack(anchor="w")
        tk.Label(
            balance_card,
            text=f"${float(self.current_user['balance']):,.2f}",
            bg=CARD_COLOR,
            fg=TEXT_PRIMARY,
            font=("SF Pro Display", 20, "bold"),
        ).pack(anchor="w", pady=(8, 0))
        actions = tk.Frame(wrapper, bg=BG_COLOR)
        actions.pack(pady=20)
        self.build_action(actions, "Buy House", lambda: self.buy_asset("house"))
        self.build_action(actions, "Buy Crypto", lambda: self.buy_asset("crypto"))
        self.build_action(actions, "Sell House", lambda: self.sell_asset("house"))
        self.build_action(actions, "Sell Crypto", lambda: self.sell_asset("crypto"))
        self.build_action(actions, "View Assets", self.view_assets)

    def buy_asset(self, asset_type):
        if not self.is_session_valid():
            if self.current_user:
                messagebox.showinfo("Session Expired", "Your session has expired. Please login again.")
            self.current_user = None
            self.login_time = None
            self.show_bank_login()
            return
        if asset_type == "house":
            price = simpledialog.askfloat("Buy House", "Enter house price:")
            if price is None or price <= 0:
                return
            asset_name = simpledialog.askstring("Buy House", "Enter house address/name:")
            if not asset_name:
                return
        else:
            price = simpledialog.askfloat("Buy Crypto", "Enter amount to invest:")
            if price is None or price <= 0:
                return
            asset_name = simpledialog.askstring("Buy Crypto", "Enter crypto symbol (e.g., BTC, ETH):")
            if not asset_name:
                return
        rows = read_users()
        for row in rows:
            if row["user"] == self.current_user["user"] and row["phone"] == self.current_user["phone"]:
                balance = float(row["balance"])
                if price > balance:
                    messagebox.showerror("Funds", "Insufficient funds.")
                    return
                balance -= price
                row["balance"] = f"{balance:.2f}"
                write_users(rows)
                self.current_user = row
                username = row["user"]
                if username not in self.user_assets:
                    self.user_assets[username] = {"houses": [], "crypto": []}
                asset_data = {
                    "name": asset_name,
                    "price": price,
                    "type": asset_type,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                if asset_type == "house":
                    self.user_assets[username]["houses"].append(asset_data)
                else:
                    self.user_assets[username]["crypto"].append(asset_data)
                append_log(row["user"], f"Buy {asset_type.title()}", price, balance)
                self.last_sms = (
                    f"Assets App: Purchased {asset_type} '{asset_name}' for ${price:.2f}. "
                    f"New balance: ${balance:.2f}."
                )
                messagebox.showinfo("Success", f"Purchase successful!\nSMS sent with details.")
                self.show_assets_app()
                return

    def sell_asset(self, asset_type):
        if not self.is_session_valid():
            if self.current_user:
                messagebox.showinfo("Session Expired", "Your session has expired. Please login again.")
            self.current_user = None
            self.login_time = None
            self.show_bank_login()
            return
        username = self.current_user["user"]
        if username not in self.user_assets:
            self.user_assets[username] = {"houses": [], "crypto": []}
        assets_list = self.user_assets[username]["houses"] if asset_type == "house" else self.user_assets[username]["crypto"]
        if not assets_list:
            messagebox.showinfo("No Assets", f"You don't have any {asset_type} to sell.")
            return
        asset_names = [f"{i+1}. {asset['name']} (${asset['price']:.2f})" for i, asset in enumerate(assets_list)]
        choice = simpledialog.askstring(
            f"Sell {asset_type.title()}",
            f"Available {asset_type}s:\n" + "\n".join(asset_names) + "\n\nEnter number to sell:"
        )
        if not choice:
            return
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(assets_list):
                messagebox.showerror("Invalid", "Invalid selection.")
                return
        except ValueError:
            messagebox.showerror("Invalid", "Please enter a valid number.")
            return
        asset = assets_list[idx]
        original_price = asset["price"]
        profit_factor = random.uniform(0.8, 1.3)
        sell_price = original_price * profit_factor
        rows = read_users()
        for row in rows:
            if row["user"] == self.current_user["user"] and row["phone"] == self.current_user["phone"]:
                balance = float(row["balance"])
                balance += sell_price
                row["balance"] = f"{balance:.2f}"
                write_users(rows)
                self.current_user = row
                assets_list.pop(idx)
                append_log(row["user"], f"Sell {asset_type.title()}", sell_price, balance)
                profit_loss = sell_price - original_price
                profit_text = f"Profit: ${profit_loss:.2f}" if profit_loss >= 0 else f"Loss: ${abs(profit_loss):.2f}"
                self.last_sms = (
                    f"Assets App: Sold {asset_type} '{asset['name']}' for ${sell_price:.2f}. "
                    f"{profit_text}. New balance: ${balance:.2f}."
                )
                messagebox.showinfo("Success", f"Sale successful!\nSMS sent with details.")
                self.show_assets_app()
                return

    def view_assets(self):
        if not self.is_session_valid():
            if self.current_user:
                messagebox.showinfo("Session Expired", "Your session has expired. Please login again.")
            self.current_user = None
            self.login_time = None
            self.show_bank_login()
            return
        username = self.current_user["user"]
        if username not in self.user_assets:
            self.user_assets[username] = {"houses": [], "crypto": []}
        houses = self.user_assets[username]["houses"]
        crypto = self.user_assets[username]["crypto"]
        if not houses and not crypto:
            messagebox.showinfo("No Assets", "You don't own any assets yet.")
            return
        info = "Your Assets:\n\n"
        if houses:
            info += "Houses:\n"
            for house in houses:
                info += f"  • {house['name']} - ${house['price']:.2f} (Bought: {house['date']})\n"
            info += "\n"
        if crypto:
            info += "Crypto:\n"
            for coin in crypto:
                info += f"  • {coin['name']} - ${coin['price']:.2f} (Bought: {coin['date']})\n"
        messagebox.showinfo("My Assets", info)

    def run(self):
        self.root.mainloop()

def launch_phone():
    ensure_files()
    app = PhoneSim()
    app.run()

if __name__ == "__main__":
    launch_phone()
