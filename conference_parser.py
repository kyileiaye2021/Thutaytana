import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import ConferenceRules

load_dotenv() # load open ai api from .env

def conference_parser():
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0 
    )
    
    structured_llm = llm.with_structured_output(ConferenceRules)
    
    system_instructions = """
    You are a strict compliance officer for an academic/research conference.
    Your job is to read the official conference guidelines and extract the exact formatting rules.
    
    Rules:
    1. Extract the rules and constraints exactly as written.
    2. Do NOT hallucinate standards academic rules if they are not explicitly stated in the text.
    3. If a rule (like font size) is not mentioned, do not guess. Leave it out or map it to 'Not specified'.
    4. Pay special attention to mandatory sections, like 'Ethics Statement' or 'Conflict of Interest', as the research agent will need to generate these if missing.
    """
    
    prompt = ChatPromptTemplate([
        ("system", system_instructions),
        ("user", "Conference Guidelines Text:\n{raw_text}")
    ])
    
    return prompt | structured_llm

conference_guidelines = """

    FOR ALL POSTERS:
    Please review Stanford’s Make a Good Poster page.
    Dimensions of your poster: 42 inches (wide) by 36 inches (height).
    
    SUBMISSION FILE FORMAT: .PDF 
    If you are submitting your poster with your application for printing, save the final poster in .pdf format and submit the PDF version.
    """
conference_rule_agent = conference_parser()
conference_rules = conference_rule_agent.invoke(conference_guidelines)
print("---Parsed Conference Rules---")
print(f"Format Type: {conference_rules.format_type}")
print(f"Dimension of poster: {conference_rules.dimensions}")
print(f"Required Sections: {conference_rules.required_sections}")
print(f"Word Limit for abstract: {conference_rules.word_limits}")
    


    