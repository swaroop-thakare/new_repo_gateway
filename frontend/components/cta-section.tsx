import { Button } from "@/components/ui/button"
import Link from "next/link"

export function CTASection() {
  return (
    <section className="py-20 md:py-32 bg-gradient-to-br from-[#2d1b4e] to-[#4a2c6e] bg-secondary">
      <div className="container px-4 md:px-6">
        <div className="text-center space-y-8">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-white text-balance">
            Ready to take control of your global payroll with Arealis Magnus?
          </h2>
          <Button size="lg" className="bg-white text-primary hover:bg-white/90" asChild>
            <Link href="/book-demo">Book demo</Link>
          </Button>
        </div>
      </div>
    </section>
  )
}
