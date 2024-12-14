import gi
import requests
import time

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Hardcoded Average prices for items (USD)
AVG_BIGMAC_PRICE = 5.65  # Global average Big Mac price in USD (2022)
AVG_FRIES_PRICE = 2.50  # Global average Medium Fries price in USD
AVG_DRINK_PRICE = 1.80  # Global average Medium Drink price in USD

# Cache for crypto prices to avoid excessive API calls
crypto_cache = {}
cache_time = 60  # Cache duration in seconds

# Function to get cryptocurrency price from CoinGecko with API key
def get_crypto_price(crypto, fiat):
    """Get cryptocurrency price from CoinGecko API and cache it."""
    current_time = time.time()
    if crypto in crypto_cache and (current_time - crypto_cache[crypto]['time']) < cache_time:
        return crypto_cache[crypto]['price']
    
    BASE_URL = "https://api.coingecko.com/api/v3/simple/price"
    url = f"{BASE_URL}?ids={crypto}&vs_currencies={fiat}"
    response = requests.get(url)

    try:
        data = response.json()
        if crypto in data and fiat in data[crypto]:
            price = data[crypto][fiat]
            # Cache the price and timestamp
            crypto_cache[crypto] = {'price': price, 'time': current_time}
            return price
    except Exception as e:
        print(f"Error: {e}")
    
    return None

# Function to fetch exchange rates for fiat currencies (e.g., USD to EUR)
def get_exchange_rate_from_currency(from_currency, to_currency):
    """Fetch exchange rates between fiat currencies."""
    BASE_URL = "https://api.exchangerate-api.com/v4/latest"
    url = f"{BASE_URL}/{from_currency.lower()}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "rates" in data and to_currency.upper() in data["rates"]:
            return data["rates"][to_currency.upper()]
    except Exception as e:
        print(f"Error: {e}")
    return None

# Function to get exchange rates (both fiat and cryptocurrency)
def get_exchange_rate(from_currency, to_currency):
    """Get exchange rates or cryptocurrency rates."""
    if to_currency.lower() == "bigmac":
        return AVG_BIGMAC_PRICE
    elif to_currency.lower() == "fries":
        return AVG_FRIES_PRICE
    elif to_currency.lower() == "drink":
        return AVG_DRINK_PRICE
    elif is_crypto(from_currency) and is_crypto(to_currency):
        from_price = get_crypto_price(from_currency, "usd")
        to_price = get_crypto_price(to_currency, "usd")
        if from_price and to_price:
            return from_price / to_price
    elif is_crypto(from_currency):
        return get_crypto_price(from_currency, to_currency)
    elif is_crypto(to_currency):
        price = get_crypto_price(to_currency, "usd")
        if price:
            return 1 / price
        return None
    else:
        return get_exchange_rate_from_currency(from_currency, to_currency)

# Check if the currency is cryptocurrency
def is_crypto(currency):
    crypto_currencies = ["bitcoin", "ethereum", "litecoin", "dogecoin", "xrp", "binancecoin", "solana", "cardano", "polkadot", "tether"]
    return currency.lower() in crypto_currencies

