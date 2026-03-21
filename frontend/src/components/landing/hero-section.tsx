"use client"

import { motion } from "framer-motion"
import { ArrowRight, Play, Code, Upload, Github } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"
import { LiveScanDemo } from "./live-scan-demo"

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden">
      {/* Radial gradient overlay */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#3B82F6]/10 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[rgba(59,130,246,0.1)] border border-[rgba(59,130,246,0.3)] mb-6"
            >
              <span className="w-2 h-2 rounded-full bg-[#22C55E] status-active" />
              <span className="text-sm text-[#94A3B8]">AI-Powered Security Scanning</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-[#E2E8F0] leading-tight mb-6"
            >
              Scan Your Code for{" "}
              <span className="relative">
                <span className="gradient-text">Security Vulnerabilities</span>
                <motion.span
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ delay: 1, duration: 0.8 }}
                  className="absolute -bottom-2 left-0 h-1 bg-gradient-to-r from-[#3B82F6] to-[#06B6D4] rounded-full"
                />
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-lg text-[#94A3B8] mb-8 leading-relaxed"
            >
              Detect secrets, insecure patterns, risky dependencies, and repository threats
              instantly with AI-powered scanning. Protect your codebase before deployment.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex flex-wrap gap-4"
            >
              <Link to="/app/scan">
                <Button size="lg" className="btn-gradient text-white gap-2 h-12 px-8">
                  Start Scanning
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Button
                size="lg"
                variant="outline"
                className="gap-2 h-12 px-8 bg-transparent border-[rgba(59,130,246,0.3)] text-[#E2E8F0] hover:bg-[rgba(59,130,246,0.1)] hover:border-[rgba(59,130,246,0.5)]"
              >
                <Play className="h-4 w-4" />
                Watch Demo
              </Button>
            </motion.div>

            {/* Quick Scan Options */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="mt-12 grid grid-cols-3 gap-4"
            >
              {[
                { icon: Code, label: "Paste Code" },
                { icon: Upload, label: "Upload File" },
                { icon: Github, label: "GitHub Repo" },
              ].map((item) => (
                <Link key={item.label} to="/app/scan">
                  <motion.div
                    whileHover={{ scale: 1.05, y: -5 }}
                    className="glass-card p-4 rounded-xl text-center cursor-pointer transition-all"
                  >
                    <item.icon className="h-6 w-6 text-[#3B82F6] mx-auto mb-2" />
                    <span className="text-sm text-[#94A3B8]">{item.label}</span>
                  </motion.div>
                </Link>
              ))}
            </motion.div>
          </motion.div>

          {/* Right Content - Live Scan Demo */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <LiveScanDemo />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
