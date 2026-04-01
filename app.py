from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from typing import  List, Optional, Annotated
import base64
import os
from models import PosterBulletPoints
from research_parser import research_context_parser, research_figure_parser
from generate_poster import poster_formatter_agent, generate_poster

# initialize the web server
app = FastAPI()

# temporarily create folder for on-the-fly image processing
# will implement database later
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok = True)

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
    extracted_images = {}
    vision_metadata = None
    if images:
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
                "vision_metadata": [v.model_dump() for v in vision_metadata] if vision_metadata else None
            }
    )
    
    