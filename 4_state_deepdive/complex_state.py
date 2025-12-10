from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
import operator

class SimpleState(TypedDict):
    count: int
    sum: Annotated[int, operator.add]
    history: Annotated[List[int], operator.concat]

#manual method
# def increment(state: SimpleState) -> SimpleState:
#     new_count = state["count"] + 1
#     state["count"] = new_count
#     state["sum"] = new_count + state["sum"]
#     state["history"].append(new_count)
#     return state

def increment(state: SimpleState) -> SimpleState:
    new_count = state["count"] + 1

    return {
        "count": new_count,
        "sum": new_count,
        "history": [new_count]
    }

def should_continue(state):
    if state["count"] < 5:
        return "continue"
    else:
        return "stop"

graph = StateGraph(SimpleState)

graph.add_node("increment", increment)
graph.set_entry_point("increment")
graph.add_conditional_edges("increment", should_continue, {"continue": "increment", "stop": END})

app = graph.compile()

state = {
    "count": 0,
    "sum": 0,
    "history": []
}

response = app.invoke(state)
print(response)