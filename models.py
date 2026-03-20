# define exact instruction what we want to give AI

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

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

class FontConstraints(BaseModel):
    # to fix the error of the structured output of open ai
    body_min_size: str = Field(description="Minimum body font size. Return 'None' if missing.", default="None")
    title_size: str = Field(description="Title font size. Return 'None' if missing.", default="None")
    family: str = Field(description="Font family like Arial. Return 'None' if missing.", default="None")
    
class WordLimits(BaseModel):
    total: int = Field(description="Max total words for abstract. Return 200 if missing.", default = 200)
    
class ConferenceRules(BaseModel):
    """
    Defining rules that the conference rule parser should return

    Args:
        BaseModel (class): a parent class that provides the behavior
    """
    format_type:str = Field(description="Identify if the guidelines are for a 'poster', 'presentation slides', 'research abstract' or all of them.")
    dimensions: str = Field(description="Physical dimensions or aspect ratio (e.g., '36x48 inches', 'A0 size', '16:9 aspect ratio') of the poster. Return 'Not specified' if missing.")
    font_constraints: FontConstraints = Field(description="Font Rules.")
    required_sections: List[str] = Field(description="List of mandatory sections explicitly requested (e.g., ['Abstract', 'Ethics Statement', 'References']).")
    word_limits: WordLimits = Field(description="Word Limits")
    branding_rules: Optional[str] = Field(description="Any specific rules about logos, color palettes, or institutional branding.")
    
