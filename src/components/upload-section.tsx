import { useContext, useState } from "react";
import { GlassCard } from "./ui/glass-card";
// Summary Results Component
import React from "react";
import Markdown from "react-markdown";

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
  CheckCircle,
  AlertCircle,
  Loader2,
  MessageSquare,
  FileText,
  Globe,
} from "lucide-react";
import { ApiUrlContext, useApiUrl } from "../apiUrl";
import remarkGfm from "remark-gfm";

interface UploadedFile {
  file: File;
  name: string;
  size: string;
  duration?: string;
  type: string;
}

interface SummaryData {
  global_summary?: string;
  qa?: string;
  tra?: string;
  topic_summaries?: Array<{
    topic: string;
    summary: string;
  }>;
  // qa_pairs?: Array<{
  //   question: string;
  //   answer: string;
  // }>;
}

interface ApiError {
  error: string;
}

export function UploadSection() {
  const API_BASE_URL = useApiUrl();
  const [activeTab, setActiveTab] = useState<"youtube" | "upload" | "live">(
    "youtube"
  );
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [podcastType, setPodcastType] = useState("interview");
  const [summaryLanguage, setSummaryLanguage] = useState("English");

  // API Functions
  const analyzeYouTube = async (
    url: string,
    type: string,
    language: string
  ): Promise<SummaryData> => {
    const response = await fetch(`${API_BASE_URL}/summarize/youtube`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        youtube_link: url,
        podcast_type: type,
        summary_language: language,
      }),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || "Failed to analyze YouTube video");
    }

    return response.json();
  };

  const analyzeAudio = async (
    file: File,
    type: string,
    language: string
  ): Promise<SummaryData> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("podcast_type", type);
    formData.append("summary_language", language);

    const response = await fetch(`${API_BASE_URL}/summarize/audio`, {
      method: "POST",
      // body: formData,
      body: formData,
    });
    console.log("file upload", response)
    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || "Failed to analyze audio file");
    }

    return response.json();
  };

  const transcribeLive = async (
    file: File
  ): Promise<{ transcript: string }> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/transcribe/live`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || "Failed to transcribe audio");
    }

    return response.json();
  };

  // Handler Functions
  const handleYouTubeAnalysis = async () => {
    if (!youtubeUrl.trim()) return;

    setIsLoading(true);
    setError(null);
    setSummaryData(null);

    try {
      const data = await analyzeYouTube(
        youtubeUrl,
        podcastType,
        summaryLanguage
      );
      setSummaryData(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleAudioAnalysis = async () => {
    if (!uploadedFile) return;

    setIsLoading(true);
    setError(null);
    setSummaryData(null);

    try {
      const data = await analyzeAudio(
        uploadedFile.file,
        podcastType,
        summaryLanguage
      );
      setSummaryData(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Helper functions
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getAudioDuration = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const audio = document.createElement("audio");
      const url = URL.createObjectURL(file);

      audio.addEventListener("loadedmetadata", () => {
        const duration = audio.duration;
        const minutes = Math.floor(duration / 60);
        const seconds = Math.floor(duration % 60);
        URL.revokeObjectURL(url);
        resolve(`${minutes}:${seconds.toString().padStart(2, "0")}`);
      });

      audio.addEventListener("error", () => {
        URL.revokeObjectURL(url);
        resolve("Unknown");
      });

      audio.src = url;
    });
  };

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
      if (
        file.type.startsWith("audio/") ||
        file.name.match(/\.(mp3|wav|m4a|flac|aac|ogg)$/i)
      ) {
        handleFileUpload(file);
      }
    }
  };

  const handleFileUpload = async (file: File) => {
    const duration = await getAudioDuration(file);

    const fileInfo: UploadedFile = {
      file: file,
      name: file.name,
      size: formatFileSize(file.size),
      duration: duration,
      type: file.type || "audio/unknown",
    };

    setUploadedFile(fileInfo);
    // Clear previous results when new file is uploaded
    setSummaryData(null);
    setError(null);
  };

  const handleCancelUpload = () => {
    setUploadedFile(null);
    setSummaryData(null);
    setError(null);
  };

  const triggerFileInput = () => {
    const fileInput = document.getElementById(
      "file-upload"
    ) as HTMLInputElement;
    fileInput?.click();
  };

  const resetAnalysis = () => {
    setSummaryData(null);
    setError(null);
    setYoutubeUrl("");
    setUploadedFile(null);
  };

  const tabs = [
    { id: "youtube", label: "YouTube Link", icon: Youtube },
    { id: "upload", label: "Upload File", icon: Upload },
    { id: "live", label: "Live Audio", icon: Mic },
  ];

  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 relative">
      <div className="max-w-6xl mx-auto">
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

        {/* Show results if available */}
        {summaryData && (
          <div className="mb-16">
            <SummaryResults
              data={summaryData}
              onReset={resetAnalysis}
              activeTab={activeTab}
            />
          </div>
        )}

        {/* Show error if available */}
        {error && (
          <div className="mb-8">
            <GlassCard
              variant="glow"
              className="p-6 bg-destructive/5 border-destructive/20"
            >
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-destructive">
                    Analysis Failed
                  </h3>
                  <p className="text-destructive/80">{error}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setError(null)}
                  className="ml-auto text-destructive hover:bg-destructive/10"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </GlassCard>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-muted/20 rounded-2xl p-1 backdrop-blur-sm border border-border/20">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
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

              <div className="space-y-6">
                {/* Configuration Options */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Podcast Type
                    </label>
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

                <div className="relative">
                  <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    placeholder="https://youtube.com/watch?v=..."
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    className="pl-12 h-14 bg-background/50 border-border/30 focus:border-primary/50"
                    disabled={isLoading}
                  />
                </div>

                <Button
                  className="w-full h-14 bg-gradient-primary hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)] transition-all duration-300"
                  disabled={!youtubeUrl.trim() || isLoading}
                  onClick={handleYouTubeAnalysis}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Analyzing...
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
                    <p className="text-lg font-medium">
                      Drop your audio file here
                    </p>
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
                            <h4
                              className="font-semibold text-lg truncate"
                              title={uploadedFile.name}
                            >
                              {uploadedFile.name}
                            </h4>
                            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <File className="w-4 h-4" />
                                {uploadedFile.size}
                              </div>
                              {uploadedFile.duration &&
                                uploadedFile.duration !== "Unknown" && (
                                  <div className="flex items-center gap-1">
                                    <Clock className="w-4 h-4" />
                                    {uploadedFile.duration}
                                  </div>
                                )}
                              <div className="flex items-center gap-1">
                                <Music className="w-4 h-4" />
                                {uploadedFile.type
                                  .split("/")[1]
                                  ?.toUpperCase() || "AUDIO"}
                              </div>
                            </div>
                          </div>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleCancelUpload}
                            className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
                            disabled={isLoading}
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Configuration Options */}
                  <div className="bg-muted/10 rounded-2xl p-6 border border-border/20 space-y-4">
                    <h4 className="text-lg font-semibold mb-4">
                      Analysis Configuration
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Podcast Type
                        </label>
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
                  </div>

                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={handleCancelUpload}
                      className="flex-1"
                      disabled={isLoading}
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Different File
                    </Button>

                    <Button
                      className="flex-1 bg-gradient-secondary hover:shadow-[0_0_30px_hsl(var(--secondary)/0.5)] transition-all duration-300"
                      onClick={handleAudioAnalysis}
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Analyzing...
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
                  <Mic className="w-8 h-8 text-accent animate-glow-pulse" />
                </div>
                <h3 className="text-2xl font-bold">Live Transcription</h3>
                <p className="text-muted-foreground">
                  Start real-time audio transcription for meetings or interviews
                </p>
              </div>

              <div className="bg-muted/20 rounded-2xl p-8 text-center space-y-4">
                <div className="text-6xl">🎙️</div>
                <p className="text-lg font-medium">Ready to start recording</p>
                <p className="text-muted-foreground">
                  Click the button below to begin live transcription
                </p>
                <Button className="bg-gradient-to-r from-accent to-accent/80 hover:shadow-[0_0_30px_hsl(var(--accent)/0.5)] transition-all duration-300">
                  Start Recording
                  <Mic className="w-5 h-5 ml-2" />
                </Button>
              </div>
            </div>
          )}
        </GlassCard>
      </div>
    </section>
  );
}

interface TopicSummary {
  topic: string;
  summary: string;
}

interface QAPair {
  question: string;
  answer: string;
}

interface SummaryData {
  global_summary?: string;
  qa?: string;
  tra?: string;
  topic_summaries?: TopicSummary[];
  qa_pairs?: QAPair[];
}

function SummaryResults({
  data,
  onReset,
  activeTab,
}: {
  data: SummaryData;
  onReset: () => void;
  activeTab: string;
}) {
  // Custom markdown components for consistent styling
  const markdownComponents = {
    // Headings
    h1: ({ children, ...props }) => (
      <h1
        className="text-xl font-bold text-primary mt-0 mb-4 flex items-start group"
        {...props}
      >
        <div className="w-2 h-6 bg-gradient-to-b from-primary to-primary/70 rounded-full mr-3 mt-1 flex-shrink-0 group-hover:scale-110 transition-transform"></div>
        <span className="text-left">{children}</span>
      </h1>
    ),
    h2: ({ children, ...props }) => (
      <h2
        className="text-lg font-bold text-primary/90 mt-6 mb-3 flex items-start group"
        {...props}
      >
        <div className="w-1.5 h-5 bg-gradient-to-b from-primary/80 to-primary/50 rounded-full mr-3 mt-1 flex-shrink-0 group-hover:scale-110 transition-transform"></div>
        <span className="text-left">{children}</span>
      </h2>
    ),
    h3: ({ children, ...props }) => (
      <h3
        className="text-base font-semibold text-primary/80 mt-4 mb-2 flex items-start group"
        {...props}
      >
        <div className="w-1 h-4 bg-gradient-to-b from-primary/60 to-primary/40 rounded-full mr-3 mt-1 flex-shrink-0 group-hover:scale-110 transition-transform"></div>
        <span className="text-left">{children}</span>
      </h3>
    ),

    // Paragraphs
    p: ({ children, ...props }) => (
      <p
        className="mb-3 text-muted-foreground leading-relaxed text-sm text-left"
        {...props}
      >
        {children}
      </p>
    ),

    // Lists
    ul: ({ children, ...props }) => (
      <ul className="my-3 space-y-2" {...props}>
        {children}
      </ul>
    ),
    ol: ({ children, ...props }) => (
      <ol className="my-3 space-y-2" {...props}>
        {children}
      </ol>
    ),
    li: ({ children, ...props }) => (
      <li
        className="text-muted-foreground text-sm group flex items-start"
        {...props}
      >
        <div className="w-1.5 h-1.5 bg-primary/60 rounded-full mt-2 mr-3 flex-shrink-0 group-hover:scale-125 transition-transform"></div>
        <span className="text-left flex-1">{children}</span>
      </li>
    ),

    // Code
    code: ({ inline, className, children, ...props }) => {
      if (inline) {
        return (
          <code
            className="bg-primary/10 text-primary px-1.5 py-0.5 rounded-md text-xs border border-primary/20 font-mono"
            {...props}
          >
            {children}
          </code>
        );
      }
      return (
        <code className="text-primary font-mono text-xs" {...props}>
          {children}
        </code>
      );
    },
    pre: ({ children, ...props }) => (
      <div className="bg-muted/30 border border-primary/10 rounded-lg p-4 my-4 font-mono text-xs backdrop-blur-sm overflow-x-auto">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs text-muted-foreground uppercase tracking-wide">
            Code
          </span>
          <div className="flex space-x-1">
            <div className="w-1.5 h-1.5 bg-red-400 rounded-full"></div>
            <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full"></div>
            <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
          </div>
        </div>
        <pre className="text-foreground text-left overflow-x-auto" {...props}>
          {children}
        </pre>
      </div>
    ),

    // Emphasis
    strong: ({ children, ...props }) => (
      <strong
        className="text-primary font-semibold bg-primary/5 px-1 rounded"
        {...props}
      >
        {children}
      </strong>
    ),
    em: ({ children, ...props }) => (
      <em className="text-primary/80 italic" {...props}>
        {children}
      </em>
    ),

    // Links
    a: ({ children, href, ...props }) => (
      <a
        href={href}
        className="text-primary hover:text-primary/80 underline decoration-primary/50 hover:decoration-primary transition-colors break-words"
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    ),

    // Blockquotes
    blockquote: ({ children, ...props }) => (
      <blockquote
        className="border-l-4 border-primary/50 pl-4 py-2 my-4 bg-primary/5 rounded-r-lg italic text-muted-foreground"
        {...props}
      >
        {children}
      </blockquote>
    ),

    // Horizontal rule
    hr: ({ ...props }) => (
      <hr
        className="my-6 border-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent"
        {...props}
      />
    ),

    // Images
    img: ({ src, alt, ...props }) => (
      <img
        src={src}
        alt={alt}
        className="max-w-full h-auto rounded-lg shadow-lg my-3"
        {...props}
      />
    ),
  };

  const renderMarkdownContent = (content: string) => (
    <div className="prose prose-neutral dark:prose-invert max-w-none">
      <Markdown components={markdownComponents} remarkPlugins={[remarkGfm]}>
        {content}
      </Markdown>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckCircle className="w-6 h-6 text-green-500" />
          <h3 className="text-2xl font-bold">Analysis Complete</h3>
        </div>
        <Button
          variant="outline"
          onClick={onReset}
          className="hover:bg-destructive/10 hover:text-destructive"
        >
          <X className="w-4 h-4 mr-2" />
          Clear Results
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Global Summary with Markdown */}
        {data.global_summary && (
          <GlassCard variant="glow" className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <Globe className="w-5 h-5 text-primary" />
              </div>
              <h4 className="text-xl font-bold">Global Summary</h4>
            </div>
            {renderMarkdownContent(data.global_summary)}
          </GlassCard>
        )}

        {/* YouTube-specific content */}
        {activeTab === "youtube" && (
          <>
            {data.qa && (
              <GlassCard variant="glow" className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-secondary/20 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-secondary" />
                  </div>
                  <h4 className="text-xl font-bold">Q&A Pairs</h4>
                </div>
                {renderMarkdownContent(data.qa)}
              </GlassCard>
            )}

          </>
        )}

        {/* Audio file-specific content */}
        {activeTab === "upload" && (
          <>
            {data.qa && (
              <GlassCard variant="glow" className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-secondary/20 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-secondary" />
                  </div>
                  <h4 className="text-xl font-bold">Q&A Pairs</h4>
                </div>
                {renderMarkdownContent(data.qa)}
              </GlassCard>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// export default SummaryResults;

export default UploadSection;
