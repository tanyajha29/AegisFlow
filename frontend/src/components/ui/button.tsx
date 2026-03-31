"use client"

import React from "react"
import clsx from "clsx"
import { motion } from "framer-motion"

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "outline" | "ghost"
  size?: "sm" | "md" | "lg"
}

const variantClasses: Record<NonNullable<ButtonProps["variant"]>, string> = {
  default: "btn-gradient text-white border-0",
  outline:
    "bg-transparent border border-[rgba(59,130,246,0.3)] text-[#E2E8F0] hover:bg-[rgba(59,130,246,0.1)] hover:border-[rgba(59,130,246,0.5)]",
  ghost: "bg-transparent text-[#E2E8F0] hover:text-white hover:bg-[rgba(59,130,246,0.1)]",
}

const sizeClasses: Record<NonNullable<ButtonProps["size"]>, string> = {
  sm: "h-9 px-4 text-sm",
  md: "h-10 px-5",
  lg: "h-12 px-8 text-base",
}

export function Button({
  children,
  className,
  variant = "default",
  size = "md",
  ...props
}: ButtonProps) {
  return (
    <motion.button
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#3B82F6] focus-visible:ring-offset-transparent",
        variant === "default" && "bg-[length:200%_200%]",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      whileHover={{
        scale: 1.02,
        boxShadow: "0 0 24px rgba(59,130,246,0.35)",
        backgroundPosition: variant === "default" ? "100% 50%" : undefined,
      }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: "spring", stiffness: 260, damping: 18 }}
      {...props}
    >
      {children}
    </motion.button>
  )
}

export default Button