# The GUI code
class CurrencyConverter(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Currency Converter")
        self.set_default_size(800, 600)  # Increased default size
        self.set_border_width(20)

        # Add a CSS provider to style the window
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        GtkWindow {
            background-color: #f5f5f5;
        }
        GtkLabel {
            font-size: 28px;  /* Increased font size for labels */
            color: #333;
        }
        GtkEntry {
            padding: 16px;
            font-size: 32px;  /* Increased font size for input field */
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        GtkButton {
            padding: 16px 24px;
            font-size: 32px;  /* Increased font size for button */
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            border: none;
        }
        GtkButton:hover {
            background-color: #45a049;
        }
        GtkComboBoxText {
            font-size: 28px;  /* Increased font size for combo box */
            padding: 16px;
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        GtkBox {
            margin-top: 30px;
            margin-bottom: 30px;
            margin-left: 40px;
            margin-right: 40px;
        }
        """)

        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Create a Box to hold everything and make it resizable
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)  # Increased spacing
        self.main_box.set_homogeneous(False)  # Allow components to grow/shrink differently
        self.add(self.main_box)

        # Create a Grid layout to organize the widgets inside the box
        self.grid = Gtk.Grid()
        self.grid.set_row_homogeneous(True)  # Allow rows to grow/shrink proportionally
        self.grid.set_column_homogeneous(True)  # Allow columns to grow/shrink uniformly
        self.main_box.pack_start(self.grid, True, True, 0)

        # Amount input
        self.amount_label = Gtk.Label(label="Amount:")
        self.grid.attach(self.amount_label, 0, 0, 1, 1)

        self.amount_entry = Gtk.Entry()
        self.grid.attach(self.amount_entry, 1, 0, 2, 1)

        # From Currency ComboBox
        self.from_currency_label = Gtk.Label(label="From Currency:")
        self.grid.attach(self.from_currency_label, 0, 1, 1, 1)

        self.from_currency_combo = Gtk.ComboBoxText()
        self.populate_currency_combobox(self.from_currency_combo)
        self.grid.attach(self.from_currency_combo, 1, 1, 2, 1)

        # To Currency ComboBox
        self.to_currency_label = Gtk.Label(label="To Currency:")
        self.grid.attach(self.to_currency_label, 0, 2, 1, 1)

        self.to_currency_combo = Gtk.ComboBoxText()
        self.populate_currency_combobox(self.to_currency_combo)
        self.grid.attach(self.to_currency_combo, 1, 2, 2, 1)

        # Convert button
        self.convert_button = Gtk.Button(label="Convert")
        self.convert_button.connect("clicked", self.on_convert_clicked)
        self.grid.attach(self.convert_button, 0, 3, 3, 1)

        # Result label
        self.result_label = Gtk.Label(label="Result: ")
        self.grid.attach(self.result_label, 0, 4, 3, 1)

        # Center the grid within the window and make it resizable
        self.main_box.set_homogeneous(True)
        self.grid.set_hexpand(True)  # Allow the grid to expand horizontally
        self.grid.set_vexpand(True)  # Allow the grid to expand vertically

    def populate_currency_combobox(self, combobox):
        """Populate ComboBox with currencies."""
        currencies = [
            "USD", "EUR", "GBP", "INR", "AUD", "CAD", "bitcoin", "ethereum", "litecoin",
            "dogecoin", "xrp", "binancecoin", "solana", "cardano", "polkadot", "tether",
            "BigMac", "Fries", "Drink"
        ]
        for currency in currencies:
            combobox.append_text(currency)
        combobox.set_active(0)

    def on_convert_clicked(self, widget):
        amount = self.amount_entry.get_text()
        from_currency = self.from_currency_combo.get_active_text()
        to_currency = self.to_currency_combo.get_active_text()

        if not amount:
            self.result_label.set_text("Please enter an amount.")
            return

        try:
            amount = float(amount)  # Try to convert the amount to float (allows decimals)
        except ValueError:
            self.result_label.set_text("Invalid amount entered.")  # Show an error if conversion fails
            return

        # Convert BigMacs, Fries, and Drinks to Fiat
        if from_currency.lower() in ["bigmac", "fries", "drink"]:
            if from_currency.lower() == "bigmac":
                usd_amount = amount * AVG_BIGMAC_PRICE
            elif from_currency.lower() == "fries":
                usd_amount = amount * AVG_FRIES_PRICE
            elif from_currency.lower() == "drink":
                usd_amount = amount * AVG_DRINK_PRICE

            # Convert USD to the target currency (fiat or crypto)
            if to_currency.lower() in ["usd", "gbp", "eur", "inr", "aud", "cad"]:
                rate = get_exchange_rate("usd", to_currency)
                if rate:
                    result = usd_amount * rate
                    self.result_label.set_text(f"Result: {result:.2f} {to_currency}")
                else:
                    self.result_label.set_text("Error: Could not fetch exchange rate.")
            elif is_crypto(to_currency):
                rate = get_crypto_price(to_currency, "usd")
                if rate:
                    result = usd_amount / rate
                    self.result_label.set_text(f"Result: {result:.2f} {to_currency}")
                else:
                    self.result_label.set_text("Error: Could not fetch crypto rate.")
            else:
                self.result_label.set_text("Error: Unsupported target currency.")
            return

        # Handle regular currency-to-currency conversion (fiat or crypto)
        rate = get_exchange_rate(from_currency, to_currency)
        if rate:
            result = amount * rate
            self.result_label.set_text(f"Result: {result:.2f} {to_currency}")
        else:
            self.result_label.set_text("Error: Could not fetch conversion rate.")

# Run the application
if __name__ == "__main__":
    window = CurrencyConverter()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
