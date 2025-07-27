import { GlassCard } from "./ui/glass-card";
import { Button } from "./ui/button";
import {
  Youtube,
  Upload,
  Mic,
  Sparkles,
  Clock,
  FileText,
  MessageSquare,
  Globe,
} from "lucide-react";
import featureImage from "../assets/uploadImage.jpg";
export function FeaturesSection() {
  const features = [
    {
      icon: Youtube,
      title: "YouTube Podcast Summarization",
      description:
        "Simply paste a YouTube link and get instant AI-powered summaries, key insights, Q&A breakdowns, and full transcripts.",
      highlights: [
        "Global summary overview",
        "Representative key sentences",
        "Q&A style breakdown",
        "Multi-language transcripts",
      ],
      color: "primary",
      demo: "Try with YouTube Link",
    },
    {
      icon: Upload,
      title: "Audio File Processing",
      description:
        "Upload your own audio files (MP3, WAV) for comprehensive analysis and transcription with advanced AI processing.",
      highlights: [
        "Support for multiple formats",
        "Intelligent content extraction",
        "Automated summarization",
        "Complete transcript generation",
      ],
      color: "secondary",
      demo: "Upload Audio File",
    },
    {
      icon: Mic,
      title: "Live Audio Transcription",
      description:
        "Get accurate, real-time transcription for meetings, interviews, and live recordings without needing summaries.",
      highlights: [
        "Real-time processing",
        "High accuracy rates",
        "Preferred language support",
        "Instant text output",
      ],
      color: "accent",
      demo: "Start Transcription",
    },
  ];

  const getIconColor = (color: string) => {
    switch (color) {
      case "primary":
        return "text-primary";
      case "secondary":
        return "text-secondary";
      case "accent":
        return "text-accent";
      default:
        return "text-primary";
    }
  };

  const getGlowColor = (color: string) => {
    switch (color) {
      case "primary":
        return "shadow-[0_0_30px_hsl(var(--primary)/0.3)]";
      case "secondary":
        return "shadow-[0_0_30px_hsl(var(--secondary)/0.3)]";
      case "accent":
        return "shadow-[0_0_30px_hsl(var(--accent)/0.3)]";
      default:
        return "shadow-[0_0_30px_hsl(var(--primary)/0.3)]";
    }
  };

  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 relative overflow-hidden -mt-32 pt-56">
      {/* Background Image with Multiple Overlays */}
      <div className="absolute inset-0 z-0">
        {/* Main background image */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url(${featureImage})`,
          }}
        />

        {/* Gradient that continues the blend from previous section */}
        <div className="absolute inset-0 bg-gradient-to-b from-background via-background/70 to-background/50" />

        {/* Side gradients for depth */}
        <div className="absolute inset-0 bg-gradient-to-br from-background/40 via-transparent to-background/40" />

        {/* Subtle pattern overlay */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255,255,255,0.1) 1px, transparent 0)`,
          }}
        />

        {/* More subtle animated gradient spheres */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-radial from-accent/10 via-accent/3 to-transparent rounded-full blur-3xl animate-pulse" />
        <div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-radial from-primary/8 via-primary/2 to-transparent rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: "1s" }}
        />
        <div
          className="absolute top-1/2 right-1/3 w-64 h-64 bg-gradient-radial from-secondary/5 via-secondary/1 to-transparent rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: "2s" }}
        />
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent/10 border border-accent/20 rounded-full text-sm text-accent font-medium backdrop-blur-sm">
            <Sparkles className="w-4 h-4" />
            Powerful AI Features
          </div>
          <h2 className="text-3xl md:text-5xl font-bold">
            <span className="text-foreground drop-shadow-sm">
              Everything you need to
            </span>
            <br />
            <span className="bg-gradient-primary bg-clip-text text-transparent drop-shadow-sm">
              unlock podcast insights
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto drop-shadow-sm">
            Our AI-powered platform handles every aspect of podcast analysis,
            from transcription to intelligent summarization.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <GlassCard
              key={index}
              className={`group hover:${getGlowColor(
                feature.color
              )} transition-all duration-500 animate-fade-in backdrop-blur-md border-white/10 bg-background/30`}
              style={{ animationDelay: `${index * 0.2}s` }}
            >
              <div className="space-y-6">
                {/* Icon */}
                <div
                  className={`w-16 h-16 rounded-2xl bg-gradient-to-br from-${feature.color}/20 to-${feature.color}/10 flex items-center justify-center backdrop-blur-sm`}
                >
                  <feature.icon
                    className={`w-8 h-8 ${getIconColor(
                      feature.color
                    )} drop-shadow-sm`}
                  />
                </div>

                {/* Content */}
                <div className="space-y-4">
                  <h3 className="text-2xl font-bold text-foreground group-hover:text-primary transition-colors drop-shadow-sm">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>

                {/* Highlights */}
                <div className="space-y-3">
                  {feature.highlights.map((highlight, idx) => (
                    <div key={idx} className="flex items-center gap-3">
                      <div
                        className={`w-2 h-2 rounded-full bg-${feature.color} shadow-lg`}
                      />
                      <span className="text-sm text-muted-foreground">
                        {highlight}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Demo Button */}
                <Button
                  variant="outline"
                  className="w-full mt-6 text-white hover:text-white border-border/30 hover:border-primary/50 hover:bg-primary/5 backdrop-blur-sm bg-background/20"
                >
                  {feature.demo}
                </Button>
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Additional Benefits */}
        <div className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            {
              icon: Clock,
              label: "Lightning Fast",
              desc: "2-minute processing",
            },
            {
              icon: FileText,
              label: "Multiple Formats",
              desc: "Support all audio types",
            },
            {
              icon: MessageSquare,
              label: "Q&A Generation",
              desc: "Intelligent insights",
            },
            {
              icon: Globe,
              label: "Multi-Language",
              desc: "50+ languages supported",
            },
          ].map((benefit, index) => (
            <div
              key={index}
              className="text-center space-y-3 animate-fade-in"
              style={{ animationDelay: `${1 + index * 0.1}s` }}
            >
              <div className="w-12 h-12 rounded-xl bg-muted/30 backdrop-blur-sm flex items-center justify-center mx-auto border border-white/10">
                <benefit.icon className="w-6 h-6 text-primary drop-shadow-sm" />
              </div>
              <div>
                <div className="font-semibold text-foreground drop-shadow-sm">
                  {benefit.label}
                </div>
                <div className="text-sm text-muted-foreground">
                  {benefit.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom fade effect */}
      <div className="absolute bottom-0 left-0 right-0 h-64 bg-gradient-to-b from-transparent via-background/50 to-background z-5" />
    </section>
  );
}
