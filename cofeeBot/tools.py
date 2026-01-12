# tools.py
import random
from langchain_core.tools import tool

# --- UPDATED MENU BASED ON YOUR INSTRUCTIONS ---
MENU = {
    # Espresso-Based Classics
    "espresso": 3.00, "double espresso": 4.00, "americano": 3.50,
    "cappuccino": 4.50, "latte": 4.50, "flat white": 4.50,
    "mocha": 5.00, "caramel latte": 5.00, "vanilla latte": 5.00,
    "hazelnut latte": 5.00,
    # Iced & Cold
    "iced latte": 5.00, "iced americano": 4.00, "iced mocha": 5.50,
    "cold brew": 4.50, "vanilla cold brew": 5.00, "iced caramel macchiato": 5.50,
    # Non-Coffee
    "hot chocolate": 4.50, "iced chocolate": 5.00, "chai latte": 4.50,
    "matcha latte": 5.00,
    "english breakfast tea": 3.00, "earl grey tea": 3.00, "green tea": 3.00,
    # Bakery
    "butter croissant": 3.50, "chocolate croissant": 4.00,
    "blueberry muffin": 3.50, "chocolate muffin": 3.50,
    "cinnamon roll": 4.00, "banana bread": 3.00
}

SPECIALS_TEXT = """
TODAY'S SPECIALS:
1. Caramel Latte Special – 10% off on all sizes.
2. Cold Brew of the Day – Vanilla Cold Brew at 30% off.
"""


@tool
def get_menu_tool():
    """Returns the menu items, prices, and today's specials."""
    menu_str = "--- COFFEE & BEVERAGE MENU ---\n"
    for item, price in MENU.items():
        menu_str += f"- {item.title()}: ${price:.2f}\n"

    menu_str += "\n--- MILK OPTIONS ---\n"
    menu_str += "Regular, Skim, Soy, Almond, Oat Milk\n"

    menu_str += f"\n{SPECIALS_TEXT}"
    return menu_str


@tool
def register_customer_tool(name: str):
    """
    Registers the customer name at the start of the call.
    """
    # Create a session ID (simulated)
    cust_id = f"C-{random.randint(1000, 9999)}"
    return {
        "action": "register",
        "name": name,
        "customer_id": cust_id,
        "message": f"Customer {name} registered. ID: {cust_id}. Now ask if this is Dine-in or Takeaway."
    }


@tool
def add_to_cart_tool(item_name: str, quantity: int = 1, details: str = ""):
    """
    Adds an item.
    'details' string should contain size, milk, sugar, or temp preferences.
    Example: item_name='latte', details='medium, oat milk, no sugar, iced'
    """
    clean_name = item_name.lower().strip()
    price = 0
    found_item = None

    # Logic to match "Caramel Latte" even if user says "Latte with caramel"
    for menu_item in MENU:
        if menu_item in clean_name or clean_name in menu_item:
            found_item = menu_item
            price = MENU[menu_item]
            break

    if not found_item:
        return f"Error: '{item_name}' not found in menu."

    # Apply Specials Logic (Simple implementation)
    if "caramel latte" in found_item:
        price = price * 0.90  # 10% off
    elif "vanilla cold brew" in found_item:
        price = price * 0.70  # 30% off

    total = price * quantity

    return {
        "action": "add",
        "item": found_item,
        "details": details,
        "quantity": quantity,
        "cost": total,
        "message": f"Added {quantity} x {found_item.title()} ({details}) to cart. Total: ${total:.2f}"
    }


@tool
def reserve_table_tool(room_name: str, time: str, pax: int):
    """
    Reserves a space.
    room_name: 'Rose Lounge' or 'Meeting Room'
    """
    res_id = f"RES-{random.randint(100, 999)}"
    return f"Reservation Confirmed. Room: {room_name}, Time: {time}, Pax: {pax}. RESERVATION ID: {res_id}. (SMS sent)."


@tool
def checkout_tool(cart_items: list, customer_name: str):
    """
    Finalizes the order. Returns the receipt and UNIQUE ORDER ID.
    """
    if not cart_items:
        return "Error: Cart is empty."

    total = sum(item['cost'] for item in cart_items)
    order_id = f"ORD-{random.randint(10000, 99999)}"

    receipt = f"ORDER ID: {order_id}\n"
    receipt += f"Customer: {customer_name}\n"
    for item in cart_items:
        details = item.get('details', 'Standard')
        receipt += f"- {item['item'].title()} ({details}) x{item['quantity']} : ${item['cost']:.2f}\n"
    receipt += f"TOTAL: ${total:.2f}\n"
    receipt += f"(System Note: Tell the user this Order ID and that an SMS has been sent.)"

    return receipt