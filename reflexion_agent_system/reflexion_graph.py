from typing import List
from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import MessageGraph, END
from chains import revisor_chain, first_responder_chain
from execute_tools import execute_tools

MAX_ITERATIONS = 2

graph = MessageGraph()

graph.add_node("responder", first_responder_chain)
graph.add_node("revisor", revisor_chain)
graph.add_node("execute_tools", execute_tools)

graph.add_edge("responder", "execute_tools")
graph.add_edge("execute_tools", "revisor")

def event_loop(state: List[BaseMessage]) -> str:
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state)
    if count_tool_visits > MAX_ITERATIONS:
        return END
    return "execute_tools"

graph.add_conditional_edges("revisor", event_loop)
graph.set_entry_point("responder")

app = graph.compile()
print(app.get_graph().draw_mermaid())

response = app.invoke("Write about best travel destinations 2025")
print(response[-1].tool_calls[0]["args"]["answer"])
print(response, "response")