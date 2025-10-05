import { Shield, Award, Zap, TrendingUp } from "lucide-react"
import { FadeIn } from "@/components/fade-in"

const reasons = [
  {
    icon: Shield,
    title: "Non-custodial",
    description: "We don't touch your money — we just make it flow smarter",
    color: "from-[#3a4a65] to-[#1a1f36]",
  },
  {
    icon: Award,
    title: "Enterprise-Grade",
    description: "Built with banking security standards and compliance",
    color: "from-[#1a1f36] to-[#3a4a65]",
  },
  {
    icon: Zap,
    title: "Proven Tech",
    description: "From Hackathon wins to enterprise pilots",
    color: "from-[#2b354b] to-[#1a1f36]",
  },
  {
    icon: TrendingUp,
    title: "Future-Ready",
    description: "Agentic AI powers the backbone — scaling with you",
    color: "from-[#3a4a65] to-[#243046]",
  },
]

export function WhyChooseSection() {
  return (
    <section className="py-20 md:py-32 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-[#0f172a]/20 dark:to-[#111827]/20" />

      <div className="container px-4 md:px-6 relative">
        {/* Glass card wrapper */}
        <div className="relative rounded-3xl bg-white/60 dark:bg-[#0f0f0f]/60 backdrop-blur-xl border border-white/15 dark:border-white/10 p-8 md:p-12 lg:p-16 shadow-2xl overflow-hidden">
          {/* Decorative gradient orbs */}
          {/* previously: rose/fuchsia/purple blobs */}

          <div className="relative">
            <FadeIn className="text-center mb-16">
              <div className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
                Why Arealis
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4">Why Choose Us?</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Built for the future of financial operations
              </p>
            </FadeIn>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {reasons.map((reason, index) => {
                const Icon = reason.icon
                return (
                  <FadeIn
                    key={index}
                    className="group relative rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all hover:-translate-y-2 backdrop-blur-sm border
                    bg-gradient-to-br from-blue-50/80 via-cyan-50/60 to-blue-50/80
                    dark:from-blue-950/30 dark:via-cyan-950/20 dark:to-blue-950/30
                    border-blue-200/50 dark:border-blue-800/30"
                  >
                    <div
                      className={`h-14 w-14 rounded-xl bg-gradient-to-br ${reason.color} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform`}
                    >
                      <Icon className="h-7 w-7 text-white" />
                    </div>
                    <h3 className="text-xl font-bold mb-2">{reason.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{reason.description}</p>
                  </FadeIn>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
