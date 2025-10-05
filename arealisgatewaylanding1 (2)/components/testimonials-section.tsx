import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export function TestimonialsSection() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4 text-balance">
            A word from our customers
          </h2>
        </div>

        <div className="grid gap-8 md:grid-cols-2">
          <Card className="bg-gradient-to-br from-[#2d1b4e] to-[#4a2c6e] text-white border-0">
            <CardContent className="p-8 space-y-6">
              <p className="text-lg leading-relaxed">
                "With Arealis, we've been able to keep on top of compliance, standardization and payroll. Arealis has
                effectively taken a labor and money issue for us."
              </p>
              <div className="flex items-center gap-4 pt-4 border-t border-white/20">
                <Avatar>
                  <AvatarFallback className="bg-white/20 text-white">JD</AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-semibold">John Doe</div>
                  <div className="text-sm text-white/70">CFO, Global Tech Inc</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-8 space-y-6">
              <p className="text-lg leading-relaxed text-muted-foreground">
                "They were flexible as a vendor and provided great support they provide us with payroll, tax compliance,
                and HR capabilities that have been game-changers for our business."
              </p>
              <div className="flex items-center gap-4 pt-4 border-t">
                <Avatar>
                  <AvatarFallback className="bg-primary/10 text-primary">SD</AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-semibold">Sarah Davidson</div>
                  <div className="text-sm text-muted-foreground">Senior Global Mobility and Remote Hiring Manager</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
