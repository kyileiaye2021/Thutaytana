import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from models import ResearchContext, FigureMetadata

load_dotenv() # load open ai api from .env

def research_figure_parser(raw_text, image_blobs):
    """
    This agent will read text and looks at images to generate accurate metadata and descriptions for figures.
    """
    
    # defining vlm 
    vlm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature = 0
    )
    
    # binding with structured output
    structured_vlm = vlm.with_structured_output(FigureMetadata)
    
    # system prompt
    system_instructions = """
    You are a Scientific Vision Agent specializing in research document analysis.
    Your task is to analyze the provided research figures (charts, graphs, tables, diagrams, images) 
    alongside the paper's text and extract high-fidelity descriptions of what the figures show.
    
    Rules:
    - Use the provided text to figure out what the acronyms or labels in the images mean.
    - Extract quantitative data: axes, legends, p-values.
    - If a figure caption is given, use it to ground your interpretation. If not, try to understand the figure based on the research context and generate metadata.
    - Return a list of clear figure descriptions."""
    
    # constructing multimodal list 
    # info provided by users
    user_content = [
        {"type": "text", "text": f"Raw Research Context: {raw_text}\n\nAnalyze these images based on the text above:"}
    ]
    for img in image_blobs:
        user_content.append({"type": "image_url", "image_url":img})
        
    # multimodal prompting
    prompt = structured_vlm.invoke(
        [
            SystemMessage(content=system_instructions),
            HumanMessage(content=user_content)
        ]
    )
    
    return prompt.figure_descriptions # Returns a List of figure descriptions from the research context

def research_context_parser():
    """
    This agent will get research related context from the user and will structure and return it 
    """
    # wraps open ai api but gives agent capabilities
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0 # temperature 0 is crucial because we want factual extraction, not creative writing
    )
    
    # make llm to return the research context in the schema/structure we defined in the ResearchContext in models.py
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
    
    When writing the research abstract, you must mimic the writing style, sentence structure, and tone provided in the 
    <style_guide> for each specific section.
    
    <study_guide>
        <section name="Introduction">
            <description>1-2 sentences establishing the research area and the primary challenge.</description>
            <example>
                In the rapidly evolving landscape of clinical AI, deep learning models have demonstrated remarkable success in identifying patterns within high-resolution medical imaging. 
                However, the deployment of these systems in critical healthcare settings is frequently hindered by their 'black-box' nature, which lacks the transparency required for clinical validation and physician trust.
            </example>
        </section>
        
        <section name="Problem Gap">
            <description>1-2 sentences identifying the specific void in current literature or technology.</description>
            <example>
                Current diagnostic frameworks often prioritize predictive accuracy at the expense of interpretability, 
                failing to provide the causal reasoning behind a model's output. Consequently, there remains a critical 
                need for hybrid architectures that can integrate raw data processing with symbolic logic to mirror the 
                structured decision-making processes of medical experts.
            </example>
        </section>
        
        <section name="Methodology">
            <description>1-2 sentences describing the technical approach or system architecture.</description>
            <example>
                We propose a neuro-symbolic pipeline that utilizes a Convolutional Neural Network (CNN) for feature extraction, coupled with a Logic-Reasoning Layer that applies expert-defined rules to those features. 
                This architecture enables the system to generate not only a diagnostic prediction but also a human-readable trace of the logical steps taken to reach that conclusion.
            </example>
        </section>
        
        <section name="Results/Findings">
            <description>1-2 sentences highlighting concrete achievements and their broader impact.</description>
            <example>
                Experimental results indicate that the hybrid model maintains a 94% F1-score in lesion classification—comparable to state-of-the-art purely neural models 
                while increasing the 'Explanatory Satisfaction' score among participating clinicians by 42%. These findings suggest that neuro-symbolic integration provides 
                a viable path toward trustworthy, interpretable AI without sacrificing the performance necessary for clinical adoption.
            </example>
        </section>
    </study_guide>
    
    """
    
    # text prompting
    prompt = ChatPromptTemplate([
        ("system", system_instructions),
        ("user", "User's focus: {user_goal}\n\nRaw Research Text:\n{raw_text}\nFigure Descriptions: {vision_metadata}") # input param for the research context parser
    ])
    
    # chain the llm prompt and its output structure together
    parser_chain = prompt | structured_llm # structure the llm output into the predefined structure
    
    return parser_chain

sample_raw_research_text = """"""

user_focus = "poster"
with open("./non-invasive cancer.png", "rb") as image_file:
    encoded_str = base64.b64encode(image_file.read()).decode('utf-8')
    # add data URI prefix to tell api what kind of media files those chars represent;; otherwise the api will reject it or read it as gibberish
    formatted_image_uri = f"data:image/png;base64,{encoded_str}"
extracted_images = [formatted_image_uri]

if extracted_images:
    vision_metadata = research_figure_parser(sample_raw_research_text, extracted_images)
else:
    vision_metadata = "No figures present in this document"
print(vision_metadata)

# agent = research_context_parser()
# # run the agent 
# print("running research parser...")
# res = agent.invoke({
#     "user_goal": user_focus,
#     "raw_text": sample_raw_research_text
# })

# print("\n--- Parsed Output ---")
# print(f"Title: {res.title}\n")
# print(f"Problem Gap: {res.problem_gap}\n")
# print(f"Methodologies: {res.methodology}\n")
# print(f"Results: {res.key_res}\n")
# print(f"Abstract: {res.abstract}\n")

    