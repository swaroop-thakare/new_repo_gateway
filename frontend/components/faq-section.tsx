import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

export function FAQSection() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6 max-w-4xl">
        <div className="mb-12">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4 text-balance">
            Frequently Asked Questions
          </h2>
        </div>

        <div className="rounded-lg bg-gradient-to-br from-[#2d1b4e] to-[#4a2c6e] p-6 mb-8 text-white">
          <h3 className="font-bold mb-2">How long does the global payroll implementation process take?</h3>
          <p className="text-sm text-white/90">
            Depending on your circumstances, you can be running payroll for your team in weeks — compared to months with
            other global payroll providers. We've designed a phased implementation approach to get you up through the
            process one step at a time together.
          </p>
        </div>

        <Accordion type="single" collapsible className="w-full space-y-4">
          <AccordionItem value="item-1" className="border rounded-lg px-6 bg-card">
            <AccordionTrigger className="hover:no-underline text-left">
              In what countries do you offer global payroll in?
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              We offer payroll services in over 100 countries worldwide, covering all major markets and emerging
              economies. Our in-country experts ensure full compliance with local regulations.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2" className="border rounded-lg px-6 bg-card">
            <AccordionTrigger className="hover:no-underline text-left">
              How do you protect sensitive employee data?
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              We use bank-level encryption and comply with international data protection standards including GDPR, SOC
              2, and ISO 27001. All data is stored securely with regular security audits.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3" className="border rounded-lg px-6 bg-card">
            <AccordionTrigger className="hover:no-underline text-left">
              Can I manage payments to employees, authorities, and providers with Arealis Payroll?
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              Yes, our platform handles all payment types including employee salaries, tax authorities, benefits
              providers, and vendor payments through a single unified system.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-4" className="border rounded-lg px-6 bg-card">
            <AccordionTrigger className="hover:no-underline text-left">
              How can I pay an employee in another country if my business does not have an entity in their location?
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              Through our Employer of Record (EOR) service, we can hire and pay employees on your behalf in countries
              where you don't have a legal entity, ensuring full compliance with local laws.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </section>
  )
}
