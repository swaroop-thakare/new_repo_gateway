"use client"

import React from "react"

interface MagnusLogoProps {
  className?: string
  showText?: boolean
  textClassName?: string
}

export function MagnusLogo({ className = "", showText = true, textClassName = "" }: MagnusLogoProps) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      {/* Magnus Symbol */}
      <div className="flex h-9 w-9 items-center justify-center">
        <svg
          width="32"
          height="32"
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8"
        >
          {/* Top hexagon outline */}
          <path
            d="M8 12 L16 8 L24 12 L24 20 L16 24 L8 20 Z"
            stroke="#2E3192"
            strokeWidth="2"
            fill="none"
          />
          {/* Bottom hexagon outline */}
          <path
            d="M8 20 L16 16 L24 20 L24 28 L16 32 L8 28 Z"
            stroke="#2E3192"
            strokeWidth="2"
            fill="none"
          />
        </svg>
      </div>
      
      {/* Magnus Text */}
      {showText && (
        <span className={`font-heading text-xl font-semibold tracking-tight text-foreground ${textClassName}`}>
          Arealis Magnus
        </span>
      )}
    </div>
  )
}
