from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os

from app.graph.graph import build_graph
from app.model.state import InterviewState

app = FastAPI(title="Podcast Summarizer API", description="Summarizes interview podcasts with Q&A and topics", version="1.0.0")
graph = build_graph()

class YouTubeRequest(BaseModel):
    youtube_link: str
    podcast_type: str
    summary_language: str

@app.post("/summarize/youtube")
async def summarize_youtube(request: YouTubeRequest):
    try:
        state = InterviewState(
            source_type="youtube",
            source_link_or_path=request.youtube_link,
            podcast_type=request.podcast_type,
            summary_language=request.summary_language
        )
        final_state = graph.invoke(state)
        
        final_state = InterviewState(**final_state)

        return {
            "global_summary": final_state.final_summary,
            "rep": final_state.representative_sentences,
            "sum": final_state.global_summary,
            "qa": final_state.qa,
            "tra": final_state.transcript
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/summarize/audio")
async def summarize_audio(file: UploadFile):
    try:
        # Save uploaded file locally
        temp_file_path = f"temp_uploads/{file.filename}"
        os.makedirs("temp_uploads", exist_ok=True)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        state = InterviewState(
            source_type="audio",
            source_link_or_path=temp_file_path
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
            "tra": final_state.transcript
        })
    except Exception as e:
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
            source_type="live",
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
