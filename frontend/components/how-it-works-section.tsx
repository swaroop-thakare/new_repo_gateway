import { Upload, Cpu, CheckCircle } from "lucide-react"

const steps = [
  {
    icon: Upload,
    title: "Connect Your Data",
    subtitle: "Upload & Configure",
    description:
      "Securely connect your ERP or upload a simple CSV file with your payment instructions. Set your approval and compliance policies.",
  },
  {
    icon: Cpu,
    title: "Automate and Decide",
    subtitle: "Arealis Orchestrates",
    description:
      "Our agents instantly get to work: screening, routing, and preparing every payment for approval. You monitor the entire process from a single dashboard.",
  },
  {
    icon: CheckCircle,
    title: "Approve with Confidence",
    subtitle: "Approve & Reconcile",
    description:
      "Give the final approval. Your own bank moves the funds. Receive a fully reconciled report and a signed, audit-proof evidence pack moments later.",
  },
]

export function HowItWorksSection() {
  return (
    <section className="py-20 md:py-32 relative overflow-hidden">
      <div className="absolute inset-0 bg-transparent" />
      <div className="container px-4 md:px-6 relative">
        <div className="relative rounded-3xl bg-gradient-to-br from-white/70 to-white/30 dark:from-gray-900/50 dark:to-gray-900/20 backdrop-blur-xl border border-white/40 dark:border-white/10 p-8 md:p-12 lg:p-16 shadow-2xl overflow-hidden">
          <div className="relative">
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-1.5 rounded-full bg-white/40 text-foreground/80 text-sm font-semibold mb-4">
                Simple Process
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4">How It Works</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Three simple steps to transform your payout operations
              </p>
            </div>

            <div className="grid gap-12 md:grid-cols-3">
              {steps.map((step, index) => {
                const Icon = step.icon
                return (
                  <div key={index} className="relative">
                    <div className="flex flex-col items-center text-center space-y-4 group">
                      <div className="relative bg-white/60 dark:bg-gray-900/50 backdrop-blur-sm rounded-2xl p-6 border border-white/30 dark:border-white/10 shadow-lg group-hover:shadow-xl transition-all group-hover:-translate-y-2 w-full">
                        <div className="relative mx-auto w-fit mb-4">
                          <div className="h-20 w-20 rounded-full bg-primary flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <Icon className="h-10 w-10 text-primary-foreground" />
                          </div>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 mb-1">{step.subtitle}</p>
                          <h3 className="text-2xl font-bold mb-3">{step.title}</h3>
                          <p className="text-muted-foreground leading-relaxed">{step.description}</p>
                        </div>
                      </div>
                    </div>
                    {index < steps.length - 1 && (
                      <div className="hidden md:block absolute top-16 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-slate-200 to-slate-300 dark:from-white/10 dark:to-white/10" />
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
