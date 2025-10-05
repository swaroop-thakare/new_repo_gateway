import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Check } from "lucide-react"

export function AllInOneSection() {
  return (
    <section className="py-20 md:py-32 bg-muted/30">
      <div className="container px-4 md:px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-start">
          <div className="space-y-8">
            <div className="space-y-4">
              <p className="text-sm font-semibold text-primary uppercase tracking-wide">All in one place</p>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-balance">
                Your all-in-one HR and payroll hub
              </h2>
              <p className="text-lg text-muted-foreground text-pretty">
                Manage your entire workforce between systems. Manage payroll, benefits, time off, and HR data, and have
                it all in a single, streamlined, familiar dashboard.
              </p>
            </div>

            <Accordion type="single" collapsible className="w-full space-y-4">
              <AccordionItem value="item-1" className="border rounded-lg px-6 bg-card">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded bg-primary/10">
                      <Check className="h-5 w-5 text-primary" />
                    </div>
                    <span className="font-semibold text-left">View and manage everyone in one place</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-4 pb-2 text-muted-foreground">
                  From full-time employees to Canada to contractors in Australia, get unified visibility and control
                  across every country, currency, and contract type. All in a single view.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-2" className="border rounded-lg px-6 bg-card">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded bg-secondary/10">
                      <Check className="h-5 w-5 text-secondary" />
                    </div>
                    <span className="font-semibold text-left">Simplify payroll admin at scale</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-4 pb-2 text-muted-foreground">
                  Automate payroll processing across multiple countries with built-in compliance and tax calculations.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-3" className="border rounded-lg px-6 bg-card">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded bg-accent/10">
                      <Check className="h-5 w-5 text-accent" />
                    </div>
                    <span className="font-semibold text-left">Offer localized employee benefits</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-4 pb-2 text-muted-foreground">
                  Provide competitive benefits packages tailored to each country's requirements and expectations.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>

          <div className="relative">
            <div className="rounded-lg border bg-card p-6 shadow-lg">
              <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded bg-primary text-primary-foreground font-bold text-sm">
                    AG
                  </div>
                  <span className="font-semibold">Arealis Magna</span>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Payroll</span>
                  <button className="rounded bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                    Learn more
                  </button>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-3 rounded-lg border p-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">Marc Brown</div>
                      <div className="text-xs text-muted-foreground">Australia</div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-sm">₹7,441.00</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 rounded-lg border p-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-accent" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">Julia Silva</div>
                      <div className="text-xs text-muted-foreground">Portugal</div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-sm">₹6,579.00</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 rounded-lg border p-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">Sarah Jones</div>
                      <div className="text-xs text-muted-foreground">UK</div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-sm">₹8,234.00</div>
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
