import { Button } from "@/components/ui/button"
import Link from "next/link"
import { FadeIn } from "@/components/fade-in"

export function FinalCTASection() {
  return (
    <section className="py-20 md:py-32 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-[#1a1f36] via-[#243046] to-[#3a4a65]" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:24px_24px]" />

      <div className="container px-4 md:px-6 relative">
        <FadeIn className="max-w-3xl mx-auto text-center space-y-8">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-balance text-white">
            Redefine the Way Your Business Moves Money
          </h2>
          <p className="text-lg text-white/90 leading-relaxed">
            From compliance to reconciliation, Arealis Magnus automates what slows you down. Stop managing financial
            friction. Start scaling with intelligence.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button size="lg" className="bg-white text-blue-700 hover:bg-white/90 font-semibold shadow-xl" asChild>
              <Link href="/book-demo">Book a Demo</Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white/10 font-semibold bg-transparent"
              asChild
            >
              <Link href="/contact">Contact Sales</Link>
            </Button>
          </div>
        </FadeIn>
      </div>
    </section>
  )
}
