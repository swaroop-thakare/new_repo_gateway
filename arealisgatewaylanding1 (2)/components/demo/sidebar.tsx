"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Plus,
  CheckSquare,
  Radio,
  Search,
  BookOpen,
  FileText,
  Activity,
  Settings,
  Plug,
  Home,
  Banknote,
  Wallet,
  Landmark,
  ShieldCheck,
  MessageSquare,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navigationItems = [
  { href: "/book-demo", label: "Overview", icon: LayoutDashboard },
  { href: "/book-demo/create", label: "Create", icon: Plus },
  { href: "/book-demo/approvals", label: "Approvals", icon: CheckSquare },
  { href: "/book-demo/live-queue", label: "Live Queue", icon: Radio },
  { href: "/book-demo/investigations", label: "Investigations", icon: Search },
  { href: "/book-demo/ledger", label: "Ledger & Recon", icon: BookOpen },
  { href: "/book-demo/audit", label: "Audit & Filings", icon: FileText },
  { href: "/book-demo/rail-health", label: "Rail Health", icon: Activity },
  { href: "/book-demo/prompt-layer", label: "Prompt Layer (xAI)", icon: MessageSquare },
]

const featureItems = [
  { href: "/book-demo/vendor-payments", label: "Vendor payments", icon: Banknote },
  { href: "/book-demo/payroll", label: "Payroll", icon: Wallet },
  { href: "/book-demo/loan-disbursements", label: "Loan Disbursements", icon: Landmark },
  { href: "/book-demo/escrow", label: "Escrow Tracking", icon: ShieldCheck },
]

export function DemoSidebar() {
  const pathname = usePathname()

  return (
    <aside
      className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col bg-sidebar
                 shadow-[0_0_0_1px_hsl(var(--color-sidebar-border)/0.7),0_20px_40px_-20px_hsl(var(--color-primary)/0.25)]
                 ring-1 ring-sidebar-border/60
                 bg-gradient-to-b from-primary/[0.06] via-background/[0.02] to-background/0
                 backdrop-blur supports-[backdrop-filter]:backdrop-blur-md"
    >
      {/* Logo Section */}
      <div className="flex items-center gap-3 border-b border-sidebar-border/60 px-6 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary/80 font-bold text-primary-foreground shadow-md shadow-primary/20">
          <Home className="h-6 w-6" />
        </div>
        <span className="text-xl font-semibold tracking-tight text-foreground">Arealis</span>
      </div>

      {/* User Profile */}
      <div className="flex items-center gap-3 border-b border-sidebar-border/60 px-6 py-4">
        <img
          src="/images/users/ryan-mitchell.png"
          alt="Avatar for Ryan Mitchell"
          className="h-10 w-10 rounded-full object-cover ring-1 ring-sidebar-border/50"
        />
        <div className="flex-1 overflow-hidden">
          <div className="truncate text-sm font-semibold text-foreground">Ryan Mitchell</div>
          <div className="truncate text-xs text-foreground/60">@mitchell87</div>
        </div>
        <button className="rounded-lg border border-sidebar-border/60 p-1.5 text-foreground/70 transition-colors hover:bg-sidebar-accent/40 hover:text-foreground">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M13 5L8 10L3 5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      {/* MAIN Section Label */}
      <div className="px-6 pt-6 pb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-foreground/60">MAIN</span>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto px-4">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const active = pathname === item.href
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                  active
                    ? "bg-gradient-to-b from-primary/15 to-primary/5 text-foreground ring-1 ring-sidebar-border/60 backdrop-blur-md shadow-[0_10px_30px_-12px_hsl(var(--color-primary)/0.35)]"
                    : "text-foreground/65 hover:text-foreground hover:bg-sidebar-accent/40 hover:ring-1 hover:ring-sidebar-border/60 hover:backdrop-blur-[2px]",
                )}
              >
                <Icon
                  className={cn(
                    "h-5 w-5 transition-colors",
                    active ? "text-foreground" : "text-foreground/70 group-hover:text-foreground",
                  )}
                />
                <span className="relative z-[1]">{item.label}</span>
                <span
                  className={cn(
                    "pointer-events-none absolute inset-0 rounded-xl",
                    active ? "shadow-[inset_0_1px_0_hsl(var(--color-sidebar-border)/0.6)]" : "",
                  )}
                />
              </Link>
            )
          })}
        </div>

        {/* FEATURES Section Label */}
        <div className="mt-6">
          <div className="px-2 pb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-foreground/60">FEATURES</span>
          </div>
          <div className="space-y-1 px-2">
            {featureItems.map((item) => {
              const active = pathname === item.href
              const Icon = item.icon
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                    active
                      ? "bg-gradient-to-b from-primary/15 to-primary/5 text-foreground ring-1 ring-sidebar-border/60 backdrop-blur-md shadow-[0_10px_30px_-12px_hsl(var(--color-primary)/0.35)]"
                      : "text-foreground/65 hover:text-foreground hover:bg-sidebar-accent/40 hover:ring-1 hover:ring-sidebar-border/60 hover:backdrop-blur-[2px]",
                  )}
                >
                  <Icon
                    className={cn(
                      "h-5 w-5 transition-colors",
                      active ? "text-foreground" : "text-foreground/70 group-hover:text-foreground",
                    )}
                  />
                  <span className="relative z-[1]">{item.label}</span>
                  <span
                    className={cn(
                      "pointer-events-none absolute inset-0 rounded-xl",
                      active ? "shadow-[inset_0_1px_0_hsl(var(--color-sidebar-border)/0.6)]" : "",
                    )}
                  />
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* OTHERS Section Label */}
      <div className="px-6 pt-4 pb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-foreground/60">OTHERS</span>
      </div>

      {/* Bottom Section */}
      <div className="border-t border-sidebar-border/60 px-4 pb-4">
        <div className="space-y-1">
          {/* Settings */}
          <Link
            href="/book-demo/settings"
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 transition-all hover:bg-white/5 hover:text-white"
          >
            <Settings className="h-5 w-5" />
            <span>Settings</span>
          </Link>

          {/* Integrations */}
          <Link
            href="/book-demo/integrations"
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 transition-all hover:bg-white/5 hover:text-white"
          >
            <Plug className="h-5 w-5" />
            <span>Integrations</span>
          </Link>
        </div>
      </div>
    </aside>
  )
}
