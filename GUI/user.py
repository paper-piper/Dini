import wx


class DiniCoinExchange(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize state
        self.balance = 1000
        self.transactions = [
            {"type": "Received", "amount": 50, "from": "Alice"},
            {"type": "Sent", "amount": 30, "to": "Bob"},
            {"type": "Bought", "amount": 100},
            {"type": "Sold", "amount": 20},
        ]

        # Setup the UI
        self.panel = wx.Panel(self)
        self.SetTitle("Dini Coin Exchange")
        self.SetSize((600, 400))

        # Header
        header = wx.StaticText(self.panel, label="Dini Coin Exchange", style=wx.ALIGN_CENTER)
        header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        header.SetForegroundColour(wx.Colour(255, 255, 255))
        header.SetBackgroundColour(wx.Colour(128, 0, 128))
        header.SetSize(self.GetSize())
        header.SetPosition((0, 0))

        # Balance display
        self.balance_label = wx.StaticText(self.panel, label=f"Your Balance: {self.balance} DINI")
        self.balance_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.balance_label.SetPosition((20, 50))

        # Tabs
        self.notebook = wx.Notebook(self.panel)
        self.notebook.SetPosition((20, 80))
        self.notebook.SetSize((550, 200))

        self.create_transfer_tab()
        self.create_buy_tab()
        self.create_sell_tab()

        # Recent Transactions
        recent_transactions_label = wx.StaticText(self.panel, label="Recent Transactions:")
        recent_transactions_label.SetPosition((20, 290))
        self.transactions_list = wx.ListBox(self.panel, pos=(20, 310), size=(550, 80))
        self.update_transactions()

    def create_transfer_tab(self):
        transfer_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(transfer_panel, "Transfer")

        recipient_label = wx.StaticText(transfer_panel, label="Recipient Address:", pos=(10, 10))
        self.recipient_input = wx.TextCtrl(transfer_panel, pos=(150, 10), size=(200, -1))

        amount_label = wx.StaticText(transfer_panel, label="Amount (DINI):", pos=(10, 50))
        self.transfer_amount_input = wx.TextCtrl(transfer_panel, pos=(150, 50), size=(100, -1))

        transfer_button = wx.Button(transfer_panel, label="Transfer", pos=(10, 90))
        transfer_button.Bind(wx.EVT_BUTTON, self.handle_transfer)

    def create_buy_tab(self):
        buy_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(buy_panel, "Buy")

        amount_label = wx.StaticText(buy_panel, label="Amount to Buy (DINI):", pos=(10, 10))
        self.buy_amount_input = wx.TextCtrl(buy_panel, pos=(200, 10), size=(100, -1))

        buy_button = wx.Button(buy_panel, label="Buy", pos=(10, 50))
        buy_button.Bind(wx.EVT_BUTTON, self.handle_buy)

    def create_sell_tab(self):
        sell_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(sell_panel, "Sell")

        amount_label = wx.StaticText(sell_panel, label="Amount to Sell (DINI):", pos=(10, 10))
        self.sell_amount_input = wx.TextCtrl(sell_panel, pos=(200, 10), size=(100, -1))

        sell_button = wx.Button(sell_panel, label="Sell", pos=(10, 50))
        sell_button.Bind(wx.EVT_BUTTON, self.handle_sell)

    def handle_transfer(self, event):
        recipient = self.recipient_input.GetValue()
        amount = int(self.transfer_amount_input.GetValue() or 0)

        if amount > self.balance:
            wx.MessageBox("Insufficient balance", "Error", wx.ICON_ERROR)
            return

        self.balance -= amount
        self.transactions.insert(0, {"type": "Sent", "amount": amount, "to": recipient})
        self.update_transactions()

    def handle_buy(self, event):
        amount = int(self.buy_amount_input.GetValue() or 0)

        self.balance += amount
        self.transactions.insert(0, {"type": "Bought", "amount": amount})
        self.update_transactions()

    def handle_sell(self, event):
        amount = int(self.sell_amount_input.GetValue() or 0)

        self.balance -= amount
        self.transactions.insert(0, {"type": "Sold", "amount": amount})
        self.update_transactions()

    def update_transactions(self):
        self.balance_label.SetLabel(f"Your Balance: {self.balance} DINI")
        self.transactions_list.Clear()
        for tx in self.transactions[:5]:
            details = f"{tx['type']} {tx['amount']} DINI"
            if "to" in tx:
                details += f" to {tx['to']}"
            elif "from" in tx:
                details += f" from {tx['from']}"
            self.transactions_list.Append(details)


# Run the Application
if __name__ == "__main__":
    app = wx.App()
    frame = DiniCoinExchange(None)
    frame.Show()
    app.MainLoop()
