"use client"

import { CyberBackground } from "@/components/cyber-background"
import { Navbar } from "@/components/landing/navbar"
import { HeroSection } from "@/components/landing/hero-section"
import { FeaturesSection } from "@/components/landing/features-section"
import { AIAgentsSection } from "@/components/landing/ai-agents-section"
import { DashboardPreview } from "@/components/landing/dashboard-preview"
import { CTASection } from "@/components/landing/cta-section"
import { Footer } from "@/components/landing/footer"

export default function LandingPage() {
  return (
    <div className="min-h-screen cyber-grid relative">
      <CyberBackground />
      <div className="relative z-10">
        <Navbar />
        <main>
          <HeroSection />
          <FeaturesSection />
          <AIAgentsSection />
          <DashboardPreview />
          <CTASection />
        </main>
        <Footer />
      </div>
    </div>
  )
}