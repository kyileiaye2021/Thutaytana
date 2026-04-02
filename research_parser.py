import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from models import ResearchContext, FigureMetadata

load_dotenv() # load open ai api from .env

def research_figure_parser(raw_text, image_blobs):
    """
    This agent will read text and looks at images to generate accurate metadata and descriptions for figures.
    """
    
    # defining vlm 
    vlm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0
        # max_retries=2 # good practice to handle momentary network blips
    )
    
    # binding with structured output
    structured_vlm = vlm.with_structured_output(FigureMetadata)
    
    # system prompt
    system_instructions = """
    You are a Scientific Vision Agent specializing in research document analysis.
    Your task is to analyze the provided research figures (charts, graphs, tables, diagrams, images) 
    alongside the paper's text and extract high-fidelity descriptions of what the figures show.
    
    Rules:
    - CRITICAL: For each figure, you MUST include the exact 'image_filename' provided in the prompt text.
    - Use the provided text to figure out what the acronyms or labels in the images mean.
    - Extract quantitative data (axes, legends, p-values) into `extracted_metrics`.
    - Write a deep `detailed_analysis` that will be used by another AI to write the abstract.
    - If a figure caption is given, use it to ground your interpretation. If not, try to understand the figure based on the research context and generate metadata.
    - Write a short, punchy `poster_caption` suitable for a PowerPoint slide.
    - Categorize the figure into the most logical `suggested_section` (Introduction, Problem Gap, Method, Results, Conclusion, or Exclude)."""
    
    # constructing multimodal list 
    # info provided by users
    user_content = [
        {"type": "text", "text": f"Raw Research Context: {raw_text}\n\nAnalyze these images based on the text above:"}
    ]
    for filename, img in image_blobs.items():
        user_content.append({"type": "text", "text": f"\n--- Start of Image: {filename} ---"})
        user_content.append({"type": "image_url", "image_url":{"url": img}}) # need to change img to dict if we use groq
        
    # multimodal prompting
    prompt = structured_vlm.invoke(
        [
            SystemMessage(content=system_instructions),
            HumanMessage(content=user_content)
        ]
    )
    
    return prompt.figures # Returns a List of figure descriptions from the research context

def research_context_parser():
    """
    This agent will get research related context from the user and will structure and return it 
    """
    # wraps open ai api but gives agent capabilities
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_retries=2 # good practice to handle momentary network blips   )
    )
    # make llm to return the research context in the schema/structure we defined in the ResearchContext in models.py
    structured_llm = llm.with_structured_output(ResearchContext)
    
    # system prompt for llm (instruction for llm)
    system_instructions = """ 
    You are an expert academic parser and research assistant. 
    Your job is to analyze raw research text, notes, and user goals, and extract a structured summary.
    
    Rules:
    1. Be precise, formal, and academic in your tone.
    2. If a research abstract is missing in the raw text, you must create one based on the given research context using:
       - research objective
       - problem gap
       - methodology
       - key results (with metrics)
       - conclusions and implications
    3. Extract concrete metrics for the results wherever possible.
    4. You MUST integrate quantitative insights from the provided 'Figure Descriptions' into your summary, especially in the Results section if vision_metada is not None.
    5. Ensure logical coherence across sections; each section should naturally build on the previous one.
    
    When writing the research abstract, you must mimic the writing style, sentence structure, and tone provided in the 
    <style_guide> for each specific section. You may combine the Results and Conclusion sections if appropriate, but preserve clarity of contributions and impact.
    
    <style_guide>
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
        
        <section name="Research Goal">
            <description>1 sentence explicitly stating the primary aim, objective, or hypothesis of the study to address the identified problem gap.</description>
            <example>
                To address this limitation, this study aims to develop and validate a novel neuro-symbolic framework designed to seamlessly integrate high-performance feature extraction with transparent, rule-based clinical reasoning.
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
           <description>1-2 sentences highlighting concrete findings with quantitative metrics.</description>
            <example>
                Experimental results indicate that the hybrid model maintains a 94% F1-score in lesion classification—comparable to state-of-the-art purely neural models 
                while increasing the 'Explanatory Satisfaction' score among participating clinicians by 42%. These findings suggest that neuro-symbolic integration provides 
                a viable path toward trustworthy, interpretable AI without sacrificing the performance necessary for clinical adoption.
            </example>
        </section>
        
        <section name="Conclusion">
        <description>1-2 sentences summarizing key contributions, connecting results to the research objective, and highlighting broader impact or future implications.</description>
        <example>
            These results demonstrate that integrating interpretable reasoning mechanisms with high-performance learning models can effectively bridge the gap between accuracy and transparency in clinical AI systems. 
            More broadly, this work establishes a scalable foundation for deploying trustworthy, human-aligned decision-support systems in high-stakes medical environments.
        </example>
    </section>       
    </style_guide>
    
    """
    
    # text prompting
    prompt = ChatPromptTemplate([
        ("system", system_instructions),
        ("user", "User's focus: {user_goal}\n\nRaw Research Text:\n{raw_text}\nFigure Descriptions: {vision_metadata}") # input param for the research context parser
    ])
    
    # chain the llm prompt and its output structure together
    parser_chain = prompt | structured_llm # structure the llm output into the predefined structure
    
    return parser_chain

