import { ArrowLeftRight, Building2, Shield, FileCheck } from "lucide-react"

const features = [
  {
    icon: Shield,
    title: "Smart Compliance (ACC)",
    description:
      "Eliminate manual errors. Our engine automatically screens every transaction against your policies, KYC requirements, and AML watchlists before it's sent.",
  },
  {
    icon: ArrowLeftRight,
    title: "Intelligent Routing (PDR)",
    description:
      "Reduce failed payments and fees. Our system automatically selects the fastest, cheapest, and most reliable payment rail (IMPS, NEFT, RTGS) for every transaction.",
  },
  {
    icon: Building2,
    title: "Automated Reconciliation (ARL)",
    description:
      "Close your books in minutes, not days. Instantly match thousands of payouts to your bank statements and generate journals for your ERP. Eliminate spreadsheet hell.",
  },
  {
    icon: FileCheck,
    title: "Audit-Ready Reporting (CRRAK)",
    description:
      "Generate comprehensive, regulator-ready audit packs with a single click. Every decision is tracked, time-stamped, and linked to its evidence in a tamper-proof ledger.",
  },
]

export function CoreFeaturesSection() {
  return (
    <section id="features" className="py-24 md:py-32 bg-gradient-to-b from-background to-muted/20">
      <div className="container px-4 md:px-6">
        <div className="relative rounded-3xl bg-gradient-to-br from-blue-50/80 via-cyan-50/60 to-blue-50/80 dark:from-blue-950/30 dark:via-cyan-950/20 dark:to-blue-950/30 backdrop-blur-sm border border-blue-200/50 dark:border-blue-800/30 p-8 md:p-12 lg:p-16 shadow-xl">
          {/* Decorative gradient orbs */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl -z-10" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-gradient-to-tr from-cyan-400/20 to-blue-400/20 rounded-full blur-3xl -z-10" />

          <div className="mb-20 grid gap-8 lg:grid-cols-2 lg:gap-16 items-start">
            <div className="space-y-4">
              <div className="text-sm font-semibold tracking-wide text-primary uppercase">Future Payment</div>
              <h2 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl text-balance leading-tight">
                A Fully-Managed Payout Engine
              </h2>
            </div>
            <div className="lg:pt-12">
              <p className="text-lg text-muted-foreground text-pretty leading-relaxed">
                Enterprise-grade automation for every step of your payout workflow. Design a financial operating system
                that works for your business and streamlined cash flow management.
              </p>
            </div>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div
                  key={index}
                  className="group relative bg-white/90 dark:bg-card/90 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-border/50"
                >
                  {/* Gradient overlay on hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                  <div className="relative space-y-6">
                    {/* Icon with gradient background */}
                    <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <Icon className="h-7 w-7 text-primary stroke-[2]" />
                    </div>

                    <div className="space-y-3">
                      <h3 className="text-xl font-semibold tracking-tight text-foreground group-hover:text-primary transition-colors duration-300">
                        {feature.title}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-sm">{feature.description}</p>
                    </div>
                  </div>

                  {/* Decorative corner accent */}
                  <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-primary/10 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
