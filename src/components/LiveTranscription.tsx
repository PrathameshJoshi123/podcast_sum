import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Square, RotateCcw, Copy, Download, AlertTriangle } from 'lucide-react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

// Your LiveTranscription component
const LiveTranscription = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [wordCount, setWordCount] = useState(0);
  
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable
  } = useSpeechRecognition();

  // Update word count when transcript changes
  useEffect(() => {
    const words = transcript.trim().split(/\s+/).filter(word => word.length > 0);
    console.log("in useeffect",transcript)
    setWordCount(words.length);
  }, [transcript]);

  // Recording duration timer
  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      await SpeechRecognition.startListening({ 
        continuous: true,
        language: 'en-US',
        interimResults: true
      });
      setIsRecording(true);
      setRecordingDuration(0);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    SpeechRecognition.stopListening();
    setIsRecording(false);
  };

  const handleReset = () => {
    resetTranscript();
    setRecordingDuration(0);
    setWordCount(0);
  };

  const copyTranscript = async () => {
    try {
      await navigator.clipboard.writeText(transcript);
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy transcript:', error);
    }
  };

  const downloadTranscript = () => {
    const element = document.createElement('a');
    const file = new Blob([transcript], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `transcript-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Handle browser support check
  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-red-500/20 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-2xl font-bold">Browser Not Supported</h3>
          <p className="text-muted-foreground">
            Your browser doesn't support speech recognition. Please use Chrome or Safari for the best experience.
          </p>
        </div>
      </div>
    );
  }

  // Handle microphone permission
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
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto transition-all duration-300 ${
          isRecording 
            ? 'bg-red-500/20 animate-pulse' 
            : 'bg-gradient-to-br from-accent/20 to-accent/10'
        }`}>
          {isRecording ? (
            <Mic className="w-8 h-8 text-red-500 animate-pulse" />
          ) : (
            <Mic className="w-8 h-8 text-accent" />
          )}
        </div>
        <h3 className="text-2xl font-bold">Live Transcription</h3>
        <p className="text-muted-foreground">
          {isRecording 
            ? "Recording in progress - speak clearly into your microphone"
            : "Start real-time audio transcription for meetings or interviews"
          }
        </p>
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
        {(isRecording || transcript) && (
          <div className="flex items-center space-x-6 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'}`} />
              <span>{isRecording ? 'Recording' : 'Stopped'}</span>
            </div>
            <div>Duration: {formatDuration(recordingDuration)}</div>
            <div>Words: {wordCount}</div>
          </div>
        )}
      </div>

      {/* Transcript Display */}
      <div className="bg-muted/20 rounded-2xl p-6 min-h-[300px] space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-lg">Transcript</h4>
          {transcript && (
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
          {transcript ? (
            <p className="text-foreground leading-relaxed whitespace-pre-wrap">
              {transcript}
              {listening && <span className="inline-block w-1 h-5 bg-accent animate-pulse ml-1" />}
            </p>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
              <div className="text-4xl">🎙️</div>
              <p className="text-muted-foreground">
                {isRecording 
                  ? "Listening... Start speaking to see your words appear here"
                  : "Your transcription will appear here when you start recording"
                }
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
        <h5 className="font-medium text-blue-700 dark:text-blue-300 mb-2">💡 Tips for better transcription:</h5>
        <ul className="text-sm text-blue-600 dark:text-blue-400 space-y-1">
          <li>• Speak clearly and at a moderate pace</li>
          <li>• Use a quiet environment with minimal background noise</li>
          <li>• Keep your microphone close but not too close to avoid distortion</li>
          <li>• Pause briefly between sentences for better accuracy</li>
        </ul>
      </div>
    </div>
  );
};

export default LiveTranscription;