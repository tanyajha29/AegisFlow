"use client"

import { motion } from "framer-motion"
import { Bot, Shield, Key, Package, FileSearch } from "lucide-react"
import { useEffect, useState } from "react"

const agents = [
  {
    icon: Shield,
    name: "Injection Agent",
    status: "active",
    description: "Detects SQL, XSS, and command injection vulnerabilities",
  },
  {
    icon: Key,
    name: "Secrets Agent",
    status: "active",
    description: "Finds hardcoded credentials and API keys",
  },
  {
    icon: Bot,
    name: "Auth Agent",
    status: "active",
    description: "Analyzes authentication and authorization flaws",
  },
  {
    icon: Package,
    name: "Dependency Agent",
    status: "active",
    description: "Scans for vulnerable dependencies and packages",
  },
  {
    icon: FileSearch,
    name: "Report Agent",
    status: "active",
    description: "Generates comprehensive security reports",
  },
]

const terminalLines = [
  "$ dristiscan analyze --target ./src",
  "[Agent] Initializing security scan...",
  "[Injection] Scanning login.py for SQL injection...",
  "[Secrets] Analyzing config files for exposed credentials...",
  "[Auth] Checking authentication middleware...",
  "[Dependency] Reviewing package.json dependencies...",
  "[Report] Generating remediation suggestions...",
  "[Agent] Scan complete. 3 vulnerabilities found.",
]

export function AIAgentsSection() {
  const [visibleLines, setVisibleLines] = useState<number>(0)

  useEffect(() => {
    if (visibleLines < terminalLines.length) {
      const timer = setTimeout(() => {
        setVisibleLines((prev) => prev + 1)
      }, 800)
      return () => clearTimeout(timer)
    } else {
      const resetTimer = setTimeout(() => {
        setVisibleLines(0)
      }, 3000)
      return () => clearTimeout(resetTimer)
    }
  }, [visibleLines])

  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#6366F1]/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-[#E2E8F0] mb-4">
            AI Security Agents in Action
          </h2>
          <p className="text-[#94A3B8] max-w-2xl mx-auto">
            Our specialized AI agents work together to provide comprehensive security analysis
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8 items-center">
          {/* Agent Cards */}
          <div className="space-y-4">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="glass-card p-4 rounded-xl flex items-center gap-4 group hover:border-[rgba(99,102,241,0.5)] transition-all"
              >
                <div className="w-12 h-12 rounded-lg bg-[rgba(99,102,241,0.2)] flex items-center justify-center shrink-0">
                  <agent.icon className="h-6 w-6 text-[#6366F1]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-[#E2E8F0]">{agent.name}</h3>
                    <span className="w-2 h-2 rounded-full bg-[#22C55E] status-active" />
                  </div>
                  <p className="text-sm text-[#94A3B8] truncate">{agent.description}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Terminal */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="glass-card rounded-2xl overflow-hidden border border-[rgba(99,102,241,0.3)]"
          >
            <div className="flex items-center gap-2 px-4 py-3 border-b border-[rgba(99,102,241,0.2)] bg-[rgba(15,23,42,0.8)]">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
                <div className="w-3 h-3 rounded-full bg-[#EAB308]" />
                <div className="w-3 h-3 rounded-full bg-[#22C55E]" />
              </div>
              <span className="text-sm text-[#94A3B8] ml-2">Terminal</span>
            </div>
            <div className="p-4 font-mono text-sm h-[280px] overflow-hidden">
              {terminalLines.slice(0, visibleLines).map((line, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`py-1 ${
                    line.startsWith("$")
                      ? "text-[#22C55E]"
                      : line.includes("[Agent]")
                      ? "text-[#3B82F6]"
                      : line.includes("[Injection]")
                      ? "text-[#EF4444]"
                      : line.includes("[Secrets]")
                      ? "text-[#F97316]"
                      : line.includes("[Auth]")
                      ? "text-[#06B6D4]"
                      : line.includes("[Dependency]")
                      ? "text-[#EAB308]"
                      : line.includes("[Report]")
                      ? "text-[#6366F1]"
                      : "text-[#94A3B8]"
                  }`}
                >
                  {line}
                </motion.div>
              ))}
              {visibleLines < terminalLines.length && (
                <motion.span
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                  className="inline-block w-2 h-4 bg-[#E2E8F0]"
                />
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}