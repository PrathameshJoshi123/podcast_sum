import React, { useState, useEffect, useRef } from "react";
import {
  Mic,
  MicOff,
  Square,
  RotateCcw,
  Copy,
  Download,
  AlertTriangle,
  Upload,
  Loader2,
} from "lucide-react";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import { useApiUrl } from "../apiUrl";

const LiveTranscription = () => {
  const API_BASE_URL = useApiUrl();
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [wordCount, setWordCount] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [podcastType, setPodcastType] = useState("interview");
  const [summaryLanguage, setSummaryLanguage] = useState("English");
  
  // New states for continuous transcription
  const [finalTranscript, setFinalTranscript] = useState(""); // Accumulated final text
  const [currentInterim, setCurrentInterim] = useState(""); // Current interim text
  const [isRestarting, setIsRestarting] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const restartTimeoutRef = useRef(null);
  const lastFinalTranscriptRef = useRef("");

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();

  // Handle continuous transcription flow
  useEffect(() => {
    if (!isRecording) return;

    const currentTranscript = transcript.trim();
    
    // Check if we have new final text (when speech recognition provides complete sentences)
    if (currentTranscript && currentTranscript !== lastFinalTranscriptRef.current) {
      // If the current transcript is longer than what we had before, it means we got final text
      if (currentTranscript.length > lastFinalTranscriptRef.current.length) {
        const newFinalText = currentTranscript.substring(lastFinalTranscriptRef.current.length);
        if (newFinalText.trim()) {
          setFinalTranscript(prev => {
            const combined = prev + (prev ? " " : "") + newFinalText.trim();
            return combined;
          });
          lastFinalTranscriptRef.current = currentTranscript;
        }
      }
    }
    
    // Handle interim results (current speaking)
    setCurrentInterim(currentTranscript.substring(lastFinalTranscriptRef.current.length));
    
  }, [transcript, isRecording]);

  // Auto-restart speech recognition when it stops
  useEffect(() => {
    if (isRecording && !listening && !isRestarting) {
      console.log("Speech recognition stopped, restarting...");
      setIsRestarting(true);
      
      // Save any remaining transcript as final before restarting
      const remainingText = transcript.trim().substring(lastFinalTranscriptRef.current.length);
      if (remainingText) {
        setFinalTranscript(prev => {
          const combined = prev + (prev ? " " : "") + remainingText.trim();
          return combined;
        });
        lastFinalTranscriptRef.current = transcript.trim();
      }
      
      // Clear current interim since we're restarting
      setCurrentInterim("");
      
      restartTimeoutRef.current = setTimeout(() => {
        if (isRecording) {
          resetTranscript();
          SpeechRecognition.startListening({
            continuous: true,
            language: "en-US",
            interimResults: true,
          }).then(() => {
            setIsRestarting(false);
          }).catch((error) => {
            console.error("Error restarting speech recognition:", error);
            setIsRestarting(false);
          });
        }
      }, 500); // Small delay to prevent rapid restarts
    }

    return () => {
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
    };
  }, [listening, isRecording, isRestarting, transcript, resetTranscript]);

  // Calculate total word count
  useEffect(() => {
    const fullText = finalTranscript + " " + currentInterim;
    const words = fullText
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0);
    setWordCount(words.length);
  }, [finalTranscript, currentInterim]);

  // Recording duration timer
  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  const startRecording = async () => {
    try {
      // Reset all transcript states
      setFinalTranscript("");
      setCurrentInterim("");
      lastFinalTranscriptRef.current = "";
      resetTranscript();
      
      // Start speech recognition
      await SpeechRecognition.startListening({
        continuous: true,
        language: "en-US",
        interimResults: true,
      });

      // Start audio recording
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });

      streamRef.current = stream;
      audioChunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm;codecs=opus",
        });
        setAudioBlob(audioBlob);

        // Clean up stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
        }
      };

      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);
      setRecordingDuration(0);
      setUploadStatus("");
    } catch (error) {
      console.error("Error starting recording:", error);
      setUploadStatus("Error: Could not access microphone");
    }
  };

  const stopRecording = () => {
    // Save any remaining interim text as final
    const remainingText = currentInterim.trim();
    if (remainingText) {
      setFinalTranscript(prev => prev + (prev ? " " : "") + remainingText);
    }
    setCurrentInterim("");
    
    // Stop speech recognition
    SpeechRecognition.stopListening();

    // Stop audio recording
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === "recording"
    ) {
      mediaRecorderRef.current.stop();
    }

    setIsRecording(false);
    setIsRestarting(false);
    
    // Clear any pending restart
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
    }
  };

  const handleReset = () => {
    resetTranscript();
    setFinalTranscript("");
    setCurrentInterim("");
    lastFinalTranscriptRef.current = "";
    setRecordingDuration(0);
    setWordCount(0);
    setAudioBlob(null);
    setUploadStatus("");
    setIsRestarting(false);
    audioChunksRef.current = [];
    
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
    }
  };

  // Get the complete transcript for copying/downloading
  const getCompleteTranscript = () => {
    return (finalTranscript + " " + currentInterim).trim();
  };

  const copyTranscript = async () => {
    try {
      const completeText = getCompleteTranscript();
      await navigator.clipboard.writeText(completeText);
      setUploadStatus("Transcript copied to clipboard!");
      setTimeout(() => setUploadStatus(""), 3000);
    } catch (error) {
      console.error("Failed to copy transcript:", error);
    }
  };

  const downloadTranscript = () => {
    const completeText = getCompleteTranscript();
    const element = document.createElement("a");
    const file = new Blob([completeText], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = `transcript-${new Date()
      .toISOString()
      .slice(0, 10)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadAudio = () => {
    if (!audioBlob) return;

    const url = URL.createObjectURL(audioBlob);
    const element = document.createElement("a");
    element.href = url;
    element.download = `recording-${new Date()
      .toISOString()
      .slice(0, 10)}.webm`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    URL.revokeObjectURL(url);
  };

  const uploadToBackend = async () => {
    if (!audioBlob) return;

    setIsUploading(true);
    setUploadStatus("Uploading audio...");

    try {
      const formData = new FormData();
      formData.append("file", audioBlob, `recording-${Date.now()}.webm`);
      formData.append("podcast_type", podcastType);
      formData.append("summary_language", summaryLanguage);

      const response = await fetch(`${API_BASE_URL}/summarize/audio`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus("✅ Audio uploaded successfully!");
        console.log("Upload result:", result);
      } else {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadStatus("❌ Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadStatus(""), 5000);
    }
  };

  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-red-500/20 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-2xl font-bold">Browser Not Supported</h3>
          <p className="text-muted-foreground">
            Your browser doesn't support speech recognition. Please use Chrome
            or Safari for the best experience.
          </p>
        </div>
      </div>
    );
  }
  if (!isMicrophoneAvailable) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-yellow-500/20 flex items-center justify-center mx-auto">
            <MicOff className="w-8 h-8 text-yellow-500" />
          </div>
          <h3 className="text-2xl font-bold">Microphone Access Required</h3>
          <p className="text-muted-foreground">
            Please allow microphone access to use live transcription features.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center space-y-4">
        <div
          className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto transition-all duration-300 ${
            isRecording
              ? "bg-red-500/20 animate-pulse"
              : "bg-gradient-to-br from-accent/20 to-accent/10"
          }`}
        >
          {isRecording ? (
            <Mic className="w-8 h-8 text-red-500 animate-pulse" />
          ) : (
            <Mic className="w-8 h-8 text-accent" />
          )}
        </div>
        <h3 className="text-2xl font-bold">
          Live Transcription with Audio Recording
        </h3>
        <p className="text-muted-foreground">
          {isRecording
            ? "Recording audio and transcribing in real-time"
            : "Start recording to transcribe speech and save audio file"}
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Podcast Type</label>
          <select
            value={podcastType}
            onChange={(e) => setPodcastType(e.target.value)}
            className="w-full h-12 px-3 bg-background/50 border border-border/30 rounded-lg focus:border-primary/50 focus:outline-none"
          >
            <option value="interview">Interview</option>
            <option value="panel">Panel</option>
            <option value="monologue">Monologue</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">
            Summary Language
          </label>
          <select
            value={summaryLanguage}
            onChange={(e) => setSummaryLanguage(e.target.value)}
            className="w-full h-12 px-3 bg-background/50 border border-border/30 rounded-lg focus:border-primary/50 focus:outline-none"
          >
            <option value="English">English</option>
            <option value="Hindi">Hindi</option>
            <option value="Marathi">Marathi</option>
          </select>
        </div>
      </div>
      {/* Recording Controls */}
      <div className="flex flex-col items-center space-y-4">
        <div className="flex items-center space-x-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="bg-gradient-to-r from-accent to-accent/80 hover:shadow-[0_0_30px_hsl(var(--accent)/0.5)] transition-all duration-300 px-6 py-3 rounded-xl font-medium text-white flex items-center space-x-2"
            >
              <Mic className="w-5 h-5" />
              <span>Start Recording</span>
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-500 hover:bg-red-600 transition-all duration-300 px-6 py-3 rounded-xl font-medium text-white flex items-center space-x-2"
            >
              <Square className="w-5 h-5" />
              <span>Stop Recording</span>
            </button>
          )}

          <button
            onClick={handleReset}
            className="border border-muted-foreground/20 hover:bg-muted/50 transition-all duration-300 px-4 py-3 rounded-xl font-medium flex items-center space-x-2"
          >
            <RotateCcw className="w-5 h-5" />
            <span>Reset</span>
          </button>
        </div>

        {/* Recording Stats */}
        {(isRecording || finalTranscript || currentInterim) && (
          <div className="flex items-center space-x-6 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isRecording ? "bg-red-500 animate-pulse" : "bg-gray-400"
                }`}
              />
              <span>{isRecording ? "Recording" : "Stopped"}</span>
            </div>
            <div>Duration: {formatDuration(recordingDuration)}</div>
            <div>Words: {wordCount}</div>
            {audioBlob && (
              <div className="text-green-600">
                Audio: {(audioBlob.size / 1024 / 1024).toFixed(2)} MB
              </div>
            )}
            {isRestarting && (
              <div className="text-yellow-600 flex items-center space-x-1">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Reconnecting...</span>
              </div>
            )}
          </div>
        )}

        {/* Upload Status */}
        {uploadStatus && (
          <div
            className={`text-sm px-4 py-2 rounded-lg ${
              uploadStatus.includes("✅")
                ? "bg-green-100 text-green-700"
                : uploadStatus.includes("❌")
                ? "bg-red-100 text-red-700"
                : "bg-blue-100 text-blue-700"
            }`}
          >
            {uploadStatus}
          </div>
        )}
      </div>

      {/* Audio Controls */}
      {audioBlob && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h5 className="font-medium text-green-700 dark:text-green-300">
              🎵 Audio Recording Ready
            </h5>
            <div className="flex items-center space-x-2">
              <button
                onClick={downloadAudio}
                className="px-3 py-2 bg-green-500/20 hover:bg-green-500/30 rounded-lg transition-colors flex items-center space-x-2 text-sm"
                title="Download audio file"
              >
                <Download className="w-4 h-4" />
                <span>Download Audio</span>
              </button>
              <button
                onClick={uploadToBackend}
                disabled={isUploading}
                className="px-3 py-2 bg-blue-500/20 hover:bg-blue-500/30 disabled:opacity-50 rounded-lg transition-colors flex items-center space-x-2 text-sm"
                title="Upload to backend"
              >
                {isUploading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Upload className="w-4 h-4" />
                )}
                <span>{isUploading ? "Uploading..." : "Upload to Server"}</span>
              </button>
            </div>
          </div>
          <p className="text-sm text-green-600 dark:text-green-400">
            Audio file size: {(audioBlob.size / 1024 / 1024).toFixed(2)} MB |
            Format: WebM
          </p>
        </div>
      )}

      {/* Transcript Display */}
      <div className="bg-muted/20 rounded-2xl p-6 min-h-[300px] space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-lg">Continuous Transcript</h4>
          {(finalTranscript || currentInterim) && (
            <div className="flex items-center space-x-2">
              <button
                onClick={copyTranscript}
                className="p-2 hover:bg-muted/50 rounded-lg transition-colors"
                title="Copy transcript"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                onClick={downloadTranscript}
                className="p-2 hover:bg-muted/50 rounded-lg transition-colors"
                title="Download transcript"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        <div className="border-2 border-dashed border-muted-foreground/20 rounded-xl p-4 min-h-[200px] overflow-y-auto">
          {finalTranscript || currentInterim ? (
            <div className="text-foreground leading-relaxed whitespace-pre-wrap">
              {/* Final transcript - stable text */}
              <span className="text-foreground">{finalTranscript}</span>
              {/* Current interim - text being spoken now */}
              {currentInterim && (
                <>
                  {finalTranscript && " "}
                  <span className="text-foreground/70 bg-accent/10 px-1 rounded">
                    {currentInterim}
                  </span>
                </>
              )}
              {/* Cursor indicator when listening */}
              {listening && !isRestarting && (
                <span className="inline-block w-1 h-5 bg-accent animate-pulse ml-1" />
              )}
              {/* Reconnecting indicator */}
              {isRestarting && (
                <span className="inline-flex items-center ml-2 text-yellow-600">
                  <Loader2 className="w-3 h-3 animate-spin mr-1" />
                  <span className="text-xs">reconnecting...</span>
                </span>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
              <div className="text-4xl">🎙️</div>
              <p className="text-muted-foreground">
                {isRecording
                  ? "Listening... Start speaking to see your words appear here"
                  : "Your transcription will appear here when you start recording"}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
        <h5 className="font-medium text-blue-700 dark:text-blue-300 mb-2">
          💡 Tips for better continuous recording:
        </h5>
        <ul className="text-sm text-blue-600 dark:text-blue-400 space-y-1">
          <li>• Speak clearly and at a moderate pace</li>
          <li>• The system automatically reconnects during silence - keep speaking naturally</li>
          <li>• Gray highlighted text shows what you're currently saying</li>
          <li>• Previous text remains saved even when the system reconnects</li>
          <li>• Use a quiet environment with minimal background noise</li>
          <li>• Audio is recorded in WebM format for optimal quality</li>
        </ul>
      </div>
    </div>
  );
};

export default LiveTranscription;