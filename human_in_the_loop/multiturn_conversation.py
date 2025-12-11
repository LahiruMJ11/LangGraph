from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, add_messages, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import uuid

load_dotenv()

class State(TypedDict):
    linkedin_topic: str
    generated_post: Annotated[list[str], add_messages]
    human_feedback: Annotated[list[str], add_messages]

llm = ChatGroq(model = "llama-3.1-8b-instant")

def model(state: State):
    """Using LLM to generate a linkedin post with human feedback"""

    print("[model] Generating content")
    linkedin_topic = state["linkedin_topic"]
    feedback = state["human_feedback"] if "human_feedback" in state else ["No feedback yet"]

    #define the prompt
    prompt = f"""
            
            Linkedin Topic: {linkedin_topic}
            Human Feedback: {feedback[-1] if feedback else "No feedback yet"}
            
            Generate a Structured well written LinkedIn post based on the given topic
            
            Consider previous human feedback to refine the response."""

    response = llm.invoke([
        SystemMessage(content="You are an expert LinkedIn content writer."),
        HumanMessage(content=prompt)
    ])

    generated_linkedin_post = response.content

    print("[model] Generated LinkedIn post: {}".format(generated_linkedin_post))

    return {
        "generated_post": [AIMessage(content=generated_linkedin_post)],
        "human_feedback": feedback,
    }

def human_node(state: State):
    """Human Intervention node - loops back to model until input is done."""
    print("\n [human_node] waiting for human feedback...")

    #Interrup for user feedback
    user_feedback = interrupt({
        "generated_post": state["generated_post"],
        "message": "Provide  feedback or type 'done' to finish."
    })

    print(f"[human_node] Received Human Feedback: {user_feedback}")

    if user_feedback.lower() == "done":
        return Command(update={"human_feedback": state["human_feedback"] + ["Finalized"]}, goto="end_node")
    else:
        return Command(update={"human_feedback": state["human_feedback"] + [user_feedback]}, goto="model")

def end_node(state: State):
    """Final node"""
    print("\n [end_node] received final node")
    print("\n Final generated post: ", state["generated_post"][-1])
    print("\n Final human feedback: ", state["human_feedback"][-1])

    return {"generated_post": state["generated_post"], "human_feedback": state["human_feedback"]}

graph = StateGraph(State)

graph.add_node("model", model)
graph.add_node("end_node", end_node)
graph.add_node("human_node", human_node)
graph.set_entry_point("model")

graph.add_edge("model", "human_node")
graph.set_finish_point("end_node")

#enabling interrup mechanism
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

linkedin_topic = input("Enter LinkedIn post topic: ")
initial_state = {
    "linkedin_topic": linkedin_topic,
    "generated_post": [],
    "human_feedback": []
}

for chunk in app.stream(initial_state, config=thread_config):
    for node_id, value in chunk.items():
        #If we reach interrupt continuously ask for human feedback
        if (node_id=="__interrupt__"):
            while True:
                user_feedback = input("Enter user feedback or type 'done' to finish.: ")

                #execute graph with user feedback
                app.invoke(Command(resume=user_feedback), config=thread_config)

                if user_feedback.lower() == "done":
                    break


