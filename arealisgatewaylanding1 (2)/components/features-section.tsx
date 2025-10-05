import { CreditCard, Users, Banknote } from "lucide-react"

export function FeaturesSection() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4 text-balance">
            One platform for all your payroll needs
          </h2>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          <div className="flex flex-col items-center text-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-primary/10">
              <CreditCard className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-bold">Vendor payments</h3>
            <p className="text-muted-foreground text-pretty">
              Streamline your vendor payment processes with automated workflows and real-time tracking for all your
              business transactions.
            </p>
          </div>

          <div className="flex flex-col items-center text-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-secondary/10">
              <Users className="h-8 w-8 text-secondary" />
            </div>
            <h3 className="text-xl font-bold">Payroll</h3>
            <p className="text-muted-foreground text-pretty">
              Manage global payroll with confidence. Pay your team on time, every time, with full compliance and zero
              hassle.
            </p>
          </div>

          <div className="flex flex-col items-center text-center space-y-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-accent/10">
              <Banknote className="h-8 w-8 text-accent" />
            </div>
            <h3 className="text-xl font-bold">Loan disposal</h3>
            <p className="text-muted-foreground text-pretty">
              Efficiently manage and track loan disbursements with integrated approval workflows and comprehensive audit
              trails.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
