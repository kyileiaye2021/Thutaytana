import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import ResearchContext

load_dotenv() # load open ai api from .env

def research_parser():
    """
    This agent will get research related context from the user and will structure and return it 
    """
    # wraps open ai api but gives agent capabilities
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0 # temperature 0 is crucial because we want factual extraction, not creative writing
    )
    
    # make llm to return the research context in the schema/structure we defined in the researchcontext
    structured_llm = llm.with_structured_output(ResearchContext)
    
    # system prompt for llm (instruction for llm)
    system_instructions = """ 
    You are an expert academic parser and research assistant. 
    Your job is to analyze raw research text, notes, and user goals, and extract a structured summary.
    
    Rules:
    1. Be precise and academic in your tone.
    2. If a research abstract is missing from the raw text, you must create one based on the given research context 
       by including what the research is about, what problem gap the research is trying to solve, what methods are used,
       what outcomes/achievements are resulted in, what are the future directions.
    3. Extract concrete metrics for the results wherever possible.
    """
    
    prompt = ChatPromptTemplate([
        ("system", system_instructions),
        ("user", "User's focus: {user_goal}\n\nRaw Research Text:\n{raw_text}")
    ])
    
    # chain the llm prompt and its output structure together
    parser_chain = prompt | structured_llm
    
    return parser_chain

sample_raw_research_text = """
    We introduce a novel routing algorithm for web crawlers in the UCI ICS domain. 
    Current crawlers get stuck in spider traps. We utilized a checksum-based deduplication 
    method and priority queues based on page rank. Our method crawled 50,000 pages 20% faster 
    than the baseline and reduced duplicate processing by 15%. Future work will integrate machine learning for dynamic priority scoring.
    """
user_focus = "poster"
agent = research_parser()
# run the agent 
print("running research parser...")
res = agent.invoke({
    "user_goal": user_focus,
    "raw_text": sample_raw_research_text
})

print("\n--- Parsed Output ---")
print(f"Title: {res.title}")
print(f"Results: {res.key_res}")
print(f"Abstract: {res.abstract}")

    