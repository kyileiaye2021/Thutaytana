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


    