import { cn } from "../../lib/utils"
import { forwardRef } from "react"

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "glow" | "minimal"
}

const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "relative backdrop-blur-sm border rounded-2xl p-6 transition-all duration-300",
          {
            "bg-gradient-card border-border/20 shadow-lg hover:shadow-xl hover:border-border/30": 
              variant === "default",
            "bg-gradient-card border-primary/20 shadow-[0_0_40px_hsl(var(--primary)/0.3)] hover:shadow-[0_0_60px_hsl(var(--primary)/0.4)]": 
              variant === "glow",
            "bg-card/50 border-border/10 hover:bg-card/70": 
              variant === "minimal",
          },
          className
        )}
        {...props}
      />
    )
  }
)

GlassCard.displayName = "GlassCard"

export { GlassCard }