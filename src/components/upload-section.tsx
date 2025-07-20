import { useState } from "react"
import { GlassCard } from "./ui/glass-card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Upload, Youtube, Link, File, Mic, ArrowRight, Sparkles } from "lucide-react"

export function UploadSection() {
  const [activeTab, setActiveTab] = useState<"youtube" | "upload" | "live">("youtube")
  const [youtubeUrl, setYoutubeUrl] = useState("")
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    // Handle file drop logic here
  }

  const tabs = [
    { id: "youtube", label: "YouTube Link", icon: Youtube },
    { id: "upload", label: "Upload File", icon: Upload },
    { id: "live", label: "Live Audio", icon: Mic }
  ]

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
            <span className="bg-gradient-secondary bg-clip-text text-transparent">analyze your podcast?</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose your preferred method below and experience the power of AI-driven podcast analysis.
          </p>
        </div>

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

              <div className="space-y-4">
                <div className="relative">
                  <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    placeholder="https://youtube.com/watch?v=..."
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    className="pl-12 h-14 bg-background/50 border-border/30 focus:border-primary/50"
                  />
                </div>
                <Button 
                  className="w-full h-14 bg-gradient-primary hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)] transition-all duration-300"
                  disabled={!youtubeUrl.trim()}
                >
                  Analyze Podcast
                  <ArrowRight className="w-5 h-5 ml-2" />
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

              <div
                className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
                  isDragging
                    ? "border-secondary bg-secondary/10"
                    : "border-border/30 hover:border-secondary/50"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <File className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <div className="space-y-2">
                  <p className="text-lg font-medium">Drop your audio file here</p>
                  <p className="text-muted-foreground">or click to browse</p>
                  <p className="text-sm text-muted-foreground">
                    Max file size: 500MB • Supports MP3, WAV, M4A
                  </p>
                </div>
                <Button 
                  variant="outline" 
                  className="mt-4 border-secondary/30 hover:border-secondary hover:bg-secondary/10"
                >
                  Choose File
                </Button>
              </div>
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
                <Button 
                  className="bg-gradient-to-r from-accent to-accent/80 hover:shadow-[0_0_30px_hsl(var(--accent)/0.5)] transition-all duration-300"
                >
                  Start Recording
                  <Mic className="w-5 h-5 ml-2" />
                </Button>
              </div>
            </div>
          )}
        </GlassCard>
      </div>
    </section>
  )
}