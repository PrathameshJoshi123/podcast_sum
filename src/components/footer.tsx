import { Zap, Github, Twitter, Mail, Heart } from "lucide-react"
import { Button } from "./ui/button"

export function Footer() {
  const footerSections = [
    {
      title: "Product",
      links: [
        { label: "Features", href: "#features" },
        { label: "Pricing", href: "#pricing" },
        { label: "API", href: "#api" },
        { label: "Documentation", href: "#docs" }
      ]
    },
    {
      title: "Company",
      links: [
        { label: "About", href: "#about" },
        { label: "Blog", href: "#blog" },
        { label: "Careers", href: "#careers" },
        { label: "Contact", href: "#contact" }
      ]
    },
    {
      title: "Support",
      links: [
        { label: "Help Center", href: "#help" },
        { label: "Privacy Policy", href: "#privacy" },
        { label: "Terms of Service", href: "#terms" },
        { label: "Status", href: "#status" }
      ]
    }
  ]

  return (
    <footer className="bg-card/50 border-t border-border/20 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center">
                <Zap className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <div className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                  PodcastAI
                </div>
                <div className="text-xs text-muted-foreground -mt-1">
                  Summarizer
                </div>
              </div>
            </div>
            <p className="text-muted-foreground max-w-md">
              Transform any podcast into actionable insights with AI-powered transcription, 
              summarization, and analysis. Make content consumption efficient and intelligent.
            </p>
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" className="w-9 h-9 p-0 hover:bg-primary/10">
                <Github className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="w-9 h-9 p-0 hover:bg-primary/10">
                <Twitter className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="w-9 h-9 p-0 hover:bg-primary/10">
                <Mail className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Footer Links */}
          {footerSections.map((section) => (
            <div key={section.title} className="space-y-4">
              <h4 className="font-semibold text-foreground">{section.title}</h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-muted-foreground hover:text-foreground transition-colors duration-200"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="mt-16 pt-8 border-t border-border/20">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-muted-foreground text-sm">
              © 2024 PodcastAI Summarizer. All rights reserved.
            </div>
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              Made with
              <Heart className="w-4 h-4 text-red-500 fill-current" />
              for podcast enthusiasts
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}