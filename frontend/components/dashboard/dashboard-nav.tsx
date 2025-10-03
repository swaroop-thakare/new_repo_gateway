"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Bell, Search, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

export function DashboardNav() {
  const pathname = usePathname()

  const navItems = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/dashboard/transactions", label: "Transactions" },
    { href: "/dashboard/prompt-layer", label: "Prompt Layer" },
  ]

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded bg-primary text-primary-foreground font-bold text-sm">
              AG
            </div>
            <span className="font-bold text-lg text-white">Arealis Gateway</span>
          </Link>

          {/* Center Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "px-4 py-2 text-sm font-medium rounded-md transition-colors",
                  pathname === item.href
                    ? "bg-primary text-primary-foreground"
                    : "text-slate-300 hover:text-white hover:bg-slate-800",
                )}
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-3">
            <div className="relative hidden lg:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search transactions, beneficiaries..."
                className="pl-9 w-64 bg-slate-900 border-slate-800 text-white placeholder:text-slate-500"
              />
            </div>
            <Button variant="ghost" size="icon" className="text-slate-300 hover:text-white">
              <Bell className="h-5 w-5" />
            </Button>
            <Button variant="ghost" className="text-slate-300 hover:text-white gap-2">
              <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                A
              </div>
              <span className="hidden md:inline">Admin</span>
              <ChevronDown className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}
