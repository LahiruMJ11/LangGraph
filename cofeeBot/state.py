# state.py
from typing import TypedDict, List, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage

class CoffeeState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    customer_name: Optional[str]
    customer_id: Optional[str]
    # Track order type (Takeaway/Dine-in) to help the agent flow
    order_type: Optional[str]
    cart: List[dict]
    total_price: float