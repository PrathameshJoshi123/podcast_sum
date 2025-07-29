# # app/nodes/transcription_node.py (Your existing file)

# from typing import List
# import whisper_s2t
# import json
# import os
# from app.model.state import InterviewState, AudioSegment # Import AudioSegment
# import logging

# logger = logging.getLogger(__name__)

# # os.environ["PATH"] = r"D:\My_Space\Podcast_Summarizer\cudnn\bin;" + os.environ["PATH"]
# # os.add_dll_directory(r"D:\My_Space\Podcast_Summarizer\cudnn\bin")
# # It's generally better to set these system-wide or manage via env variables before script execution
# # rather than in Python code unless absolutely necessary and carefully managed.

# def transcribe_audio(file_path: str) -> tuple[str, List[AudioSegment]]: # Modified return type
#     logger.info(f"Transcribing audio file: {file_path}")
#     # Load the model once globally
#     # Consider making this a global or part of a shared context if LangGraph
#     # allows, to avoid reloading for every node call if not intended.
#     # For now, keeping it inside for self-containment.
#     model = whisper_s2t.load_model(
#         model_identifier="small",
#         backend="CTranslate2",
#         compute_type="int8",
#         device="cuda"  # Change to "cpu" if no GPU
#     )
#     # Prepare file list and parameters
#     files = [f"{file_path}"]
#     tasks = ["transcribe"]
#     initial_prompts = [None]

#     # Transcribe with VAD (voice activity detection)
#     out = model.transcribe_with_vad(
#         files,
#         tasks=tasks,
#         initial_prompts=initial_prompts,
#         batch_size=16
#     )

#     # Get first file's utterances
#     utterances = out[0]

#     # Format segments and combine text
#     formatted_segments: List[AudioSegment] = [] # Use the TypedDict
#     full_text = ""

#     for segment in utterances:
#         formatted_segments.append({
#             "start": segment["start_time"],
#             "end": segment["end_time"],
#             "text": segment["text"].strip(), # Strip text here
#             "speaker": None # Placeholder for speaker diarization
#         })
#         full_text += segment["text"].strip() + " "

#     # Save to JSON (optional for debugging)
#     os.makedirs("transcripts_json", exist_ok=True)
#     json_path = os.path.join("transcripts_json", "transcription_output.json")
#     with open(json_path, "w", encoding="utf-8") as f:
#         json.dump(formatted_segments, f, ensure_ascii=False, indent=2)

#     logger.info("Audio transcription complete.")
#     return full_text.strip(), formatted_segments # Return both

# # LangGraph node function
# def audio_transcribe_node(state: InterviewState) -> InterviewState:
#     logger.info("Executing audio_transcribe_node...")
#     audio_source_path = None

#     if state.source_type == "youtube":
#         audio_source_path = state.audio_file_path # Assuming this is the downloaded path
#     elif state.source_type == "audio":
#         audio_source_path = state.source_link_or_path # Assuming this is the local audio path

#     if not audio_source_path or not os.path.exists(audio_source_path):
#         state.error_message = "Audio file path not found or invalid."
#         logger.error(state.error_message)
#         return state

#     try:
#         full_text, formatted_segments = transcribe_audio(audio_source_path)
#         state.transcript = full_text
#         state.formatted_transcript_segments = formatted_segments
#         logger.info(f"Transcript generated. Total segments: {len(formatted_segments)}")
#     except Exception as e:
#         state.error_message = f"Audio transcription failed: {str(e)}"
#         logger.error(state.error_message, exc_info=True)

#     return state


import json
import os
import ffmpeg
import whisper_s2t  # <-- new import
from app.model.state import InterviewState
import uuid


# CUDA setup for Windows
os.environ["PATH"] = r"D:\My_Space\Podcast_Summarizer\cudnn\bin;" + os.environ["PATH"]
os.add_dll_directory(r"D:\My_Space\Podcast_Summarizer\cudnn\bin")


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video format to .wav using ffmpeg."""
    output_path = f"{os.path.splitext(input_path)[0]}_{uuid.uuid4().hex[:8]}.wav"
    try:
        ffmpeg.input(input_path).output(output_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000').run(quiet=True, overwrite_output=True)
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to convert to WAV: {e}")
    return output_path


def transcribe_audio(file_path: str) -> str:

    model = whisper_s2t.load_model(
        model_identifier="small",
        backend="CTranslate2",
        compute_type="int8",
        device="cuda"  # Change to "cpu" if no GPU
    )
    # Prepare file list and parameters
    files = [f"{file_path}"]
    tasks = ["transcribe"]
    initial_prompts = [None]

    # Transcribe with VAD (voice activity detection)
    out = model.transcribe_with_vad(
        files,
        tasks=tasks,
        initial_prompts=initial_prompts,
        batch_size=16
    )

    # Get first file's utterances
    utterances = out[0]

    formatted_segments = []
    full_text = ""

    for segment in utterances:
        formatted_segments.append({
            "start": segment["start_time"],
            "end": segment["end_time"],
            "text": segment["text"]
        })
        full_text += segment["text"].strip() + " "

    os.makedirs("transcripts_json", exist_ok=True)
    json_path = os.path.join("transcripts_json", "transcription_output.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(formatted_segments, f, ensure_ascii=False, indent=2)


    return full_text.strip(), formatted_segments


def audio_transcribe_node(state: InterviewState) -> InterviewState:
    try:
        if state.source_type == "youtube":
            transcript_text, full_transcript = transcribe_audio(state.audio_file_path)
        elif state.source_type == "audio":
            file_path = convert_to_wav(state.source_link_or_path)
            print("Path", file_path)
            transcript_text, full_transcript = transcribe_audio(file_path=file_path)
            state.wav_file_path = file_path
            
        state.transcript = transcript_text
        state.formatted_transcript_segments = full_transcript
        print(transcript_text)
    except Exception as e:
        raise RuntimeError(f"Audio transcription failed: {str(e)}")

    return state
