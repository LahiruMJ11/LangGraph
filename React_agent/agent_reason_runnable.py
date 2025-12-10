from langchain_openai import ChatOpenAI
from langchain.agents import tool, create_react_agent
import datetime
from langchain_community.tools import TavilySearchResults
from langchain import hub
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model = "gpt-4o")

search_tool = TavilySearchResults(search_depth="basic")

@tool
def get_time_now(format: str = "%Y-%m-%d %H:%M:%S"):
    """Returns current time in specified format"""
    current_time = datetime.datetime.now().strftime(format)
    return current_time

tools = [search_tool, get_time_now]

react_prompt = hub.pull("hwchase17/react")

react_agent_runnable = create_react_agent(tools=tools, llm=llm, prompt=react_prompt)