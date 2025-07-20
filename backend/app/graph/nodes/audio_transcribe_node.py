import whisper_s2t
import json
import os
from app.model.state import InterviewState

os.environ["PATH"] = r"D:\My_Space\Podcast_Summarizer\cudnn\bin;" + os.environ["PATH"]
os.add_dll_directory(r"D:\My_Space\Podcast_Summarizer\cudnn\bin")

def transcribe_audio(file_path: str) -> str:
    print(file_path)
    # Load the model once globally
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

    # Format segments and combine text
    formatted_segments = []
    full_text = ""

    for segment in utterances:
        formatted_segments.append({
            "start": segment["start_time"],
            "end": segment["end_time"],
            "text": segment["text"]
        })
        full_text += segment["text"].strip() + " "

    # Save to JSON (optional for debugging)
    os.makedirs("transcripts_json", exist_ok=True)
    json_path = os.path.join("transcripts_json", "transcription_output.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(formatted_segments, f, ensure_ascii=False, indent=2)

    return full_text.strip()

# LangGraph node function
def audio_transcribe_node(state: InterviewState) -> InterviewState:
    # if not state.audio_file_path or state.source_link_or_path:
    #     print(state.audio_file_path)
    #     raise ValueError("Audio file path not provided")

    try:
        if state.source_type == "youtube":
            transcript_text = transcribe_audio(state.audio_file_path)
        elif state.source_type == "audio":
            transcript_text = transcribe_audio(state.source_link_or_path)
        state.transcript = transcript_text
        print(transcript_text)
    except Exception as e:
        raise RuntimeError(f"Audio transcription failed: {str(e)}")

    return state
