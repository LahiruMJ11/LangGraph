import sqlite3
from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
#from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

sqlite_con = sqlite3.connect('checkpoint.sqlite', check_same_thread=False)
memory = SqliteSaver(sqlite_con)

llm = ChatGroq(model = "llama-3.1-8b-instant")

class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: BasicChatState):
    return {
        "messages": [llm.invoke(state["messages"])]
    }

graph = StateGraph(BasicChatState)

graph.add_node("chatbot", chatbot)
graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)

app = graph.compile(checkpointer = memory)

config = {"configurable": {
    "thread_id": 1
}}

response1 = app.invoke({
    "messages": HumanMessage(content = "Hi I'm Lahiru")
}, config = config)

response2 = app.invoke({
    "messages": HumanMessage(content = "What's my name?")
}, config = config)

#print(app.get_state(config = config))

# print(response1)
# print("\n")
# print(response2)

while True:
    user_input = input("User: ")
    if user_input == "exit":
        break
    else:
        response = app.invoke({
            "messages": HumanMessage(content=user_input)
        }, config = config)

        print("AI: " + response["messages"][-1].content)