import os
import subprocess
import re
from app.model.state import InterviewState

import os
import re
import subprocess
import yt_dlp

def download_youtube_audio(youtube_url: str, output_dir: str = "temp_audio") -> tuple:
    os.makedirs(output_dir, exist_ok=True)

    # Extract video ID to create a clean file name
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", youtube_url)
    if not match:
        raise ValueError("Could not extract video ID from URL")
    video_id = match.group(1)

    # Get video info using yt_dlp
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        title = info.get("title", "unknown_title")
        channel = info.get("uploader", "unknown_channel")

    # Paths
    audio_path = os.path.join(output_dir, f"{video_id}.mp3")
    wav_path = os.path.join(output_dir, f"{video_id}.wav")

    # Step 1️⃣ Download as MP3
    print("🎥 Downloading audio from YouTube...")
    command_download = [
        "yt-dlp", "-x", "--audio-format", "mp3",
        "-o", audio_path,
        youtube_url
    ]
    subprocess.run(command_download, check=True)

    # Step 2️⃣ Convert to WAV (16kHz mono)
    print("🎼 Converting to WAV (16kHz mono)...")
    command_convert = [
        "ffmpeg", "-i", audio_path,
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ]
    subprocess.run(command_convert, check=True)

    # Final check
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file not found at: {wav_path}")

    print(f"✅ Audio ready at: {wav_path}")
    return wav_path, video_id, title, channel


# LangGraph node function
def yt_audio_download_node(state: InterviewState) -> InterviewState:
    if not state.source_link_or_path:
        state.error_message = "YouTube link not provided"
        return state

    try:
        audio_file_path, video_id , title, channel= download_youtube_audio(state.source_link_or_path)
        state.audio_file_path = audio_file_path
        state.video_id = video_id
        channel_and_title = []
        channel_and_title.append(title)
        channel_and_title.append(channel)
        state.channel_and_title = channel_and_title
    except Exception as e:
        state.error_message = f"Failed to download audio: {str(e)}"

    return state
