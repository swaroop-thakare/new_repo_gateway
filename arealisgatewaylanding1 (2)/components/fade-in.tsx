"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"

type Props = React.PropsWithChildren<{ className?: string; threshold?: number }>

export function FadeIn({ children, className = "", threshold = 0.15 }: Props) {
  const ref = useRef<HTMLDivElement | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setVisible(true)
        })
      },
      { threshold },
    )

    obs.observe(el)
    return () => {
      obs.disconnect()
    }
  }, [threshold])

  return (
    <div
      ref={ref}
      className={[
        "transition-all duration-700 ease-out will-change-transform",
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6",
        className,
      ].join(" ")}
    >
      {children}
    </div>
  )
}
