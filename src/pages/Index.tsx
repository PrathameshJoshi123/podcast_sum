import { Header } from "../components/header"
import { HeroSection } from "../components/hero-section"
import { FeaturesSection } from "../components/features-section"
import { UploadSection } from "../components/upload-section"
import { Footer } from "../components/footer"
import PodcastChatbot from "../components/PodcastChatbot"
import { useState } from "react"
const Index = () => {
  const [podcastContext, setPodcastContext] = useState({
    title: "Sample Podcast Episode",
    summary: "This is a sample podcast summary...",
    transcript: "Full transcript would go here...",
    keyPoints: ["Point 1", "Point 2", "Point 3"],
    participants: ["Host", "Guest"]
  });
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <UploadSection />
        <PodcastChatbot podcastContext={podcastContext} />
      </main>
      <Footer />
    </div>
  );
};

export default Index;