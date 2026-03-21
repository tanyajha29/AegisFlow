"use client"

import { motion } from "framer-motion"
import { ArrowRight, Shield } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export function CTASection() {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background glows */}
      <div className="absolute top-0 left-1/4 w-[400px] h-[400px] bg-[#3B82F6]/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-[#06B6D4]/20 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glass-card rounded-3xl p-8 sm:p-12 text-center border border-[rgba(59,130,246,0.3)]"
        >
          <motion.div
            initial={{ scale: 0 }}
            whileInView={{ scale: 1 }}
            viewport={{ once: true }}
            className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#3B82F6] to-[#06B6D4] flex items-center justify-center mx-auto mb-6"
          >
            <Shield className="h-8 w-8 text-white" />
          </motion.div>

          <h2 className="text-3xl sm:text-4xl font-bold text-[#E2E8F0] mb-4">
            Secure Your Code Before Deployment
          </h2>
          <p className="text-[#94A3B8] mb-8 max-w-xl mx-auto">
            Join thousands of developers who trust DristiScan to protect their applications
            from security vulnerabilities.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/scan">
              <Button size="lg" className="btn-gradient text-white gap-2 h-12 px-8">
                Start Scanning Now
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/signup">
              <Button
                size="lg"
                variant="outline"
                className="h-12 px-8 bg-transparent border-[rgba(59,130,246,0.3)] text-[#E2E8F0] hover:bg-[rgba(59,130,246,0.1)] hover:border-[rgba(59,130,246,0.5)]"
              >
                Create Free Account
              </Button>
            </Link>
          </div>

          <div className="mt-8 pt-8 border-t border-[rgba(59,130,246,0.2)] flex flex-wrap justify-center gap-8 text-sm text-[#94A3B8]">
            <span>Free tier available</span>
            <span>No credit card required</span>
            <span>Setup in 2 minutes</span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}