sample_raw_research_text = """
Date: October 14
Phase: Initial Setup & Baseline Testing

Summary of Progress:
During this phase, we established the baseline Retrieval-Augmented Generation (RAG) pipeline to assist students with queries related to data structures and algorithms. The system ingests university lecture slides, textbook chapters, and documentation. We utilized a standard vector database for semantic search and a pre-trained Large Language Model (LLM) to generate answers based on the retrieved context.
Initial Findings:
We evaluated the baseline system on a test set of 500 algorithmic questions.

Overall Accuracy: 68.5%

Observation: The model performs well on direct factual recall (e.g., "What is the time complexity of QuickSort?"). However, it struggles significantly with multi-hop reasoning and constraint-based queries (e.g., "Which sorting algorithm is best for a nearly sorted array with strict memory constraints?"). Hallucinations occur in 18% of complex logic responses.

Date: November 4
Phase: Architecture Revision & Neuro-Symbolic Integration

Summary of Progress:
To address the LLM's failure in complex reasoning, we redesigned the pipeline into a neuro-symbolic architecture. Instead of relying solely on the LLM to generate the final answer from text, the LLM now acts as a semantic parser. It extracts the rules and constraints from the retrieved RAG context and formats them into logical predicates. A deterministic symbolic solver then evaluates these rules to guarantee a logically sound answer.

Overall Accuracy: Improved to 84.2%.

Observation: Hallucinations on complex algorithmic questions dropped to 3%. The symbolic solver successfully enforces strict logical consistency.

Issue: The system latency increased significantly. Processing queries through the symbolic solver adds an average of 850ms per query, making the system sluggish for simple questions that do not require deep reasoning.

Date: November 25
Phase: Optimization & Final Benchmarking

Summary of Progress:
To solve the latency bottleneck identified in the previous phase, we implemented a lightweight query classification routing mechanism. The system now uses a small, fine-tuned classifier to determine if a student's query is "factual" or "logical/algorithmic." Factual queries bypass the symbolic engine and use the standard baseline RAG, while complex queries are routed to the neuro-symbolic pipeline.

Final Accuracy: 88.7% across the entire 500-question test set.

Latency: Average response time reduced to 320ms, which is well within the acceptable threshold for real-time educational tools.

Conclusion: The hybrid routing approach successfully maintains the high accuracy and logical consistency of neuro-symbolic AI while preserving the speed and efficiency of traditional RAG systems.

"""

# A traditional biopsy method used for investigating cancer-suspicious skin tissue, while effective, is invasive and time-consuming. It includes multiple processing steps to produce Hematoxylin & Eosin (H&E) images, which are gold standard for cancer diagnosis. Recently, a virtual biopsy has emerged as a non-invasive alternative that produces two-dimensional grayscale Optical Coherence Tomography (OCT) images by simply scanning live tissue. However, interpreting OCT images requires extensive specialized training for pathologists, which makes the virtual biopsy limited in clinical settings. Moreover, the scarcity of annotated OCT datasets has hindered the development of useful foundation models to assist pathologists examining these OCT images. In this study, we developed a vision-language model capable of interpreting OCT images for tissue classifications without manual annotations. We fine-tuned the Multimodal transformer with Unified maSKed modeling (MUSK), a vision-language model originally pre-trained on H&E images, using a knowledge distillation approach. By training the model on approximately 500 H&E-OCT image pairs, we reduced the domain gap between H&E image embeddings (feature representations) from original MUSK vision encoder (teacher model) and OCT image embeddings from fine-tuned MUSK vision encoder (student model). We achieved around 72% accuracy increase in skin tissue classification in OCT images. This significant gain in accuracy highlights the model’s potential to support pathologists in interpreting OCT scans and enhance the clinical viability of non-invasive cancer diagnosis.


# user_focus = "poster"
# with open("./RAG.png", "rb") as image_file:
#     encoded_str = base64.b64encode(image_file.read()).decode('utf-8')
#     # add data URI prefix to tell api what kind of media files those chars represent;; otherwise the api will reject it or read it as gibberish
#     formatted_image_uri = f"data:image/png;base64,{encoded_str}"
    
# with open("./RAG_2.png", "rb") as image_file:
#     encoded_str2 = base64.b64encode(image_file.read()).decode('utf-8')
#     # add data URI prefix to tell api what kind of media files those chars represent;; otherwise the api will reject it or read it as gibberish
#     formatted_image_uri2 = f"data:image/png;base64,{encoded_str2}"
    
# with open("./RAG_3.png", "rb") as image_file:
#     encoded_str3 = base64.b64encode(image_file.read()).decode('utf-8')
#     # add data URI prefix to tell api what kind of media files those chars represent;; otherwise the api will reject it or read it as gibberish
#     formatted_image_uri3 = f"data:image/png;base64,{encoded_str3}"
    
# extracted_images = {
#     'RAG': formatted_image_uri, 
#     'RAG_2': formatted_image_uri2,
#     'RAG_3': formatted_image_uri3
#     }
# # extracted_images = None
# if extracted_images:
#     vision_metadata = research_figure_parser(sample_raw_research_text, extracted_images)
# else:
#     vision_metadata = None
# # print(vision_metadata)

# for img in vision_metadata:
#     print(f"File: {img.image_filename}")
#     print(f"Section: {img.suggested_section}")
#     print(f"Caption: {img.figure_caption}")
#     print(f"Deep Analysis: {img.detailed_analysis}")
#     print()

# agent = research_context_parser()
# # run the agent 
# print("running research parser...")
# res = agent.invoke({
#     "user_goal": user_focus,
#     "raw_text": sample_raw_research_text,
#     "vision_metadata": vision_metadata
# })

# print("\n--- Parsed Output ---")
# print(f"Title: {res.title}\n")
# print(f"Introduction: {res.introduction}")
# print(f"Problem Gap: {res.problem_gap}\n")
# print(f"Research Goal: {res.research_goal}\n")
# print(f"Methodologies: {res.methodology}\n")
# print(f"Results: {res.key_res}\n")
# print(f"Conclusion: {res.conclusion}\n")
# print(f"Abstract: {res.abstract}\n")

    