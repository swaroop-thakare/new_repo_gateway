"use client"

import { User, LayoutDashboard } from "lucide-react"
import { Button } from "@/components/ui/button"
import { MagnusLogo } from "@/components/magnus-logo"

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-card/95 backdrop-blur-sm">
      <div className="container mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MagnusLogo showText={true} />
          <span className="text-sm text-muted-foreground">- Client Ingestion</span>
        </div>

        <div className="flex items-center gap-4">
          <Button variant="ghost" className="text-foreground hover:text-primary">
            <LayoutDashboard className="w-4 h-4 mr-2" />
            Dashboard
          </Button>

          <div className="flex items-center gap-3 text-sm">
            <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-muted-foreground" />
            </div>
            <span className="text-foreground font-medium">Client Finance Team</span>
          </div>
        </div>
      </div>
    </header>
  )
}
