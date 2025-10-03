import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"
import Link from "next/link"

const tiers = [
  {
    name: "Starter",
    price: "₹1.5L",
    period: "/month",
    description: "Ideal for SMEs testing bulk disbursements",
    features: [
      "Up to 50,000 transactions/month",
      "Autonomous Compliance Clearance (ACC)",
      "Payment Decisioning & Smart Routing (PDR)",
      "Email support",
      "Basic reporting",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Professional",
    price: "₹5L",
    period: "/month",
    description: "For mid-size enterprises with multiple vendors",
    features: [
      "Up to 5 Lakh transactions/month",
      "ACC + PDR + ARL",
      "Autonomic Reconciliation & Ledger Posting",
      "Priority support",
      "Advanced analytics",
      "API access",
    ],
    cta: "Get Started",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "pricing",
    description: "For banks, NBFCs, and large corporates",
    features: [
      "Unlimited transactions",
      "Full suite (ACC + PDR + ARL + CRRAK)",
      "Continuous Regulatory Reporting",
      "Dedicated account manager",
      "Hybrid/on-prem deployment option",
      "Custom integrations",
      "Fraud RCA module available",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
]

export function PricingSection() {
  return (
    <section className="py-20 md:py-32 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-[#0f172a]/20 dark:to-[#111827]/20" />

      <div className="container px-4 md:px-6 relative">
        <div className="relative rounded-3xl bg-white/60 dark:bg-[#0f0f0f]/60 backdrop-blur-xl border border-white/15 dark:border-white/10 p-8 md:p-12 lg:p-16 shadow-2xl overflow-hidden">
          {/* Decorative gradient orbs */}
          {/* removed amber/yellow blobs */}

          <div className="relative">
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-semibold mb-4">
                Our Structure
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4">Pricing Structure</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Flexible plans designed to scale with your business operations
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
              {tiers.map((tier, index) => (
                <div
                  key={index}
                  className="group relative bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm rounded-2xl p-8 border border-white/15 dark:border-white/10 shadow-lg hover:shadow-xl transition-all hover:-translate-y-2"
                >
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
                      <p className="text-sm text-muted-foreground">{tier.description}</p>
                    </div>

                    <Button
                      className="w-full font-semibold bg-primary text-primary-foreground hover:opacity-90"
                      size="lg"
                      asChild
                    >
                      <Link href={tier.name === "Enterprise" ? "/contact" : "/book-demo"}>
                        {tier.name === "Enterprise" ? "Contact Sales" : "Request a Demo"}
                      </Link>
                    </Button>

                    <div className="space-y-3 pt-4 border-t border-white/15 dark:border-white/10">
                      {tier.features.map((feature, featureIndex) => (
                        <div key={featureIndex} className="flex items-start gap-3">
                          <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-muted-foreground">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-12 text-center">
              <p className="text-muted-foreground">
                Talk to us for a tailored plan that fits your financial operations.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
