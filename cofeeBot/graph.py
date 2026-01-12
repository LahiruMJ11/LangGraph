# graph.py
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from state import CoffeeState
from tools import get_menu_tool, add_to_cart_tool, register_customer_tool, checkout_tool, reserve_table_tool
from model_loader import load_local_model

# --- CONFIG ---
MODEL_PATH = "./coffee2.gguf"
llm = load_local_model(MODEL_PATH)


def chatbot_node(state: CoffeeState):
    messages = state['messages']
    current_cart = state.get('cart', [])
    cust_id = state.get('customer_id', None)
    cust_name = state.get('customer_name', "Guest")

    # --- DYNAMIC GUIDANCE FOR 1B MODEL ---
    # This helps the small model stay on track based on state
    guidance = ""
    if not cust_id:
        guidance = "CURRENT STEP: Ask for the customer's NAME immediately to register them."
    elif len(current_cart) == 0:
        guidance = "CURRENT STEP: Ask if this is Dine-in or Takeaway. Then take the order."
    else:
        guidance = "CURRENT STEP: Confirm the order, ask for Bakery items, or Checkout."

    # --- SYSTEM PROMPT (Injected with your exact text) ---
    system_prompt_text = f"""
    You are Alex, a Support Agent at 'Department of Coffee, Colombo'.

    *** STATE STATUS ***
    Customer Name: {cust_name}
    Customer ID: {cust_id if cust_id else "NOT REGISTERED"}
    Cart Items: {len(current_cart)}
    {guidance}

    *** SYSTEM INSTRUCTIONS ***
    1. GREETING: "Hello, thank you for calling Department of Coffee... My name is Alex..."
    2. PROTOCOL:
       - FIRST: Get User Name -> Use Tool 'REGISTER'.
       - SECOND: Ask "Dine-in or Takeaway?"
         - IF Dine-in: Ask "What time?" and "How many people?"
         - IF Takeaway: Ask "Are you on the way?"
       - THIRD: Take Order. Ask Size, Milk, Sugar, Hot/Iced for coffees.

    3. TOOLS:
       - Use 'REGISTER' tool for name.
       - Use 'MENU' tool to see prices/specials.
       - Use 'ADD' tool for items (include size/milk details).
       - Use 'RESERVE' if they want 'Rose Lounge' or 'Meeting Room'.
       - Use 'CHECKOUT' to finalize.

    4. MENU & UPSELLING:
       - Only list 3 items if asked.
       - Upsell Bakery items: Chocolate Croissant, Blueberry Muffin.
       - Specials: Caramel Latte (10% off), Vanilla Cold Brew (30% off).

    5. CLOSING:
       - Summarize order.
       - Ask for Rating (1-10).
       - Provide the unique ORDER ID or RESERVATION ID given by the tool.
       - Say "SMS sent".
       - End call within ~90 seconds.

    *** BEHAVIOR ***
    - Polite, warm, professional.
    - Do not talk too much. Keep it brief.
    - If user asks menu, summarize briefly.
    """

    conversation = [SystemMessage(content=system_prompt_text)] + messages
    response = llm.invoke(conversation)
    return {"messages": [response]}


def tool_execution_node(state: CoffeeState):
    """Executes tools and updates state variables."""
    last_message = state['messages'][-1].content
    cart = state.get('cart', [])
    cust_id = state.get('customer_id', None)
    cust_name = state.get('customer_name', None)

    response_msg = "Tool executed."

    # --- PARSE TOOLS ---
    # Note: 1B models sometimes format calls differently.
    # We look for keywords "TOOL_CALL: X" (Ensure your model outputs this format)

    if "TOOL_CALL: REGISTER" in last_message:
        try:
            # Expected: TOOL_CALL: REGISTER [Name]
            name = last_message.split("REGISTER")[1].strip()
            result = register_customer_tool.invoke(name)
            cust_id = result['customer_id']
            cust_name = result['name']
            response_msg = result['message']
        except:
            response_msg = "Error registering. Ask name again."

    elif "TOOL_CALL: MENU" in last_message:
        response_msg = get_menu_tool.invoke({})

    elif "TOOL_CALL: ADD" in last_message:
        try:
            # Expected: TOOL_CALL: ADD [Item Name] [qty] [details]
            # This parsing is tricky for 1B. We will try a simpler split.
            # Let's assume the model outputs: TOOL_CALL: ADD latte 1 (iced, oat milk)
            txt = last_message.split("ADD")[1].strip()
            # A robust parser would go here. For demo:
            result = add_to_cart_tool.invoke({"item_name": txt, "quantity": 1, "details": "Standard"})
            if isinstance(result, dict) and "action" in result:
                cart.append(result)
                response_msg = result['message']
            else:
                response_msg = str(result)
        except:
            response_msg = "Error adding item. Please clarify item name."

    elif "TOOL_CALL: RESERVE" in last_message:
        # Expected: TOOL_CALL: RESERVE Rose Lounge 10am 4
        response_msg = reserve_table_tool.invoke({"room_name": "Rose Lounge", "time": "TBD", "pax": 2})

    elif "TOOL_CALL: CHECKOUT" in last_message:
        response_msg = checkout_tool.invoke({"cart_items": cart, "customer_name": cust_name})

    return {
        "messages": [HumanMessage(content=f"SYSTEM: {response_msg}")],
        "cart": cart,
        "customer_id": cust_id,
        "customer_name": cust_name
    }


# --- ROUTER & GRAPH (Standard) ---
def router(state: CoffeeState):
    last_message = state['messages'][-1].content
    if "TOOL_CALL:" in last_message:
        return "tools"
    return "end"


workflow = StateGraph(CoffeeState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools", tool_execution_node)
workflow.set_entry_point("chatbot")
workflow.add_conditional_edges("chatbot", router, {"tools": "tools", "end": END})
workflow.add_edge("tools", "chatbot")
app = workflow.compile()