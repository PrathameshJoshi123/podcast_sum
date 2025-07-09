import streamlit as st
import requests
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import tempfile
from scipy.io.wavfile import write as write_wav

API_BASE_URL = "http://localhost:8000"  # Update if needed

st.title("🎙️ Podcast Summarizer")

st.sidebar.header("Choose input method")
input_method = st.sidebar.radio("Select source", ("YouTube link", "Audio file", "Live (Mic)"))

if input_method == "YouTube link":
    youtube_link = st.text_input("Enter YouTube link:")
    podcast_type = st.selectbox("Select the podcast type:", ["interview", "panel", "monologue"])
    summary_language = st.selectbox("Select the Summary Language:", ["English", "Hindi", "Marathi"])
    if st.button("Summarize YouTube"):
        if not youtube_link:
            st.warning("Please enter a valid YouTube link.")
        else:
            with st.spinner("Summarizing..."):
                response = requests.post(
                    f"{API_BASE_URL}/summarize/youtube",
                    json={"youtube_link": youtube_link, "podcast_type": podcast_type, "summary_language": summary_language}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("✅ Global Summary")
                    st.write(data["global_summary"])
                    
                    st.subheader("💬 Representative Sentences")
                    for rep in data["rep"]:
                        st.write(f"- {rep}")
                    
                    st.subheader("📄 QA Pairs")
                    st.markdown(data["qa"])

                    st.subheader("Transcript")
                    st.markdown(data["tra"])
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
elif input_method == "Audio file":
    uploaded_file = st.file_uploader("Upload audio file", type=["mp3", "wav", "m4a"])
    podcast_type = st.selectbox("Select the podcast type:", ["interview", "panel", "monologue"])
    summary_language = st.selectbox("Select the Summary Language:", ["English", "Hindi", "Marathi"])
    if st.button("Summarize Audio"):
        if not uploaded_file:
            st.warning("Please upload an audio file.")
        else:
            with st.spinner("Uploading and summarizing..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(f"{API_BASE_URL}/summarize/audio", files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("✅ Global Summary")
                    st.write(data["global_summary"])

                    st.subheader("📄 Topic Summaries")
                    if data["topic_summaries"]:
                        for ts in data["topic_summaries"]:
                            st.write(f"**Topic:** {ts['topic']}")
                            st.write(ts["summary"])
                            st.write("---")
                    else:
                        st.info("No topic summaries found.")

                    st.subheader("💬 QA Pairs")
                    if data["qa_pairs"]:
                        for qa in data["qa_pairs"]:
                            st.markdown(f"**Q:** {qa['question']}")
                            st.markdown(f"**A:** {qa['answer']}")
                            st.write("---")
                    else:
                        st.info("No QA pairs found.")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")

elif input_method == "Live (Mic)":
    st.info("🎤 Speak, and see your transcription live. When done, full summary will appear.")

    transcript_placeholder = st.empty()
    full_transcript = ""

    audio_frames = []

    def audio_callback(frame: av.AudioFrame):
        audio_frames.append(frame.to_ndarray())
        return frame

    webrtc_ctx = webrtc_streamer(
        key="live-mic",
        mode=WebRtcMode.SENDONLY,
        audio_frame_callback=audio_callback,
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )

    if not webrtc_ctx.state.playing and len(audio_frames) > 0:
        audio_data = np.concatenate(audio_frames)

        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write_wav(temp_wav.name, 48000, audio_data)

        # Get live transcription
        with open(temp_wav.name, "rb") as f:
            files = {"file": ("live_recording.wav", f, "audio/wav")}
            with st.spinner("Transcribing..."):
                response = requests.post(f"{API_BASE_URL}/transcribe/live", files=files)
                if response.status_code == 200:
                    data = response.json()
                    transcript_placeholder.markdown(data["transcript"])
                    full_transcript = data["transcript"]
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")

        # Once transcription shown, offer to summarize
        if st.button("Generate Summary & QA"):
            with open(temp_wav.name, "rb") as f:
                files = {"file": ("live_recording.wav", f, "audio/wav")}
                with st.spinner("Generating summary..."):
                    response = requests.post(f"{API_BASE_URL}/summarize/audio", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.subheader("✅ Global Summary")
                        st.write(data["global_summary"])

                        st.subheader("📄 Topic Summaries")
                        if data["topic_summaries"]:
                            for ts in data["topic_summaries"]:
                                st.write(f"**Topic:** {ts['topic']}")
                                st.write(ts["summary"])
                                st.write("---")
                        else:
                            st.info("No topic summaries found.")

                        st.subheader("💬 QA Pairs")
                        if data["qa_pairs"]:
                            for qa in data["qa_pairs"]:
                                st.markdown(f"**Q:** {qa['question']}")
                                st.markdown(f"**A:** {qa['answer']}")
                                st.write("---")
                        else:
                            st.info("No QA pairs found.")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")


st.sidebar.markdown("---")
st.sidebar.info("👋 Make sure your FastAPI server is running at the specified API base URL.")
