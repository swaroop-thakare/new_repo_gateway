import { Award, Target, Zap } from "lucide-react"
import { FadeIn } from "@/components/fade-in"

export function AboutSection() {
  return (
    <section className="py-20 md:py-32 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-[#0f172a]/20 dark:to-[#111827]/20" />

      <div className="container px-4 md:px-6 relative">
        {/* Glass card wrapper */}
        <div className="relative rounded-3xl bg-white/60 dark:bg-[#0f0f0f]/60 backdrop-blur-xl border border-white/15 dark:border-white/10 p-8 md:p-12 lg:p-16 shadow-2xl overflow-hidden">
          {/* Decorative gradient orbs */}
          {/* removed gradient orbs */}

          <div className="relative space-y-12">
            <FadeIn className="text-center max-w-3xl mx-auto space-y-4">
              <div className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-2">
                About Arealis Magna
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-balance">
                Redefining Financial Infrastructure
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Arealis is a deep-tech company redefining financial infrastructure. After securing 1st place at Google's
                Global Agentic AI Hackathon (out of 53,000+ teams), we pivoted our technology into finance, solving one
                of the industry's toughest challenges: secure, explainable, and automated bulk transactions.
              </p>
            </FadeIn>

            <div className="grid md:grid-cols-3 gap-6">
              <FadeIn
                className="group relative rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 backdrop-blur-sm border
              bg-gradient-to-br from-blue-50/80 via-cyan-50/60 to-blue-50/80
              dark:from-blue-950/30 dark:via-cyan-950/20 dark:to-blue-950/30
              border-blue-200/50 dark:border-blue-800/30"
              >
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[#3a4a65] to-[#1a1f36] flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform">
                  <Award className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">Award-Winning Tech</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  1st place at Google's Global Agentic AI Hackathon among 53,000+ teams worldwide
                </p>
              </FadeIn>

              <FadeIn
                className="group relative rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 backdrop-blur-sm border
              bg-gradient-to-br from-blue-50/80 via-cyan-50/60 to-blue-50/80
              dark:from-blue-950/30 dark:via-cyan-950/20 dark:to-blue-950/30
              border-blue-200/50 dark:border-blue-800/30"
              >
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[#3a4a65] to-[#1a1f36] flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform">
                  <Target className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">Our Mission</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Make payments fast, compliant, and transparent for enterprises without interfering with core banking
                </p>
              </FadeIn>

              <FadeIn
                className="group relative rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 backdrop-blur-sm border
              bg-gradient-to-br from-blue-50/80 via-cyan-50/60 to-blue-50/80
              dark:from-blue-950/30 dark:via-cyan-950/20 dark:to-blue-950/30
              border-blue-200/50 dark:border-blue-800/30"
              >
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[#3a4a65] to-[#1a1f36] flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">Our Vision</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Finance should flow like data: secure, intelligent, and seamless across all operations
                </p>
              </FadeIn>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
