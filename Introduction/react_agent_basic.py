from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import initialize_agent, tool
from langchain_community.tools import TavilySearchResults
import datetime

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
search_tool = TavilySearchResults(search_depth="basic")

@tool
def get_time_now(format: str = "%Y-%m-%d %H:%M:%S"):
    """Returns current time in specified format"""
    current_time = datetime.datetime.now().strftime(format)
    return current_time

tools = [search_tool, get_time_now]

agent = initialize_agent(tools=tools,
                         llm=llm,
                         agent="zero-shot-react-description",
                         verbose=True,
                         handle_parsing_errors=True)
agent.invoke("When was spaceX's last launch and how many days ago it happened?")

# result = llm.invoke("Hi how are you?")
# print(result)
