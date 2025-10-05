import { Card, CardContent } from "@/components/ui/card"
import { FadeIn } from "@/components/fade-in"

export function InsightsSection() {
  return (
    <section className="py-20 md:py-32 bg-muted/30">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4 text-balance">
            More expert payroll insights just one click away
          </h2>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <FadeIn>
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-[#1a1f36] to-[#3a4a65]" />
              <CardContent className="p-6">
                <h3 className="font-bold mb-2 text-balance">
                  Arealis Payroll's next-gen updates: Locking in on compliance, data, and more
                </h3>
                <div className="flex items-center gap-2 text-sm text-primary font-medium mt-4">
                  <span>Payroll</span>
                  <span>•</span>
                  <span>Product Updates</span>
                </div>
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn>
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-[#3a4a65] to-[#1a1f36]" />
              <CardContent className="p-6">
                <h3 className="font-bold mb-2 text-balance">
                  What is payroll? Definition, components, and how to make one
                </h3>
                <div className="flex items-center gap-2 text-sm text-primary font-medium mt-4">
                  <span>Payroll</span>
                </div>
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn>
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-blue-500 to-blue-700" />
              <CardContent className="p-6">
                <h3 className="font-bold mb-2 text-balance">
                  Payroll automation: What are the benefits, and how do you set it up?
                </h3>
                <div className="flex items-center gap-2 text-sm text-primary font-medium mt-4">
                  <span>Payroll</span>
                </div>
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn>
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-amber-600 to-amber-800" />
              <CardContent className="p-6">
                <h3 className="font-bold mb-2 text-balance">
                  How to set up direct deposit for your employees in Germany
                </h3>
                <div className="flex items-center gap-2 text-sm text-primary font-medium mt-4">
                  <span>Payroll</span>
                </div>
              </CardContent>
            </Card>
          </FadeIn>
        </div>
      </div>
    </section>
  )
}
