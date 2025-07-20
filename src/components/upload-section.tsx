import { useState, useRef, useEffect } from "react";
import { GlassCard } from "./ui/glass-card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Upload,
  Youtube,
  Link,
  File,
  Mic,
  ArrowRight,
  Sparkles,
  X,
  Music,
  Clock,
  FileAudio,
  Loader2,
  Play,
  Square,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

interface UploadedFile {
  file: File;
  name: string;
  size: string;
  duration?: string;
  type: string;
}

interface Summary {
  title: string;
  mainPoints: string[];
  keyInsights: string[];
  speakers?: string[];
  duration?: string;
  timestamp: string;
}

interface LiveTranscript {
  id: string;
  text: string;
  timestamp: string;
  confidence?: number;
}

export function UploadSection() {
  const [activeTab, setActiveTab] = useState<"youtube" | "upload" | "live">("youtube");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  
  // Processing states
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState("");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Live recording states
  const [isRecording, setIsRecording] = useState(false);
  const [liveTranscripts, setLiveTranscripts] = useState<LiveTranscript[]>([]);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [liveSummary, setLiveSummary] = useState<Summary | null>(null);
  
  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Helper function to format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Helper function to get audio duration
  const getAudioDuration = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const audio = document.createElement('audio');
      const url = URL.createObjectURL(file);
      
      audio.addEventListener('loadedmetadata', () => {
        const duration = audio.duration;
        const minutes = Math.floor(duration / 60);
        const seconds = Math.floor(duration % 60);
        URL.revokeObjectURL(url);
        resolve(`${minutes}:${seconds.toString().padStart(2, '0')}`);
      });
      
      audio.addEventListener('error', () => {
        URL.revokeObjectURL(url);
        resolve('Unknown');
      });
      
      audio.src = url;
    });
  };

  // Format recording duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Backend API functions (replace with your actual API endpoints)
  const processYouTubeUrl = async (url: string): Promise<Summary> => {
    const response = await fetch('/api/process-youtube', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to process YouTube URL: ${response.statusText}`);
    }
    
    return await response.json();
  };

  const processAudioFile = async (file: File): Promise<Summary> => {
    const formData = new FormData();
    formData.append('audio', file);
    
    const response = await fetch('/api/process-audio', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to process audio file: ${response.statusText}`);
    }
    
    return await response.json();
  };

  const processLiveTranscripts = async (transcripts: LiveTranscript[]): Promise<Summary> => {
    const response = await fetch('/api/process-live-transcripts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcripts }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to process live transcripts: ${response.statusText}`);
    }
    
    return await response.json();
  };

  // Handle YouTube URL processing
  const handleYouTubeAnalysis = async () => {
    if (!youtubeUrl.trim()) return;
    
    setIsProcessing(true);
    setProcessingStatus("Fetching YouTube content...");
    setError(null);
    setSummary(null);
    
    try {
      setProcessingStatus("Transcribing audio...");
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
      
      setProcessingStatus("Generating summary...");
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
      
      const result = await processYouTubeUrl(youtubeUrl);
      setSummary(result);
      setProcessingStatus("Analysis complete!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle file upload processing
  const handleFileAnalysis = async () => {
    if (!uploadedFile) return;
    
    setIsProcessing(true);
    setProcessingStatus("Uploading file...");
    setError(null);
    setSummary(null);
    
    try {
      setProcessingStatus("Processing audio...");
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate delay
      
      setProcessingStatus("Generating summary...");
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate delay
      
      const result = await processAudioFile(uploadedFile.file);
      setSummary(result);
      setProcessingStatus("Analysis complete!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsProcessing(false);
    }
  };

  // Live recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const audioChunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        // Here you would typically send the audio blob to your transcription service
        console.log('Recording stopped, audio blob created:', audioBlob);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingDuration(0);
      
      // Start timer
      recordingTimerRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
      
      // Simulate real-time transcription
      simulateRealTimeTranscription();
      
    } catch (err) {
      setError("Failed to access microphone. Please check your permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && streamRef.current) {
      mediaRecorderRef.current.stop();
      streamRef.current.getTracks().forEach(track => track.stop());
      
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
      
      setIsRecording(false);
      generateLiveSummary();
    }
  };

  // Simulate real-time transcription (replace with actual WebSocket or API calls)
  const simulateRealTimeTranscription = () => {
    const sampleTexts = [
      "Welcome to today's podcast discussion.",
      "We're talking about the future of artificial intelligence.",
      "The implications for businesses are quite significant.",
      "Let's dive into the technical aspects first.",
      "Machine learning has evolved tremendously over the past decade.",
    ];
    
    let index = 0;
    const addTranscript = () => {
      if (index < sampleTexts.length && isRecording) {
        const newTranscript: LiveTranscript = {
          id: `transcript-${Date.now()}-${index}`,
          text: sampleTexts[index],
          timestamp: new Date().toLocaleTimeString(),
          confidence: 0.85 + Math.random() * 0.1,
        };
        
        setLiveTranscripts(prev => [...prev, newTranscript]);
        index++;
        
        if (index < sampleTexts.length) {
          setTimeout(addTranscript, 3000 + Math.random() * 2000);
        }
      }
    };
    
    setTimeout(addTranscript, 2000);
  };

  const generateLiveSummary = async () => {
    if (liveTranscripts.length === 0) return;
    
    setIsProcessing(true);
    setProcessingStatus("Generating live session summary...");
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate processing
      const result = await processLiveTranscripts(liveTranscripts);
      setLiveSummary(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate summary");
    } finally {
      setIsProcessing(false);
    }
  };

  // File upload handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('audio/') || 
          file.name.match(/\.(mp3|wav|m4a|flac|aac|ogg)$/i)) {
        handleFileUpload(file);
      } else {
        setError("Invalid file type. Please upload an audio file.");
      }
    }
  };

  const handleFileUpload = async (file: File) => {
    setError(null);
    
    const duration = await getAudioDuration(file);
    const fileInfo: UploadedFile = {
      file: file,
      name: file.name,
      size: formatFileSize(file.size),
      duration: duration,
      type: file.type || 'audio/unknown'
    };
    
    setUploadedFile(fileInfo);
  };

  const handleCancelUpload = () => {
    setUploadedFile(null);
    setSummary(null);
    setError(null);
  };

  const triggerFileInput = () => {
    const fileInput = document.getElementById('file-upload') as HTMLInputElement;
    fileInput?.click();
  };

  // Reset state when switching tabs
  const handleTabChange = (newTab: "youtube" | "upload" | "live") => {
    setActiveTab(newTab);
    setSummary(null);
    setLiveSummary(null);
    setError(null);
    setIsProcessing(false);
    setLiveTranscripts([]);
    
    if (newTab !== "live" && isRecording) {
      stopRecording();
    }
  };

  const tabs = [
    { id: "youtube", label: "YouTube Link", icon: Youtube },
    { id: "upload", label: "Upload File", icon: Upload },
    { id: "live", label: "Live Audio", icon: Mic },
  ];

  // Summary Component
  const SummaryDisplay = ({ summary, title }: { summary: Summary; title: string }) => (
    <GlassCard variant="glow" className="mt-6 p-6">
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <CheckCircle className="w-6 h-6 text-green-500" />
          <h3 className="text-xl font-bold">{title}</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-lg mb-2">{summary.title}</h4>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              {summary.duration && (
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {summary.duration}
                </span>
              )}
              <span>Generated at {summary.timestamp}</span>
            </div>
          </div>
          
          <div>
            <h5 className="font-medium mb-2">Key Points:</h5>
            <ul className="space-y-1 text-muted-foreground">
              {summary.mainPoints.map((point, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                  {point}
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h5 className="font-medium mb-2">Key Insights:</h5>
            <ul className="space-y-1 text-muted-foreground">
              {summary.keyInsights.map((insight, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
          
          {summary.speakers && summary.speakers.length > 0 && (
            <div>
              <h5 className="font-medium mb-2">Speakers:</h5>
              <div className="flex flex-wrap gap-2">
                {summary.speakers.map((speaker, index) => (
                  <span key={index} className="px-3 py-1 bg-muted/30 rounded-full text-sm">
                    {speaker}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );

  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 relative">
      <div className="max-w-4xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary/10 border border-secondary/20 rounded-full text-sm text-secondary font-medium">
            <Sparkles className="w-4 h-4" />
            Get Started Now
          </div>
          <h2 className="text-3xl md:text-5xl font-bold">
            <span className="text-foreground">Ready to</span>
            <br />
            <span className="bg-gradient-secondary bg-clip-text text-transparent">
              analyze your podcast?
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose your preferred method below and experience the power of
            AI-driven podcast analysis.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-muted/20 rounded-2xl p-1 backdrop-blur-sm border border-border/20">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl transition-all duration-300 ${
                  activeTab === tab.id
                    ? "bg-gradient-primary text-primary-foreground shadow-lg"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <GlassCard className="mb-6 p-4 border-red-500/20 bg-red-500/5">
            <div className="flex items-center gap-3 text-red-400">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          </GlassCard>
        )}

        {/* Processing Status */}
        {isProcessing && (
          <GlassCard className="mb-6 p-6">
            <div className="flex items-center gap-3">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
              <div>
                <p className="font-medium">Processing...</p>
                <p className="text-sm text-muted-foreground">{processingStatus}</p>
              </div>
            </div>
          </GlassCard>
        )}

        {/* Content Areas */}
        <GlassCard variant="glow" className="p-8">
          {activeTab === "youtube" && (
            <div className="space-y-6 animate-fade-in">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center mx-auto">
                  <Youtube className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-2xl font-bold">Paste YouTube URL</h3>
                <p className="text-muted-foreground">
                  Enter the YouTube link of the podcast you want to analyze
                </p>
              </div>

              <div className="space-y-4">
                <div className="relative">
                  <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    placeholder="https://youtube.com/watch?v=..."
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    className="pl-12 h-14 bg-background/50 border-border/30 focus:border-primary/50"
                    disabled={isProcessing}
                  />
                </div>
                <Button
                  className="w-full h-14 bg-gradient-primary hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)] transition-all duration-300"
                  disabled={!youtubeUrl.trim() || isProcessing}
                  onClick={handleYouTubeAnalysis}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      Analyze Podcast
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {activeTab === "upload" && (
            <div className="space-y-6 animate-fade-in">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-secondary/20 to-secondary/10 flex items-center justify-center mx-auto">
                  <Upload className="w-8 h-8 text-secondary" />
                </div>
                <h3 className="text-2xl font-bold">Upload Audio File</h3>
                <p className="text-muted-foreground">
                  Support for MP3, WAV, and other audio formats
                </p>
              </div>

              {!uploadedFile ? (
                <div
                  className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${
                    isDragging
                      ? "border-secondary bg-secondary/10"
                      : "border-border/30 hover:border-secondary/50"
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={triggerFileInput}
                >
                  <File className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <div className="space-y-2">
                    <p className="text-lg font-medium">Drop your audio file here</p>
                    <p className="text-muted-foreground">or click to browse</p>
                    <p className="text-sm text-muted-foreground">
                      Max file size: 500MB • Supports MP3, WAV, M4A, FLAC, AAC
                    </p>
                  </div>

                  <input
                    id="file-upload"
                    type="file"
                    accept=".mp3,.wav,.m4a,.flac,.aac,.ogg,audio/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        handleFileUpload(file);
                      }
                    }}
                  />

                  <div className="mt-4" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="outline"
                      className="border-secondary/30 hover:border-secondary hover:bg-secondary/10"
                      onClick={triggerFileInput}
                    >
                      Choose File
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-muted/20 rounded-2xl p-6 border border-border/20">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-secondary/20 flex items-center justify-center flex-shrink-0">
                        <FileAudio className="w-6 h-6 text-secondary" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0 flex-1">
                            <h4 className="font-semibold text-lg truncate" title={uploadedFile.name}>
                              {uploadedFile.name}
                            </h4>
                            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <File className="w-4 h-4" />
                                {uploadedFile.size}
                              </div>
                              {uploadedFile.duration && uploadedFile.duration !== 'Unknown' && (
                                <div className="flex items-center gap-1">
                                  <Clock className="w-4 h-4" />
                                  {uploadedFile.duration}
                                </div>
                              )}
                              <div className="flex items-center gap-1">
                                <Music className="w-4 h-4" />
                                {uploadedFile.type.split('/')[1]?.toUpperCase() || 'AUDIO'}
                              </div>
                            </div>
                          </div>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleCancelUpload}
                            className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
                            disabled={isProcessing}
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={handleCancelUpload}
                      className="flex-1"
                      disabled={isProcessing}
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Different File
                    </Button>
                    
                    <Button
                      className="flex-1 bg-gradient-secondary hover:shadow-[0_0_30px_hsl(var(--secondary)/0.5)] transition-all duration-300"
                      onClick={handleFileAnalysis}
                      disabled={isProcessing}
                    >
                      {isProcessing ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          Analyze Audio
                          <ArrowRight className="w-4 h-4 ml-2" />
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === "live" && (
            <div className="space-y-6 animate-fade-in">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent/20 to-accent/10 flex items-center justify-center mx-auto">
                  <Mic className={`w-8 h-8 text-accent ${isRecording ? 'animate-pulse' : ''}`} />
                </div>
                <h3 className="text-2xl font-bold">Live Transcription</h3>
                <p className="text-muted-foreground">
                  Start real-time audio transcription for meetings or interviews
                </p>
              </div>

              <div className="bg-muted/20 rounded-2xl p-8 text-center space-y-6">
                {!isRecording ? (
                  <>
                    <div className="text-6xl">🎙️</div>
                    <p className="text-lg font-medium">Ready to start recording</p>
                    <p className="text-muted-foreground">
                      Click the button below to begin live transcription
                    </p>
                    <Button 
                      className="bg-gradient-to-r from-accent to-accent/80 hover:shadow-[0_0_30px_hsl(var(--accent)/0.5)] transition-all duration-300"
                      onClick={startRecording}
                      disabled={isProcessing}
                    >
                      Start Recording
                      <Mic className="w-5 h-5 ml-2" />
                    </Button>
                  </>
                ) : (
                  <>
                    <div className="space-y-4">
                      <div className="text-red-500 text-4xl animate-pulse">🔴</div>
                      <p className="text-lg font-medium">Recording in progress...</p>
                      <p className="text-2xl font-mono">{formatDuration(recordingDuration)}</p>
                    </div>
                    <Button 
                      variant="destructive"
                      className="bg-red-600 hover:bg-red-700"
                      onClick={stopRecording}
                    >
                      <Square className="w-5 h-5 mr-2" />
                      Stop Recording
                    </Button>
                  </>
                )}
              </div>

              {/* Live Transcripts */}
              {liveTranscripts.length > 0 && (
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold">Live Transcript</h4>
                  <div className="bg-muted/20 rounded-2xl p-4 max-h-64 overflow-y-auto space-y-3">
                    {liveTranscripts.map((transcript) => (
                      <div key={transcript.id} className="flex items-start gap-3">
                        <span className="text-xs text-muted-foreground bg-muted/30 px-2 py-1 rounded flex-shrink-0">
                          {transcript.timestamp}
                        </span>
                        <p className="text-sm">{transcript.text}</p>
                        {transcript.confidence && (
                          <span className="text-xs text-muted-foreground ml-auto">
                            {Math.round(transcript.confidence * 100)}%
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </GlassCard>

        {/* Display Summaries */}
        {summary && <SummaryDisplay summary={summary} title="Analysis Complete" />}
        {liveSummary && <SummaryDisplay summary={liveSummary} title="Live Session Summary" />}
      </div>
    </section>
  );
}