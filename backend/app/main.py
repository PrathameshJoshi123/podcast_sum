from fastapi import FastAPI, UploadFile, Form, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware 

from app.graph.graph import build_graph
from app.model.state import InterviewState

app = FastAPI(title="Podcast Summarizer API", description="Summarizes interview podcasts with Q&A and topics", version="1.0.0")
graph = build_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ans = {}

# def tp(state):
#     try:
#         final_state = graph.invoke(state)
#         final_state = InterviewState(**final_state)
        
#         ans["global_summary"] = final_state.final_summary
#         ans["qa"] = final_state.qa
#     except Exception as e:
#         ans["error"] = str(e)


# @app.get("/get_ans")
# def get_ans():
#     if not ans:
#         return JSONResponse(content={
#             "msg": "wait",
#             "response": ""
#         })
    
#     if "error" in ans:
#         return JSONResponse(content={
#             "msg": "error",
#             "response": ans["error"]
#         })

#     return JSONResponse(content={
#         "msg": "Success",
#         "response": ans
#     })

class YouTubeRequest(BaseModel):
    youtube_link: str
    podcast_type: str
    summary_language: str

@app.post("/summarize/youtube")
async def summarize_youtube(request: YouTubeRequest, backgroundtask: BackgroundTasks):
    try:
        state = InterviewState(
            source_type="youtube",
            source_link_or_path=request.youtube_link,
            podcast_type=request.podcast_type,
            summary_language=request.summary_language
        )
        
        final_state = graph.invoke(state)
        final_state = InterviewState(**final_state)
        
        return JSONResponse(content={
            "global_summary": final_state.final_summary,
            "rep": final_state.representative_sentences,
            "sum": final_state.global_summary,
            "qa": final_state.qa,
            "tra": final_state.transcript,
            "id" : final_state.file_key
        })
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/summarize/audio")
async def summarize_audio(
    file: UploadFile = File(...),
    podcast_type: str = Form(...),
    summary_language: str = Form(...)
):
    try:
        # Save uploaded file locally
        temp_file_path = f"temp_uploads/{file.filename}"
        os.makedirs("temp_uploads", exist_ok=True)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create InterviewState with additional form data
        state = InterviewState(
            source_type="audio",
            source_link_or_path=temp_file_path,
            podcast_type=podcast_type,              # <-- use as needed
            summary_language=summary_language       # <-- use as needed
        )

        final_state = graph.invoke(state)
        final_state = InterviewState(**final_state)

        # Remove temp file after processing
        os.remove(temp_file_path)

        return JSONResponse(content={
            "global_summary": final_state.final_summary,
            "rep": final_state.representative_sentences,
            "sum": final_state.global_summary,
            "qa": final_state.qa,
            "tra": final_state.transcript,
            "id": final_state.file_key
        })
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
from fastapi import UploadFile

@app.post("/transcribe/live")
async def transcribe_live(file: UploadFile, request):
    try:
        temp_file_path = f"temp_uploads/{file.filename}"
        os.makedirs("temp_uploads", exist_ok=True)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        state = InterviewState(
            source_type="audio",
            podcast_type=request.podcast_type,
            summary_language=request.summary_language
        )
        final_state = graph.invoke(state)
        
        final_state = InterviewState(**final_state)

        os.remove(temp_file_path)

        return JSONResponse(content={
            "transcript": final_state.transcript
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
async def root():
    return {"message": "Podcast Summarizer API is running!"}


@app.post("/question")
async def question(
    id: str = Form(...),
    question: str = Form(...),
):
    try:
        state = InterviewState(
        id=id,
        question=question,
        is_question=True
        )

        final_state = graph.invoke(state)

        final_state = InterviewState(**final_state)

        return JSONResponse(content={
            "answer": final_state.answer
        }, status_code=200)

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
