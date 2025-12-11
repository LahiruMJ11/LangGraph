from langgraph.graph import StateGraph, END, START
from langgraph.types import Command, interrupt
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

class State(TypedDict):
    value: str

def node_a(state: State):
    print("Node A")
    return Command(
        goto="node_b",
        update={
            "value": state["value"] + "a"
        }
    )

def node_b(state: State):
    print("Node B")

    human_response = interrupt("Do you want to goto C or D ?")
    print("Human Review Values: ", human_response)

    if human_response == "C":
        return Command(
            goto="node_c",
            update={
                "value": state["value"] + "b"
            }
        )

    elif human_response == "D":
        return Command(
            goto="node_d",
            update={
                "value": state["value"] + "b"
            }
        )
    return None


def node_c(state: State):
    print("Node C")
    return Command(
        goto=END,
        update={
            "value": state["value"] + "c"
        }
    )

def node_d(state: State):
    print("Node D")
    return Command(
        goto=END,
        update={
            "value": state["value"] + "d"
        }
    )

graph = StateGraph(State)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.add_node("node_d", node_d)
graph.set_entry_point("node_a")

app = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": 1}}

initial_state = {
    "value": ""
}

first_result = app.invoke(initial_state, config=config, stream_mode="updates")
print(first_result)