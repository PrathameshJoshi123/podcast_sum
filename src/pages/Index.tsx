import { Header } from "../components/header"
import { HeroSection } from "../components/hero-section"
import { FeaturesSection } from "../components/features-section"
import { UploadSection } from "../components/upload-section"
import { Footer } from "../components/footer"

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <UploadSection />
      </main>
      <Footer />
    </div>
  );
};

export default Index;