# main.py
from graph import app
from langchain_core.messages import HumanMessage

print("☕ Alex (Department of Coffee) is Ready! (Type 'quit' to exit)")

# Initial State
state = {
    "messages": [],
    "cart": [],
    "customer_name": None,
    "customer_id": None,
    "total_price": 0.0
}

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    state["messages"].append(HumanMessage(content=user_input))

    # Run Graph
    result = app.invoke(state, config={"recursion_limit": 20})
    state = result

    # Print Agent Response
    agent_response = state['messages'][-1].content

    # Clean up internal tool tokens if they leak into chat
    if "TOOL_CALL" in agent_response:
        # If the model ends with a tool call, the tool node runs,
        # and the LOOP goes back to chatbot.
        # The chatbot usually generates a verbal response AFTER the tool.
        # But if it stops, we interpret the result.
        pass

    print(f"Alex: {agent_response}")