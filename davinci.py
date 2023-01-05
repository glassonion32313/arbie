



import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import importlib
import time
import ccxt
import web3
from web3 import Web3
import pip
import auto_metamask
#checks for updates and installs them
def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

#loops through all dependancies and installs them if they aren't already installed
for package in ("ccxt","web3","autometamask","Gspread","Panda","importlib","time"):
    try:
        __import__(package)
    except ImportError:
        install(package)
#can this prompt user to login to google thru gui then automaticly obtain creditals needed and save to creds.json?
#User authentication using Google credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)

# Create a GUI for users to sign in and input their API keys
def login_GUI():
    # Create a window
    window = tk.Tk()

    # Set the window title
    window.title("Flash Loan Arbitrage Bot")

    # Set the window size
    window.geometry('350x200')

    # Add a label
    lbl_username = tk.Label(window, text="Username")
    lbl_username.grid(column=0, row=0)

    # Add a text box
    txt_username = tk.Entry(window, width=20)
    txt_username.grid(column=1, row=0)

    # Add a label
    lbl_api_key = tk.Label(window, text="API Key")
    lbl_api_key.grid(column=0, row=1)

    # Add a text box
    txt_api_key = tk.Entry(window, width=20)
    txt_api_key.grid(column=1, row=1)

    # Add a button
    btn_login = tk.Button(window, text="Login", command=lambda: login(txt_username.get(), txt_api_key.get()))
    btn_login.grid(column=1, row=2)

    # Start the window's event-loop
    window.mainloop()

# Function to authenticate user
def login(username, api_key):
    # Check if the username and API key are valid
    if username == "" or api_key == "":
        # Display an error message
        tk.messagebox.showerror("Error", "Please enter your username and API key")
    else:
        # Authenticate the user
        authenticated = authenticate(username, api_key)
        if authenticated:
            # Display a success message
            tk.messagebox.showinfo("Success", "You have successfully logged in")
        else:
            # Display an error message
            tk.messagebox.showerror("Error", "Your username or API key is incorrect")

# Function to authenticate user
def authenticate(username, api_key):
    # Connect to the Google Sheet
    sheet = client.open('sheet').sheet1

    # Check if the username and API key are valid
    data = sheet.get_all_records()
    for row in data:
        if row['Username'] == username and row['API Key'] == api_key:
            return True
    return False

# Exchange monitor
def exchange_monitor(exchanges):
    # Create a Pandas DataFrame to store the order book data
    df = pd.DataFrame(columns=['Exchange', 'Market', 'Type', 'Price', 'Quantity'])

    # Loop through the list of exchanges
    for exchange in exchanges:
        # Load the exchange module
        exchange_module = importlib.import_module('ccxt.'+exchange)

        # Create an instance of the exchange
        exchange = getattr(exchange_module, exchange)()

        # Get the list of markets
        markets = exchange.load_markets()

        # Loop through the markets
        for market in markets:
            # Get the order book data
            order_book = exchange.fetch_order_book(market)

            # Loop through the bids
            for bid in order_book['bids']:
                # Append the data to the DataFrame
                df = df.append({'Exchange': exchange.name, 'Market': market, 'Type': 'bid', 'Price': bid[0], 'Quantity': bid[1]}, ignore_index=True)

            # Loop through the asks
            for ask in order_book['asks']:
                # Append the data to the DataFrame
                df = df.append({'Exchange': exchange.name, 'Market': market, 'Type': 'ask', 'Price': ask[0], 'Quantity': ask[1]}, ignore_index=True)

    # Look for arbitrage opportunities
    for index, row in df.iterrows():
        # Check if the bid/ask prices are too far apart
        if row['Type'] == 'bid':
            # Get the ask price from the same market on a different exchange
            ask = df[(df['Market'] == row['Market']) & (df['Exchange'] != row['Exchange']) & (df['Type'] == 'ask')]['Price'].min()

            # Check if the bid/ask prices are far enough apart
            if ask - row['Price'] > 0.1:
                # Create a flash loan
                flash_loan = MetaMask.create_flash_loan()

                # Submit flash loan
                MetaMask.submit_flash_loan(flash_loan)

                # Buy at the lower price
                exchange1 = getattr(exchange_module, row['Exchange'])()
                exchange1.create_market_buy_order(row['Market'], row['Quantity'], row['Price'])

                # Sell at the higher price
                exchange2 = getattr(exchange_module, df[(df['Market'] == row['Market']) & (df['Exchange'] != row['Exchange'])]['Exchange'].iloc[0])()
                exchange2.create_market_sell_order(row['Market'], row['Quantity'], ask)

                # Calculate the profit
                profit = ask - row['Price']

                # Split the profit 50/50
                half_profit = profit/2

                # Further the bot's ability to make profitable trades
                # Code to use the other half of the profit to further the bot's ability to make profitable trades

                # Deposit the other half of the profit into the user's wallet
                wallet_address = MetaMask.get_wallet_address()
                web3.eth.sendTransaction({'to':wallet_address, 'from': flash_loan.address, 'value': half_profit})

# Start the bot
def start_bot():
    # Get the list of exchanges
    exchanges = ['binance', 'bitfinex', 'bitmex', 'kraken', 'huobi']

    # Start the exchange monitor
    while True:
        exchange_monitor(exchanges)
        time.sleep(60)

# Start the bot
start_bot()
