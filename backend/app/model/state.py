from typing import List, Optional
from pydantic import BaseModel

class TopicSummary(BaseModel):
    topic_name: str
    summary: str

class QAItem(BaseModel):
    question: str
    answer: str

class InterviewState(BaseModel):
    # === Input ===
    transcript: Optional[str] = None
    source_type: Optional[str] = None        # 'youtube' or 'audio'
    source_link_or_path: Optional[str] = None

    # Audio-related
    audio_file_path: Optional[str] = None    # path to local downloaded audio

    # === Intermediate analysis ===
    representative_sentences: Optional[List[str]] = None  # for vector DB insertion
    topics: Optional[List[str]] = None
    topic_summaries: Optional[List[TopicSummary]] = None
    qa: Optional[str] = None

    # === Outputs ===
    global_summary: Optional[str] = None     # reduced summary
    final_summary: Optional[str] = None      # final type-based generated summary

    # === Vector DB ===
    vector_db_path: Optional[str] = None     # local path to stored vector DB

    # === Metadata ===
    podcast_type: Optional[str] = "interview"  # default type

    # === Errors ===
    error_message: Optional[str] = None

    video_id: Optional[str] = None

    summary_language: Optional[str] = None

    channel_and_title: Optional[List[str]] = None