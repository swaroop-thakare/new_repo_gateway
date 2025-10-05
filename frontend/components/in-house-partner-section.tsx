import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Check } from "lucide-react"

export function InHousePartnerSection() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-start">
          <div className="relative order-2 lg:order-1">
            <div className="rounded-lg border bg-card p-6 shadow-lg">
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-4">Payroll Breakdown</h3>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-4">
                  <div className="h-12 w-12 rounded-full bg-gradient-to-br from-primary to-accent" />
                  <div className="flex-1">
                    <div className="font-semibold">₹83,452</div>
                    <div className="text-sm text-muted-foreground">Gross salary</div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div className="rounded-lg bg-green-50 p-3 border border-green-200">
                    <div className="font-semibold text-green-700">₹72,345.17</div>
                    <div className="text-xs text-green-600">Net pay</div>
                  </div>
                  <div className="rounded-lg bg-blue-50 p-3 border border-blue-200">
                    <div className="font-semibold text-blue-700">₹8,789.83</div>
                    <div className="text-xs text-blue-600">Taxes</div>
                  </div>
                  <div className="rounded-lg bg-accent/10 p-3 border border-accent/20">
                    <div className="font-semibold text-accent">₹2,317.00</div>
                    <div className="text-xs text-accent">Benefits</div>
                  </div>
                </div>

                <div className="flex gap-2 pt-4">
                  <button className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
                    Learn more
                  </button>
                  <button className="flex-1 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted">
                    Add an owner
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-8 order-1 lg:order-2">
            <div className="space-y-4">
              <p className="text-sm font-semibold text-secondary uppercase tracking-wide">Upgrade your payroll</p>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-balance">
                Your in-house payroll partner
              </h2>
              <p className="text-lg text-muted-foreground text-pretty">
                We don't outsource payroll — we own it. With in-country teams in 75+ locations, we handle compliance,
                calculations, and complexity, and confidently do payroll right.
              </p>
            </div>

            <Accordion type="single" collapsible className="w-full space-y-4">
              <AccordionItem value="item-1" className="border rounded-lg px-6 bg-card">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded bg-primary/10">
                      <Check className="h-5 w-5 text-primary" />
                    </div>
                    <span className="font-semibold text-left">Powered by just-in-time payroll management</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-4 pb-2 text-muted-foreground">
                  Move beyond outdated systems and outsourced vendors. Receive direct payroll control and processes with
                  a fully integrated, modern platform.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-2" className="border rounded-lg px-6 bg-card">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded bg-secondary/10">
                      <Check className="h-5 w-5 text-secondary" />
                    </div>
                    <span className="font-semibold text-left">
                      Built for accuracy, powered by in-house country experts
                    </span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-4 pb-2 text-muted-foreground">
                  Our in-country payroll experts ensure compliance and accuracy for every payment.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-3" className="border rounded-lg px-6 bg-card">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded bg-accent/10">
                      <Check className="h-5 w-5 text-accent" />
                    </div>
                    <span className="font-semibold text-left">Automated global payroll payments</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-4 pb-2 text-muted-foreground">
                  Process payments automatically across multiple countries and currencies.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-4" className="border rounded-lg px-6 bg-card">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded bg-primary/10">
                      <Check className="h-5 w-5 text-primary" />
                    </div>
                    <span className="font-semibold text-left">Home-grown payroll engines engineered for scale</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-4 pb-2 text-muted-foreground">
                  Scale your payroll operations seamlessly as your business grows globally.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </div>
    </section>
  )
}
