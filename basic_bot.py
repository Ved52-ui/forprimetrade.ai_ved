import tkinter as tk
from tkinter import ttk, messagebox
from binance.client import Client
from binance.exceptions import BinanceAPIException
import threading

# ---- CONFIG ----
BG_COLOR = "#121212"
FG_COLOR = "#ffffff"
ACCENT = "#00ff88"

class BinanceGUIBot:
    def __init__(self, root):
        self.root = root
        self.root.title("💹 Binance Trading Bot")
        self.root.geometry("700x500")
        self.root.config(bg=BG_COLOR)

        self.client = None

        self.build_ui()

    def build_ui(self):
        title = tk.Label(self.root, text="BINANCE TRADING BOT", font=("Arial", 22, "bold"), fg=ACCENT, bg=BG_COLOR)
        title.pack(pady=10)

        frame_api = tk.LabelFrame(self.root, text="API Credentials", fg=ACCENT, bg=BG_COLOR, font=("Arial", 12, "bold"), padx=10, pady=10)
        frame_api.pack(padx=15, pady=10, fill="x")

        tk.Label(frame_api, text="API Key:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, sticky="w")
        self.api_key_entry = tk.Entry(frame_api, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame_api, text="Secret Key:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0, sticky="w")
        self.api_secret_entry = tk.Entry(frame_api, width=50, show="*")
        self.api_secret_entry.grid(row=1, column=1, padx=5)

        connect_btn = ttk.Button(frame_api, text="Connect", command=self.connect_api)
        connect_btn.grid(row=2, column=0, columnspan=2, pady=8)

        # Trading Frame
        frame_trade = tk.LabelFrame(self.root, text="Place Order", fg=ACCENT, bg=BG_COLOR, font=("Arial", 12, "bold"), padx=10, pady=10)
        frame_trade.pack(padx=15, pady=10, fill="x")

        tk.Label(frame_trade, text="Symbol (e.g., BTCUSDT):", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, sticky="w")
        self.symbol_entry = tk.Entry(frame_trade, width=20)
        self.symbol_entry.grid(row=0, column=1)

        tk.Label(frame_trade, text="Quantity:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0, sticky="w")
        self.qty_entry = tk.Entry(frame_trade, width=20)
        self.qty_entry.grid(row=1, column=1)

        tk.Label(frame_trade, text="Order Type:", bg=BG_COLOR, fg=FG_COLOR).grid(row=2, column=0, sticky="w")
        self.order_type = ttk.Combobox(frame_trade, values=["MARKET", "LIMIT"], width=17)
        self.order_type.current(0)
        self.order_type.grid(row=2, column=1)

        tk.Label(frame_trade, text="Side:", bg=BG_COLOR, fg=FG_COLOR).grid(row=3, column=0, sticky="w")
        self.side = ttk.Combobox(frame_trade, values=["BUY", "SELL"], width=17)
        self.side.current(0)
        self.side.grid(row=3, column=1)

        place_btn = ttk.Button(frame_trade, text="Place Order", command=self.place_order_thread)
        place_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Log Area
        frame_log = tk.LabelFrame(self.root, text="Logs", fg=ACCENT, bg=BG_COLOR, font=("Arial", 12, "bold"))
        frame_log.pack(padx=15, pady=10, fill="both", expand=True)

        self.log_text = tk.Text(frame_log, bg="#1e1e1e", fg="#00ff88", height=10)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def connect_api(self):
        key = self.api_key_entry.get().strip()
        secret = self.api_secret_entry.get().strip()
        if not key or not secret:
            messagebox.showerror("Error", "Please enter both API Key and Secret.")
            return

        try:
            self.client = Client(key, secret)
            account = self.client.get_account()
            self.log("✅ Connected to Binance.com successfully!")
            balances = [b for b in account["balances"] if float(b["free"]) > 0]
            self.log(f"Available Balances: {balances}")
            messagebox.showinfo("Connected", "API Connected Successfully!")
        except BinanceAPIException as e:
            self.log(f"❌ Connection failed: {e}")
            messagebox.showerror("Connection Failed", str(e))

    def place_order_thread(self):
        threading.Thread(target=self.place_order).start()

    def place_order(self):
        if not self.client:
            messagebox.showerror("Error", "Please connect API first!")
            return

        symbol = self.symbol_entry.get().strip().upper()
        qty = self.qty_entry.get().strip()
        side = self.side.get()
        order_type = self.order_type.get()

        if not symbol or not qty:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            qty = float(qty)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number.")
            return

        try:
            self.log(f"Placing {side} {order_type} order for {symbol}, qty: {qty}")
            if order_type == "MARKET":
                order = self.client.order_market(symbol=symbol, side=side, quantity=qty)
            else:
                # Example Limit order at current price
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                order = self.client.order_limit(symbol=symbol, side=side, quantity=qty, price=str(price))
            
            self.log(f"✅ Order Placed: {order}")
            messagebox.showinfo("Success", "Order placed successfully!")
        except BinanceAPIException as e:
            self.log(f"❌ API Error: {e}")
            messagebox.showerror("API Error", str(e))
        except Exception as e:
            self.log(f"⚠️ Error: {e}")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 10, "bold"), background=ACCENT, padding=6)
    app = BinanceGUIBot(root)
    root.mainloop()
