import { Award } from "lucide-react"

export function AwardsSection() {
  return (
    <section className="py-20 md:py-32 bg-muted/30">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-8 text-balance">
            The #1 global HR platform as voted by you
          </h2>

          <div className="flex flex-wrap items-center justify-center gap-8">
            {[2020, 2021, 2022, 2023, 2024, 2025].map((year) => (
              <div key={year} className="flex flex-col items-center">
                <div className="relative mb-3">
                  <div className="h-24 w-24 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
                    <Award className="h-12 w-12 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 bg-primary text-primary-foreground text-xs font-bold px-2 py-1 rounded">
                    {year}
                  </div>
                </div>
                <div className="text-sm font-semibold">Grid Leader</div>
                <div className="text-xs text-muted-foreground">Winter {year}</div>
              </div>
            ))}
          </div>

          <div className="mt-8 flex items-center justify-center gap-8">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Trustpilot</span>
              <div className="flex gap-1">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400">
                    ★
                  </span>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">G2</span>
              <div className="flex gap-1">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400">
                    ★
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
