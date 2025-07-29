from typing import List, Optional, Any
from pydantic import BaseModel

class TopicSummary(BaseModel):
    topic_name: str
    summary: str

class QAItem(BaseModel):
    question: str
    answer: str

from typing import  List, Dict, Any, Optional
from typing_extensions import TypedDict

class AudioSegment(TypedDict):
    start: float
    end: float
    text: str

class SentenceAnalysis(TypedDict):
    text: str
    start: float
    end: float
    emotion: Optional[str]
    emotion_score: Optional[float]
    intonation_type: Optional[str] # e.g., "statement", "question", "command"
    speaker: Optional[str]

class QAPair(TypedDict):
    question: str
    answer: str
    context_sentences: List[str]
    question_speaker: Optional[str]
    answer_speaker: Optional[str]

class ProcessedChunk(TypedDict):
    id: str # A unique ID for the chunk
    text: str
    embedding: List[float] # Store as List[float] for Pydantic serialization
    metadata: Dict[str, Any] # Flexible metadata, e.g., start, end, original_index


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
    podcast_type: Optional[str] = None # default type

    # === Errors ===
    error_message: Optional[str] = None

    video_id: Optional[str] = None

    summary_language: Optional[str] = None

    channel_and_title: Optional[List[str]] = None

    all_processed_chunks: Optional[List[dict[str, Any]]] = None

    representative_chunks_for_summary: Optional[List[dict[str, Any]]] = None

    formatted_transcript_segments: List[AudioSegment]= None
    sentiment_analysis_results: List[SentenceAnalysis]= None # NEW
    intonation_analysis_results: List[SentenceAnalysis]= None # NEW
    qa_pairs: List[QAPair]= None # NEW

    wav_file_path: Optional[str] = None

    csv_path: Optional[str] = None

    is_question: Optional[bool] = False

    id: Optional[str] = None

    question: Optional[str] = None

    file_key: Optional[str] = None

    answer: Optional[str] = None
    