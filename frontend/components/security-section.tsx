import { Lock, Database, Shield, CheckCircle, ArrowDown } from "lucide-react"

export function SecuritySection() {
  return (
    <section className="py-20 md:py-32 relative overflow-hidden">
      <div className="absolute inset-0 bg-transparent" />
      <div className="container px-4 md:px-6 relative">
        <div className="relative rounded-3xl bg-gradient-to-br from-white/70 to-white/30 dark:from-gray-900/50 dark:to-gray-900/20 backdrop-blur-xl border border-white/40 dark:border-white/10 p-8 md:p-12 lg:p-16 shadow-2xl overflow-hidden">
          {/* removed orbs */}
          <div className="relative grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
            <div className="space-y-6">
              <div className="inline-block px-4 py-1.5 rounded-full bg-white/40 text-foreground/80 text-sm font-semibold mb-2">
                Security First
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-balance">
                Maximum Security. <span className="text-primary">Zero Custodial Risk.</span>
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Your funds never leave your bank accounts. Arealis Gateway is a non-custodial intelligence layer that
                integrates with your existing banks. We provide the decision-making brain for your payouts; your trusted
                banking partners handle the money.
              </p>
              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3 p-4 rounded-lg bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm border border-white/30 dark:border-white/10 shadow-md">
                  <CheckCircle className="h-6 w-6 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">Non-Custodial Architecture</h4>
                    <p className="text-sm text-muted-foreground">We never touch your funds or hold your money</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 rounded-lg bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm border border-white/30 dark:border-white/10 shadow-md">
                  <CheckCircle className="h-6 w-6 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">Bank-Grade Security</h4>
                    <p className="text-sm text-muted-foreground">
                      Enterprise encryption and compliance with global standards
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-4 rounded-lg bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm border border-white/30 dark:border-white/10 shadow-md">
                  <CheckCircle className="h-6 w-6 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">Audit Trail</h4>
                    <p className="text-sm text-muted-foreground">
                      Every decision tracked and timestamped in tamper-proof ledger
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="rounded-2xl border-2 border-white/40 dark:border-white/10 bg-white/60 dark:bg-gray-900/50 backdrop-blur-sm p-8 space-y-6 shadow-xl">
                <div className="text-center pb-4 border-b">
                  <h3 className="text-xl font-bold mb-2">Non-Custodial Architecture</h3>
                  <p className="text-sm text-muted-foreground">Your money stays in your bank</p>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-5 rounded-xl bg-white/60 dark:bg-gray-900/50 border border-white/30 dark:border-white/10 shadow-sm">
                    <div className="h-14 w-14 rounded-xl bg-primary flex items-center justify-center flex-shrink-0 shadow-lg">
                      <Database className="h-7 w-7 text-primary-foreground" />
                    </div>
                    <div>
                      <p className="font-bold text-lg">Your Bank Account</p>
                      <p className="text-sm text-muted-foreground">Funds remain secure</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-center">
                    <ArrowDown className="h-8 w-8 text-primary" />
                  </div>

                  <div className="flex items-center gap-4 p-5 rounded-xl bg-white/60 dark:bg-gray-900/50 border border-white/30 dark:border-white/10 shadow-md">
                    <div className="h-14 w-14 rounded-xl bg-primary flex items-center justify-center flex-shrink-0 shadow-lg">
                      <Shield className="h-7 w-7 text-primary-foreground" />
                    </div>
                    <div>
                      <p className="font-bold text-lg">Arealis Gateway</p>
                      <p className="text-sm text-muted-foreground">Intelligence & orchestration layer</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-center">
                    <ArrowDown className="h-8 w-8 text-primary" style={{ animationDelay: "0.2s" }} />
                  </div>

                  <div className="flex items-center gap-4 p-5 rounded-xl bg-white/60 dark:bg-gray-900/50 border border-white/30 dark:border-white/10 shadow-sm">
                    <div className="h-14 w-14 rounded-xl bg-primary flex items-center justify-center flex-shrink-0 shadow-lg">
                      <Lock className="h-7 w-7 text-primary-foreground" />
                    </div>
                    <div>
                      <p className="font-bold text-lg">Secure Payments</p>
                      <p className="text-sm text-muted-foreground">Compliant & auditable</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
