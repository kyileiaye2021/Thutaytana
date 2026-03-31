# define exact instruction what we want to give AI

from pydantic import BaseModel, Field
from typing import Literal, List, Optional

# Parsing Research Context
class ResearchContext(BaseModel):
    """
    Defining the schema where research context parser will return

    Args:
        BaseModel (class): a parent class that provides the behavior
    """
    title: str = Field(description="Official title about the research that is reflecting the main goal of the research project")
    introduction: str = Field(description="A bit background about research context")
    problem_gap: str = Field(description="The specific academic or technical gap this research attempts to solve.")
    research_goal: str = Field(description="The goal of the research to solve the problem gap")
    methodology: str = Field(description="A concise summary of the methods, algorithms, or experiments used to solve the research topic or problem.")
    key_res: List[str] = Field(description="A list of critical findings, metrics, or outcomes for research problem.")
    conclusion: str = Field(description="The primary takeaway or future work suggested for the resaerch project.")
    abstract: str = Field(description="The research abstract. If the provided text lacks an abstract, generate a 200-word one summarizing the context.")
    special_focus: str = Field(description="The user's stated goal (poster or presentation slides).")

class FigureDetails(BaseModel):
    """
    Defining schema for the structure of how figure descriptions were be generated for an image

    Args:
        BaseModel (class): _a parent class that provides behavior
    """
    image_filename: str = Field(description="The filename provided")
    
    # For text parser 
    detailed_analysis: str = Field(description="Deep explanation of the figure, trends, extracted metrics, and context. Used for writing the abstract.")
    extracted_metrics: List[str] = Field(description="Specific numbers, percentages, or p-values.")
    
    # For the poster agent 
    suggested_section: Literal["Introduction", "Problem Gap", "Research Goal", "Method", "Result", "Conclusion", "Exclude"] = Field(
        description="Categorize where this image belongs on a scientific poster. Use 'Exclude' if it is just a decorative logo.")
    
    figure_caption: List[str] = Field(description="A very short, 1-sentence punchy caption to display directly under the image on the poster.")
    
class FigureMetadata(BaseModel):
    """
    Define the OUTER schema that holds the list of images
    Container for all analyzed figures from the document.
    """
    figures: List[FigureDetails] = Field(description="A list of all the figures analyzed and their metadata.")
    
# Parsing Conference Rules
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
    width_inches: float = Field(description="The mandatory width of the poster in inches. Return 48.0 if not specified.", default=48.0)
    height_inches: float = Field(description="The mandatory height of the poster in inches. Return 36.0 if not specified.", default=36.0)
    font_constraints: FontConstraints = Field(description="Font Rules.")
    required_sections: List[str] = Field(description="List of mandatory sections explicitly requested (e.g., ['Abstract', 'Ethics Statement', 'References']).")
    word_limits: WordLimits = Field(description="Word Limits")
    branding_rules: Optional[str] = Field(description="Any specific rules about logos, color palettes, or institutional branding.")
    

class PosterBulletPoints(BaseModel):
    title: str = Field(description="The original title")
    introduction_bullets: List[str] = Field(description="2-3 extremely concise, short bullet points for Introduction.")
    problem_gap_bullets: List[str] = Field(description="1-2 extremely concise, short bullet points for Problem Gap.")
    research_goal_bullets: List[str] = Field(description="2-3 extremely concise, short bullet points for Research Goals.")
    method_bullets: List[str] = Field(description="3-4 extremely concise, short bullet points for Methodologies.")
    result_bullets: List[str] = Field(description="3-4 extremely concise, short bullet points for Results.")
    conclusion_bullets: List[str] = Field(description="2-3 extremely concise, short bullet points for Conclusion.")