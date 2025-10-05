"use client"

import { Bell, ChevronDown, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { ThemeToggle } from "@/components/theme-toggle"
import { useState } from "react"

export function TopBar() {
  const [environment, setEnvironment] = useState("Sandbox")
  const [searchQuery, setSearchQuery] = useState("")

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    try {
      const response = await fetch('/api/search/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Search results:', data)
        // You could implement a modal or dropdown to show results
      } else {
        console.error('Search failed')
      }
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  return (
    <div className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/5 bg-[#0d0d0d] px-6">
      {/* Left: Tenant & Environment */}
      <div className="flex items-center gap-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2 px-3 font-medium text-white hover:bg-white/5">
              <span className="font-heading text-sm font-semibold">Arealis Magna</span>
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56 border-white/10 bg-[#1a1a1a]">
            <DropdownMenuLabel className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Switch Tenant
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-white/5" />
            <DropdownMenuItem className="font-medium text-white hover:bg-white/5">Arealis Magna</DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Arealis India</DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Arealis Europe</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2 px-3 font-medium text-white hover:bg-white/5">
              <Badge className={`${environment === "Sandbox" ? "border-blue-500/30 bg-blue-500/20 text-blue-400" : "border-green-500/30 bg-green-500/20 text-green-400"} font-semibold`}>
                {environment}
              </Badge>
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48 border-white/10 bg-[#1a1a1a]">
            <DropdownMenuLabel className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Environment
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-white/5" />
            <DropdownMenuItem 
              className="font-medium text-white hover:bg-white/5"
              onClick={() => setEnvironment("Sandbox")}
            >
              Sandbox
            </DropdownMenuItem>
            <DropdownMenuItem 
              className="text-gray-300 hover:bg-white/5"
              onClick={() => setEnvironment("Production")}
            >
              Production
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Center: Search */}
      <form onSubmit={handleSearch} className="relative w-96">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search Trace ID, UTR, Beneficiary, Amount..."
          className="border-white/10 bg-white/5 pl-9 text-sm text-white placeholder:text-gray-500 focus-visible:border-blue-500/50 focus-visible:ring-blue-500/20"
        />
      </form>

      {/* Right: Date Range, Notifications, Theme Toggle, User */}
      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="gap-2 border-white/10 bg-white/5 font-medium text-white hover:bg-white/10"
            >
              <span className="text-sm">Today</span>
              <ChevronDown className="h-3 w-3 text-gray-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48 border-white/10 bg-[#1a1a1a]">
            <DropdownMenuItem className="text-white hover:bg-white/5">Today</DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Last 24 hours</DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Last 7 days</DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Last 30 days</DropdownMenuItem>
            <DropdownMenuSeparator className="bg-white/5" />
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Custom range...</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button variant="ghost" size="icon" className="relative text-gray-300 hover:bg-white/5 hover:text-white">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-blue-500 ring-2 ring-[#0d0d0d]" />
        </Button>

        <ThemeToggle />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2 hover:bg-white/5">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-blue-500 text-xs font-semibold text-white">
                RM
              </div>
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 border-white/10 bg-[#1a1a1a]">
            <DropdownMenuLabel>
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium text-white">Ryan Mitchell</p>
                <p className="text-xs text-gray-400">ryan@arealis.com</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-white/5" />
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Profile</DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">API Keys</DropdownMenuItem>
            <DropdownMenuItem className="text-gray-300 hover:bg-white/5">Preferences</DropdownMenuItem>
            <DropdownMenuSeparator className="bg-white/5" />
            <DropdownMenuItem className="text-red-400 hover:bg-white/5">Sign out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
