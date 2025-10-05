import { Shield, Check } from "lucide-react"

export function ComplianceSection() {
  return (
    <section className="py-20 md:py-32 bg-muted/30">
      <div className="container px-4 md:px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          <div className="space-y-8">
            <div className="space-y-4">
              <p className="text-sm font-semibold text-primary uppercase tracking-wide">Maintain compliance</p>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-balance">
                Compliance made easy
              </h2>
              <p className="text-lg text-muted-foreground text-pretty">
                Stay on top of changing payroll laws and tax compliance with Arealis Magnus products your IP, automates
                tax updates, and helps you stay compliant everywhere you hire.
              </p>
            </div>

            <div className="rounded-lg border bg-primary/5 p-6 space-y-4">
              <div className="flex items-start gap-3">
                <Shield className="h-6 w-6 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold mb-2">Arealis Watchtower</h3>
                  <p className="text-sm text-muted-foreground">
                    We keep ourselves up to date on new payroll laws. We keep you informed automatically about changes
                    that affect your business, including tax rates and compliance requirements.
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-start gap-3">
                <Check className="h-6 w-6 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold mb-2">Protect your IP with Arealis IP Guard</h3>
                  <p className="text-sm text-muted-foreground">
                    Safeguard your intellectual property with built-in protections and compliance tools.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-lg border bg-card p-6 shadow-lg">
              <div className="mb-6">
                <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary mb-4">
                  <Check className="h-4 w-4" />
                  Spring Service
                </div>
                <h3 className="text-xl font-bold mb-2">Team Overview</h3>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-lg border p-3">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-accent" />
                    <div>
                      <div className="font-medium text-sm">Marc Brown</div>
                      <div className="text-xs text-muted-foreground">Australia</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">Salary</div>
                    <div className="font-semibold text-sm">₹7,441.00</div>
                  </div>
                </div>

                <div className="flex items-center justify-between rounded-lg border p-3">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-accent" />
                    <div>
                      <div className="font-medium text-sm">Julia Silva</div>
                      <div className="text-xs text-muted-foreground">Portugal</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">Salary</div>
                    <div className="font-semibold text-sm">₹6,579.00</div>
                  </div>
                </div>

                <div className="flex items-center justify-between rounded-lg border p-3">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600" />
                    <div>
                      <div className="font-medium text-sm">Sarah Jones</div>
                      <div className="text-xs text-muted-foreground">UK</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">Salary</div>
                    <div className="font-semibold text-sm">₹8,234.00</div>
                  </div>
                </div>
              </div>

              <button className="mt-4 w-full rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
                View team
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
