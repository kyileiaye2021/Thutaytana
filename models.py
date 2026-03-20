# define exact instruction what we want to give AI

from pydantic import BaseModel, Field
from typing import List

class ResearchContext(BaseModel):
    """
    Defining the schema where research context parser will return

    Args:
        BaseModel (class): a parent class that provides the behavior
    """
    title: str = Field(description="Official title about the research that is reflecting the main goal of the research project")
    abstract: str = Field(description="The research abstract. If the provided text lacks an abstract, generate a 200-word one summarizing the context.")
    problem_gap: str = Field(description="The specific academic or technical gap this research attempts to solve.")
    methodology: str = Field(description="A concise summary of the methods, algorithms, or experiments used to solve the research topic or problem.")
    key_res: List[str] = Field(description="A list of critical findings, metrics, or outcomes for research problem.")
    conclusion: str = Field(description="The primary takeaway or future work suggested for the resaerch project.")
    special_focus: str = Field(description="The user's stated goal (poster or presentation slides).")

