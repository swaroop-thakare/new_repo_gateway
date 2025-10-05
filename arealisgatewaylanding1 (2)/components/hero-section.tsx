import { Button } from "@/components/ui/button"
import Link from "next/link"
import { FadeIn } from "@/components/fade-in"
import Image from "next/image"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-[#07122a] via-[#0a1f44] to-[#0b2b66] text-white">
      <div className="container px-4 py-20 md:py-32 md:px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          <FadeIn className="space-y-8">
            <div className="inline-block rounded-full bg-white/20 px-4 py-1.5 text-sm backdrop-blur-sm text-white font-semibold">
              {"The Smartest Way to Move Money at Scale"}
            </div>

            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl text-balance text-white">
              {"Arealis Magna is a non-custodial financial intelligence layer"}
            </h1>

            <p className="text-lg text-white/90 max-w-xl text-pretty">
              {
                "It sits on top of your banking rails (NEFT, RTGS, IMPS, UPI, NACH). We don't hold your funds — instead, we power faster disbursements, autonomous compliance, and real-time reconciliation. Think of it as the brains for your financial flows."
              }
            </p>

            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="bg-white text-primary hover:bg-white/90 font-semibold shadow-xl" asChild>
                <Link href="/book-demo">Request a Demo</Link>
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-white text-white hover:bg-white/10 bg-transparent font-semibold"
                asChild
              >
                <Link href="/contact">{"Talk to Sales"}</Link>
              </Button>
            </div>
          </FadeIn>

          <FadeIn className="relative">
            <div className="rounded-2xl overflow-hidden shadow-2xl border border-white/20">
              <Image
                src="/placeholder.svg?height=600&width=800"
                alt="Professional using laptop with financial dashboard displaying payment flows and analytics"
                width={800}
                height={600}
                className="w-full h-auto"
                query="professional person using laptop with modern financial dashboard showing payment analytics and real-time data flows on screen, dark blue interface"
              />
            </div>
          </FadeIn>
        </div>
      </div>
    </section>
  )
}
