"use client"

import Link from "next/link"

export function DemoFooter() {
  return (
    <footer className="border-t border-white/5 bg-[#0a0a0a] px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <span>© 2025 xAI</span>
          <span>•</span>
          <Link 
            href="https://x.ai" 
            target="_blank" 
            rel="noopener noreferrer"
            className="hover:text-white transition-colors"
          >
            Learn More about xAI
          </Link>
        </div>
        <div className="text-xs text-gray-500">
          Arealis Gateway v2.0
        </div>
      </div>
    </footer>
  )
}
