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
    - CRITICAL: For each figure, you MUST include the exact 'image_filename' provided in the prompt text.
    - Use the provided text to figure out what the acronyms or labels in the images mean.
    - Extract quantitative data (axes, legends, p-values) into `extracted_metrics`.
    - Write a deep `detailed_analysis` that will be used by another AI to write the abstract.
    - If a figure caption is given, use it to ground your interpretation. If not, try to understand the figure based on the research context and generate metadata.
    - Write a short, punchy `poster_caption` suitable for a PowerPoint slide.
    - Categorize the figure into the most logical `suggested_section` (Introduction, Problem Gap, Methodology, Results/Findings, Conclusion, or Exclude)."""
    
    # constructing multimodal list 
    # info provided by users
    user_content = [
        {"type": "text", "text": f"Raw Research Context: {raw_text}\n\nAnalyze these images based on the text above:"}
    ]
    for filename, img in image_blobs.items():
        user_content.append({"type": "text", "text": f"\n--- Start of Image: {filename} ---"})
        user_content.append({"type": "image_url", "image_url":img})
        
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
    1. Be precise, formal, and academic in your tone.
    2. If a research abstract is missing in the raw text, you must create one based on the given research context using:
       - research objective
       - problem gap
       - methodology
       - key results (with metrics)
       - conclusions and implications
    3. Extract concrete metrics for the results wherever possible.
    4. You MUST integrate quantitative insights from the provided 'Figure Descriptions' into your summary, especially in the Results section.
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
A traditional biopsy method used for investigating cancer-suspicious skin tissue, while effective, is invasive and time-consuming. It includes multiple processing steps to produce Hematoxylin & Eosin (H&E) images, which are gold standard for cancer diagnosis. Recently, a virtual biopsy has emerged as a non-invasive alternative that produces two-dimensional grayscale Optical Coherence Tomography (OCT) images by simply scanning live tissue. However, interpreting OCT images requires extensive specialized training for pathologists, which makes the virtual biopsy limited in clinical settings. We developed a vision-language model capable of interpreting OCT images for tissue classifications without manual annotations by  fine-tuning the Multimodal transformer with Unified maSKed modeling (MUSK), a vision-language model originally pre-trained on H&E images, using a knowledge distillation approach. By training the model on approximately 500 H&E-OCT image pairs, we reduced the domain gap between H&E image embeddings (feature representations) from original MUSK vision encoder (teacher model) and OCT image embeddings from fine-tuned MUSK vision encoder (student model). We achieved 72% accuracy improvement in OCT in skin tissue classification.
"""
# A traditional biopsy method used for investigating cancer-suspicious skin tissue, while effective, is invasive and time-consuming. It includes multiple processing steps to produce Hematoxylin & Eosin (H&E) images, which are gold standard for cancer diagnosis. Recently, a virtual biopsy has emerged as a non-invasive alternative that produces two-dimensional grayscale Optical Coherence Tomography (OCT) images by simply scanning live tissue. However, interpreting OCT images requires extensive specialized training for pathologists, which makes the virtual biopsy limited in clinical settings. Moreover, the scarcity of annotated OCT datasets has hindered the development of useful foundation models to assist pathologists examining these OCT images. In this study, we developed a vision-language model capable of interpreting OCT images for tissue classifications without manual annotations. We fine-tuned the Multimodal transformer with Unified maSKed modeling (MUSK), a vision-language model originally pre-trained on H&E images, using a knowledge distillation approach. By training the model on approximately 500 H&E-OCT image pairs, we reduced the domain gap between H&E image embeddings (feature representations) from original MUSK vision encoder (teacher model) and OCT image embeddings from fine-tuned MUSK vision encoder (student model). We achieved around 72% accuracy increase in skin tissue classification in OCT images. This significant gain in accuracy highlights the model’s potential to support pathologists in interpreting OCT scans and enhance the clinical viability of non-invasive cancer diagnosis.


user_focus = "poster"
with open("./non-invasive cancer.png", "rb") as image_file:
    encoded_str = base64.b64encode(image_file.read()).decode('utf-8')
    # add data URI prefix to tell api what kind of media files those chars represent;; otherwise the api will reject it or read it as gibberish
    formatted_image_uri = f"data:image/png;base64,{encoded_str}"
    
with open("./musk.png", "rb") as image_file:
    encoded_str2 = base64.b64encode(image_file.read()).decode('utf-8')
    # add data URI prefix to tell api what kind of media files those chars represent;; otherwise the api will reject it or read it as gibberish
    formatted_image_uri2 = f"data:image/png;base64,{encoded_str2}"
    
extracted_images = {
    'non-invasive cancer.png': formatted_image_uri, 
    'musk-model.png': formatted_image_uri2
    }

if extracted_images:
    vision_metadata = research_figure_parser(sample_raw_research_text, extracted_images)
else:
    vision_metadata = "No figures present in this document"
# print(vision_metadata)

for img in vision_metadata:
    print(f"File: {img.image_filename}")
    print(f"Section: {img.suggested_section}")
    print(f"Caption: {img.figure_caption}")
    print(f"Deep Analysis: {img.detailed_analysis}")
    print()

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
# print(f"Methodologies: {res.methodology}\n")
# print(f"Results: {res.key_res}\n")
# print(f"Conclusion: {res.conclusion}\n")
# print(f"Abstract: {res.abstract}\n")

    