from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pptx import Presentation
from typing import  List, Optional, Annotated
import base64
import os
from models import PosterBulletPoints
from research_parser import research_context_parser, research_figure_parser
from generate_poster import poster_formatter_agent, generate_poster
from conference_parser import conference_parser
import json

# initialize the web server
app = FastAPI()

templates = Jinja2Templates(directory="templates")
@app.get("/")
async def serve_home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Define data to receive from the frontend
# We have to use Form() since we are receiving multipart form data
# we can use pydantic object if the input is pure text
@app.post("/api/draft")
async def generate_draft(
    request: Request,
    raw_text: str = Form(...),
    user_focus: str = Form("poster"), 
    images: Annotated[list[UploadFile] | None, File()] = None,
):
    # process images if users attach them
    print("=== /api/draft called ===")
    print(f"DEBUG: images received: {images}")          # is it None or a list?
    print(f"DEBUG: number of images: {len(images) if images else 0}")
    extracted_images = {}
    vision_metadata = None
    if images:
        # temporarily create folder for on-the-fly image processing
        # will implement database later
        # get the absolute path of the directory where app.py exists
        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Users/kyileiaye/Desktop/Thutaytana
        UPLOAD_DIR = os.path.join(BASE_DIR, "uploads") # join it with the folder name ; Users/kyileiaye/Desktop/Thutaytana/uploads
        os.makedirs(UPLOAD_DIR, exist_ok = True) # create the directory

        for img in images:
            file_path = os.path.join(UPLOAD_DIR, img.filename)
            content = await img.read()
            with open(file_path, "wb") as f:
                f.write(content)
                
            # convert to base 64 for AI vision agent
            encoded_str = base64.b64encode(content).decode("utf-8")
            mimie_type = img.content_type or "image/png"
            formatted_uri = f"data:{mimie_type};base64,{encoded_str}"
            
            # map file path to the base64 string
            extracted_images[file_path] = formatted_uri
            
        # run Vision Agent
        vision_metadata = research_figure_parser(raw_text, extracted_images)
        
    # process text
    context_agent = research_context_parser()
    parsed_context = context_agent.invoke({
        "user_goal": user_focus,
        "raw_text": raw_text,
        "vision_metadata": vision_metadata
    })
    
    # creating poster
    poster_agent = poster_formatter_agent()
    bullet_points = poster_agent.invoke({
        'title': parsed_context.title,
        'introduction': parsed_context.introduction,
        'problem': parsed_context.problem_gap,
        'research_goals': parsed_context.research_goal,
        'methods': parsed_context.methodology,
        'results': parsed_context.key_res,
        'conclusion': parsed_context.conclusion
    })
    
    # return html template, passing AI generated bullet points into it
    return templates.TemplateResponse(
            request=request,
            name="draft_editor.html",
            context={
                "bullets": bullet_points.model_dump(), # converting bullet point object to dict
                "vision_metadata": [v.model_dump() for v in vision_metadata] if vision_metadata else None,
                "abstract": parsed_context.abstract
            }
    )
    
# for exporting to pptx poster slide
@app.post("/api/download-pptx")
async def download_pptx(
    title: str = Form(...),
    introduction: str = Form(...),
    problem: str = Form(...),
    research_goals: str = Form(...),
    methods: str = Form(...),
    results: str = Form(...),
    conclusion: str = Form(...),
    vision_data: str = Form(None) 
):
    print("DEBUG vision_data:", vision_data) 
    bullet_points = PosterBulletPoints(
        title = title,
        introduction_bullets= introduction.split("\n"),
        problem_gap_bullets=problem.split("\n"),
        research_goal_bullets=research_goals.split("\n"),
        method_bullets=methods.split("\n"),
        result_bullets=results.split("\n"),
        conclusion_bullets=conclusion.split("\n"),
    )
    
    parsed_vision = None
    if vision_data:

        vision_list = json.loads(vision_data)
        
        if vision_list is not None:
        
        # Helper class to allow dot-notation (e.g., img.image_filename)
        # The vision agent returns pydantic vision_metadata obj and access its data using dot notation
        # but json.load(vision_data) doesn't recreate pydantic obj but it creates dict. we have to call img['image_filename] 
        # but generate poster calls vision metadata with dot annotation. So, if we create a class, we can call the dot 
            class ImageMetaData:
                def __init__(self, d):
                    for k, v in d.items():
                        setattr(self, k , v)
                        
            parsed_vision = [ImageMetaData(img) for img in vision_list]
    
    # Default conference rules
    conference_guidelines = "Dimensions: 48 inches wide by 36 inches height."
    conference_rule_agent = conference_parser()
    conference_rules = conference_rule_agent.invoke(conference_guidelines)

    output_path = "./uploads/poster_output.pptx"
    generate_poster(bullet_points, vision_metadata=parsed_vision, conference_rules=conference_rules, output_name=output_path)

    return FileResponse(
        path=output_path,
        filename="poster.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

    