import { Button } from "@/components/ui/button"
import Link from "next/link"

export function NewHeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-background via-background to-background dark:from-primary/15 dark:via-primary/10 dark:to-background">
      <div className="absolute inset-0 hidden dark:block bg-[radial-gradient(130%_100%_at_0%_0%,theme(colors.primary/60),transparent_58%),radial-gradient(130%_120%_at_100%_100%,theme(colors.primary/45),transparent_50%)]" />
      <div className="absolute inset-0 hidden dark:block bg-primary/20 mix-blend-multiply" />

      {/* subtle blueprint/grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_40%_at_70%_30%,theme(colors.primary/18),transparent_60%)] dark:bg-[radial-gradient(60%_40%_at_70%_30%,theme(colors.primary/40),transparent_62%)]" />
      <div className="pointer-events-none absolute inset-0 hidden dark:block bg-[radial-gradient(120%_100%_at_10%_90%,theme(colors.primary/32),transparent_58%)]" />

      <div className="container relative px-4 py-20 md:py-28 md:px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          <div className="space-y-8">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl text-balance leading-[1.1]">
              The Smartest Way to <span className="text-primary">Move Money at Scale.</span>
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl text-pretty leading-relaxed">
              Arealis Magnus is a non-custodial financial intelligence layer that sits on top of banking rails (NEFT,
              RTGS, IMPS, UPI, NACH). We don&apos;t hold your funds—rather, we power faster disbursements, autonomous
              compliance, and real-time reconciliation. The control plane for your financial flows.
            </p>

            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="font-semibold shadow-lg shadow-primary/25" asChild>
                <Link href="/book-demo">Request a Demo</Link>
              </Button>
              <Button size="lg" variant="outline" className="font-semibold bg-transparent" asChild>
                <Link href="/contact">Talk to Sales</Link>
              </Button>
            </div>

            <div className="flex flex-wrap gap-3 pt-2">
              <span className="px-3 py-1.5 text-xs font-medium rounded-full border bg-background/50 supports-[backdrop-filter]:bg-background/30 dark:bg-background/20 backdrop-blur-sm">
                RBI-ready workflows
              </span>
              <span className="px-3 py-1.5 text-xs font-medium rounded-full border bg-background/50 supports-[backdrop-filter]:bg-background/30 dark:bg-background/20 backdrop-blur-sm">
                Real-time reconciliation
              </span>
              <span className="px-3 py-1.5 text-xs font-medium rounded-full border bg-background/50 supports-[backdrop-filter]:bg-background/30 dark:bg-background/20 backdrop-blur-sm">
                Bank-grade security
              </span>
            </div>
          </div>

          <div className="relative flex items-center justify-center">
            <div className="relative w-full max-w-2xl">
              <div className="relative aspect-video rounded-2xl border border-border/60 bg-background/60 supports-[backdrop-filter]:bg-background/40 dark:bg-background/18 backdrop-blur-md shadow-2xl overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/15 via-accent/10 to-primary/20 dark:from-primary/32 dark:via-accent/12 dark:to-primary/26 flex items-center justify-center">
                  <div className="absolute inset-0 bg-[url('/fintech-dashboard.png')] bg-cover bg-center opacity-35" />
                  <button className="relative z-10 h-20 w-20 rounded-full bg-primary/90 backdrop-blur-sm flex items-center justify-center shadow-xl hover:scale-110 transition-transform group-hover:bg-primary">
                    <svg
                      className="h-8 w-8 text-primary-foreground ml-1"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </button>
                </div>

                <div className="absolute top-4 left-4 px-3 py-1.5 rounded-full bg-background/60 supports-[backdrop-filter]:bg-background/40 dark:bg-background/18 backdrop-blur-sm border text-xs font-medium">
                  Watch Demo
                </div>
                <div className="absolute bottom-4 right-4 px-3 py-1.5 rounded-full bg-background/60 supports-[backdrop-filter]:bg-background/40 dark:bg-background/18 backdrop-blur-sm border text-xs font-medium">
                  2:30
                </div>
              </div>

              <div className="absolute -bottom-6 -left-6 px-4 py-3 rounded-xl bg-background/60 supports-[backdrop-filter]:bg-background/40 dark:bg-background/18 backdrop-blur-md border shadow-lg hidden lg:block">
                <div className="text-2xl font-bold text-primary">99.9%</div>
                <div className="text-xs text-muted-foreground">Uptime</div>
              </div>
              <div className="absolute -top-6 -right-6 px-4 py-3 rounded-xl bg-background/60 supports-[backdrop-filter]:bg-background/40 dark:bg-background/18 backdrop-blur-md border shadow-lg hidden lg:block">
                <div className="text-2xl font-bold text-accent">₹10B+</div>
                <div className="text-xs text-muted-foreground">Processed</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
