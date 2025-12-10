from pydantic import BaseModel, Field
from typing import List

class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing")
    superflous: str = Field(description="Critique of what is superflous")

class AnswerQuestion(BaseModel):
    """Answer the user's question"""

    answer: str = Field(description="~250 word detailed answer to the question")
    search_queries: List[str] = Field(description="1-3 search queries for researching improvements to address the critique "
                                                  "of your current answer.")
    reflection: Reflection = Field(description="Your reflection on the initial answer.")

class ReviseAnswer(AnswerQuestion):
    """Revise your original answer based on critique and search results"""

    references: List[str] = Field(
        description="Citations motivating your updated answer.",
    )


