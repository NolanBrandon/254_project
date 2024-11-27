import gi
import requests

# Import the necessary GTK module
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Function to fetch exchange rates from the API
def get_exchange_rate(from_currency, to_currency):
    # Replace 'YOUR_API_KEY' (random string below) with the actual key you got from ExchangeRate-API
    api_url = f"https://v6.exchangerate-api.com/v6/56a5a0f9c6833acac63c2498/latest/{from_currency}"
    response = requests.get(api_url)
    data = response.json()
    
    if data['result'] == 'success':
        rate = data['conversion_rates'].get(to_currency)
        if rate:
            return rate
        else:
            print(f"Conversion rate for {to_currency} not found.")
            return None
    else:
        print(f"Error fetching exchange rates: {data['error-type']}")
        return None

# Define the GUI for the Currency Converter
class CurrencyConverter(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Currency Converter")

        # Main VBox container for widgets
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        # Label for the amount input field
        self.amount_label = Gtk.Label(label="Amount:")
        self.box.pack_start(self.amount_label, True, True, 0)
        
        # Entry field for the amount
        self.amount_entry = Gtk.Entry()
        self.box.pack_start(self.amount_entry, True, True, 0)

        # Label and Combobox for 'From' currency
        self.from_currency_label = Gtk.Label(label="From Currency:")
        self.box.pack_start(self.from_currency_label, True, True, 0)
        self.from_currency_combo = Gtk.ComboBoxText()
        self.from_currency_combo.append_text("USD")
        self.from_currency_combo.append_text("EUR")
        self.from_currency_combo.append_text("GBP")
        self.from_currency_combo.set_active(0)
        self.box.pack_start(self.from_currency_combo, True, True, 0)

        # Label and Combobox for 'To' currency
        self.to_currency_label = Gtk.Label(label="To Currency:")
        self.box.pack_start(self.to_currency_label, True, True, 0)
        self.to_currency_combo = Gtk.ComboBoxText()
        self.to_currency_combo.append_text("EUR")
        self.to_currency_combo.append_text("USD")
        self.to_currency_combo.append_text("GBP")
        self.to_currency_combo.set_active(0)
        self.box.pack_start(self.to_currency_combo, True, True, 0)

        # Button to perform conversion
        self.convert_button = Gtk.Button(label="Convert")
        self.convert_button.connect("clicked", self.on_convert_clicked)
        self.box.pack_start(self.convert_button, True, True, 0)

        # Label to display the result
        self.result_label = Gtk.Label(label="Result: ")
        self.box.pack_start(self.result_label, True, True, 0)

    def on_convert_clicked(self, widget):
        # Get the user inputs
        amount = self.amount_entry.get_text()
        from_currency = self.from_currency_combo.get_active_text()
        to_currency = self.to_currency_combo.get_active_text()

        if amount.isdigit():  # Check if the input is a valid number
            amount = float(amount)
            rate = get_exchange_rate(from_currency, to_currency)

            if rate:
                result = amount * rate
                # Update the result label with the conversion result
                self.result_label.set_text(f"Result: {amount} {from_currency} = {result:.2f} {to_currency}")
        else:
            # Show error if the input amount is invalid
            self.result_label.set_text("Please enter a valid amount.")

# Main application loop
window = CurrencyConverter()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
