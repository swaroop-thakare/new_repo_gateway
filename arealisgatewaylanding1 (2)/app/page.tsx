import { Header } from "@/components/header"
import { NewHeroSection } from "@/components/new-hero-section"
import { AboutSection } from "@/components/about-section"
import { CoreFeaturesSection } from "@/components/core-features-section"
import { HowItWorksSection } from "@/components/how-it-works-section"
import { SecuritySection } from "@/components/security-section"
import { WhyChooseSection } from "@/components/why-choose-section"
import { PricingSection } from "@/components/pricing-section"
import { FinalCTASection } from "@/components/final-cta-section"
import { NewFooter } from "@/components/new-footer"

export default function Home() {
  return (
    <main className="min-h-screen">
      <Header />
      <NewHeroSection />
      <AboutSection />
      <CoreFeaturesSection />
      <HowItWorksSection />
      <SecuritySection />
      <WhyChooseSection />
      <PricingSection />
      <FinalCTASection />
      <NewFooter />
    </main>
  )
}
