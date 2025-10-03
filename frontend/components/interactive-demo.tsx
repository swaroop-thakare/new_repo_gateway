"use client"
import BookDemoOverview from "@/app/book-demo/page"
import { Sparkles, Play } from "lucide-react"
import { Button } from "@/components/ui/button"

export function InteractiveDemo() {
  return (
    <section className="relative py-24 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/5 via-transparent to-transparent" />

      <div className="container relative mx-auto px-4">
        <div className="mx-auto max-w-3xl text-center mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 mb-6">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Interactive Demo</span>
          </div>

          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-balance">See Arealis Gateway in action</h2>

          <p className="text-lg text-muted-foreground text-balance">
            Experience our powerful payment operations platform with real-time metrics, intelligent routing, and
            comprehensive oversight—all in one unified dashboard.
          </p>
        </div>

        <div className="mx-auto max-w-7xl">
          <div className="rounded-t-xl border border-b-0 bg-gradient-to-b from-muted/30 to-muted/10 backdrop-blur-sm shadow-lg">
            <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
              <div className="flex items-center gap-2">
                <span className="inline-flex h-3 w-3 rounded-full bg-red-500" />
                <span className="inline-flex h-3 w-3 rounded-full bg-yellow-500" />
                <span className="inline-flex h-3 w-3 rounded-full bg-green-500" />
              </div>

              <div className="flex-1 mx-8">
                <div className="flex items-center gap-2 rounded-lg bg-background/80 border border-border/50 px-4 py-2 text-sm text-muted-foreground shadow-sm">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                  <span className="truncate font-medium">app.arealisgateway.com/dashboard</span>
                </div>
              </div>

              <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-primary/10 border border-primary/20">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs text-primary font-semibold">Live Preview</span>
              </div>
            </div>
          </div>

          <div className="rounded-b-xl border bg-card shadow-2xl overflow-hidden">
            <div className="relative">
              <div
                className="overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-primary/20 scrollbar-track-transparent hover:scrollbar-thumb-primary/40"
                style={{ maxHeight: "70vh", minHeight: "600px" }}
              >
                <div className="p-8 bg-gradient-to-br from-background via-background to-muted/10">
                  <BookDemoOverview />
                </div>
              </div>

              <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-card via-card/80 to-transparent pointer-events-none flex items-end justify-center pb-4">
                <div className="flex items-center gap-2 text-xs text-muted-foreground/60">
                  <svg className="h-4 w-4 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                  <span>Scroll to explore more</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center space-y-6">
          <div className="space-y-2">
            <p className="text-base text-foreground font-medium">Ready to transform your payment operations?</p>
            <p className="text-sm text-muted-foreground">
              See how Arealis Gateway can streamline your workflows and boost efficiency
            </p>
          </div>
          <Button size="lg" className="gap-2 shadow-lg hover:shadow-xl transition-shadow">
            <Play className="h-4 w-4" />
            Book a personalized demo
          </Button>
        </div>
      </div>
    </section>
  )
}
