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
    
    prompt = ChatPromptTemplate([
        ("system", system_instructions),
        ("user", "User's focus: {user_goal}\n\nRaw Research Text:\n{raw_text}")
    ])
    
    # chain the llm prompt and its output structure together
    parser_chain = prompt | structured_llm
    
    return parser_chain

sample_raw_research_text = """
    A traditional biopsy method used for investigating cancer-suspicious skin tissue, while effective, is invasive and time-consuming. It includes multiple processing steps to produce Hematoxylin & Eosin (H&E) images, which are gold standard for cancer diagnosis. Recently, a virtual biopsy has emerged as a non-invasive alternative that produces two-dimensional grayscale Optical Coherence Tomography (OCT) images by simply scanning live tissue. However, interpreting OCT images requires extensive specialized training for pathologists, which makes the virtual biopsy limited in clinical settings. Moreover, the scarcity of annotated OCT datasets has hindered the development of useful foundation models to assist pathologists examining these OCT images. In this study, we developed a vision-language model capable of interpreting OCT images for tissue classifications without manual annotations. We fine-tuned the Multimodal transformer with Unified maSKed modeling (MUSK), a vision-language model originally pre-trained on H&E images, using a knowledge distillation approach. By training the model on approximately 500 H&E-OCT image pairs, we reduced the domain gap between H&E image embeddings (feature representations) from original MUSK vision encoder (teacher model) and OCT image embeddings from fine-tuned MUSK vision encoder (student model). We achieved around 72% accuracy increase in skin tissue classification in OCT images. This significant gain in accuracy highlights the model’s potential to support pathologists in interpreting OCT scans and enhance the clinical viability of non-invasive cancer diagnosis."""
user_focus = "poster"
agent = research_parser()
# run the agent 
print("running research parser...")
res = agent.invoke({
    "user_goal": user_focus,
    "raw_text": sample_raw_research_text
})

print("\n--- Parsed Output ---")
print(f"Title: {res.title}\n")
print(f"Problem Gap: {res.problem_gap}\n")
print(f"Methodologies: {res.methodology}\n")
print(f"Results: {res.key_res}\n")
print(f"Abstract: {res.abstract}\n")

    