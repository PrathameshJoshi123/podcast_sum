import { Button } from "./ui/button"
import { GlassCard } from "./ui/glass-card"
import { Play, Sparkles, Zap } from "lucide-react"
import heroImage from "../assets/hero-podcast.jpg"

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-background/95 via-background/80 to-background/95" />
      </div>
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-primary/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-secondary/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 w-24 h-24 bg-accent/10 rounded-full blur-2xl animate-float" style={{ animationDelay: '2s' }} />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full text-sm text-primary font-medium animate-fade-in">
            <Sparkles className="w-4 h-4" />
            AI-Powered Podcast Intelligence
          </div>

          {/* Main Heading */}
          <div className="space-y-4 animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold">
              <span className="bg-gradient-primary bg-clip-text text-transparent">
                Transform Podcasts
              </span>
              <br />
              <span className="text-foreground">Into Insights</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Extract summaries, transcripts, and key insights from any podcast in seconds. 
              Upload audio files or paste YouTube links to unlock the power of AI-driven content analysis.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in" style={{ animationDelay: '0.4s' }}>
            <Button size="lg" className="px-8 py-6 text-lg bg-gradient-primary hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)] transition-all duration-300">
              <Play className="w-5 h-5 mr-2" />
              Try Free Demo
            </Button>
            <Button variant="outline" size="lg" className="px-8 py-6 text-lg border-border/30 hover:border-primary/50">
              <Zap className="w-5 h-5 mr-2" />
              View Features
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 animate-fade-in" style={{ animationDelay: '0.6s' }}>
            <GlassCard variant="minimal" className="text-center">
              <div className="text-3xl font-bold text-primary">10K+</div>
              <div className="text-muted-foreground">Podcasts Analyzed</div>
            </GlassCard>
            <GlassCard variant="minimal" className="text-center">
              <div className="text-3xl font-bold text-secondary">95%</div>
              <div className="text-muted-foreground">Accuracy Rate</div>
            </GlassCard>
            <GlassCard variant="minimal" className="text-center">
              <div className="text-3xl font-bold text-accent">2min</div>
              <div className="text-muted-foreground">Average Process Time</div>
            </GlassCard>
          </div>
        </div>
      </div>

      {/* Audio Wave Animation */}
      <div className="absolute bottom-0 left-0 right-0 h-32 flex items-end justify-center gap-1 opacity-20">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="w-1 bg-gradient-primary rounded-t animate-wave"
            style={{
              height: `${Math.random() * 100 + 20}px`,
              animationDelay: `${i * 0.1}s`,
            }}
          />
        ))}
      </div>
    </section>
  )
}