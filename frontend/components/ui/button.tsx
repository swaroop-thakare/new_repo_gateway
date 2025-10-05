import type * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-b from-primary/95 to-primary/75 text-primary-foreground shadow-sm hover:from-primary hover:to-primary/85 active:to-primary/70 ring-1 ring-inset ring-white/10 dark:ring-black/40 border border-white/10 dark:border-black/30 [box-shadow:inset_0_1px_0_rgba(255,255,255,.15)] backdrop-blur-sm",
        destructive:
          "bg-gradient-to-b from-destructive/95 to-destructive/75 text-destructive-foreground shadow-sm hover:from-destructive hover:to-destructive/85 active:to-destructive/70 ring-1 ring-inset ring-white/10 dark:ring-black/40 border border-white/10 dark:border-black/30 [box-shadow:inset_0_1px_0_rgba(255,255,255,.12)] backdrop-blur-sm",
        outline:
          "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50",
        secondary:
          "bg-gradient-to-b from-secondary/90 to-secondary/70 text-secondary-foreground shadow-sm hover:from-secondary hover:to-secondary/80 active:to-secondary/65 ring-1 ring-inset ring-white/10 dark:ring-black/40 border border-white/10 dark:border-black/30 [box-shadow:inset_0_1px_0_rgba(255,255,255,.12)] backdrop-blur-sm",
        success:
          "bg-gradient-to-b from-success/95 to-success/75 text-success-foreground shadow-sm hover:from-success hover:to-success/85 active:to-success/70 ring-1 ring-inset ring-white/10 dark:ring-black/40 border border-white/10 dark:border-black/30 [box-shadow:inset_0_1px_0_rgba(255,255,255,.12)] backdrop-blur-sm",
        warning:
          "bg-gradient-to-b from-warning/95 to-warning/75 text-warning-foreground shadow-sm hover:from-warning hover:to-warning/85 active:to-warning/70 ring-1 ring-inset ring-white/10 dark:ring-black/40 border border-white/10 dark:border-black/30 [box-shadow:inset_0_1px_0_rgba(255,255,255,.12)] backdrop-blur-sm",
        ghost: "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return <Comp data-slot="button" className={cn(buttonVariants({ variant, size, className }))} {...props} />
}

export { Button, buttonVariants }
