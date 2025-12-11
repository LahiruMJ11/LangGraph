from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, add_messages, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatGroq(model = "llama-3.1-8b-instant")

GENERATE_POST = "generate_post"
GET_REVIEW_DECISION = "get_review_decision"
POST = "post"
COLLECT_FEEDBACK = "collect_feedback"

def generate_post(state: State):
    return {
        "messages": [llm.invoke(state["messages"])]
    }

def get_review_decision(state: State):
    post_content = state["messages"][-1].content

    print("\n Current LinkedIn Post \n")
    print(post_content)
    print("\n")

    user_input = input("Post to LinkedIn? (yes/no): ")
    if user_input == "yes":
        return POST
    else:
        return COLLECT_FEEDBACK

def post(state: State):
    final_post = state["messages"][-1].content
    print("\n Final LinkedIn Post \n")
    print(final_post + "\n")

def collect_feedback(state: State):
    user_feedback = input("Enter your feedback: ")

    return {
        "messages": [HumanMessage(content=user_feedback)]
    }

graph = StateGraph(State)

graph.add_node(GENERATE_POST, generate_post)
graph.add_node(POST, post)
graph.add_node(COLLECT_FEEDBACK, collect_feedback)
graph.set_entry_point(GENERATE_POST)
graph.add_edge(COLLECT_FEEDBACK, GENERATE_POST)
graph.add_conditional_edges(GENERATE_POST, get_review_decision)
graph.add_edge(POST, END)

app = graph.compile()

response = app.invoke({
    "messages": [HumanMessage(content="Generate me a LinkedIn post on best travel destinations 2025")]
})

print(response)