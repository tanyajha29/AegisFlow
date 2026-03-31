"use client"

import { motion } from "framer-motion"
import {
  Code2,
  Github,
  KeyRound,
  Brain,
  BarChart3,
  FileText,
  History,
  Shield,
} from "lucide-react"

const features = [
  {
    icon: Code2,
    title: "Multi-Language Scanning",
    description: "Support for Python, JavaScript, TypeScript, Java, Go, and more.",
  },
  {
    icon: Github,
    title: "GitHub Integration",
    description: "Scan repositories directly from GitHub with one-click integration.",
  },
  {
    icon: KeyRound,
    title: "Secret Detection",
    description: "Find hardcoded API keys, passwords, and sensitive credentials.",
  },
  {
    icon: Brain,
    title: "AI-Based Analysis",
    description: "Advanced AI agents analyze code patterns and detect vulnerabilities.",
  },
  {
    icon: BarChart3,
    title: "Risk Scoring",
    description: "Get comprehensive security scores and risk assessments.",
  },
  {
    icon: FileText,
    title: "PDF Reports",
    description: "Generate professional security audit reports for stakeholders.",
  },
  {
    icon: History,
    title: "Scan History",
    description: "Track all your scans and monitor security trends over time.",
  },
  {
    icon: Shield,
    title: "Real-time Protection",
    description: "Continuous monitoring and instant vulnerability alerts.",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-[#E2E8F0] mb-4">
            Powerful Security Features
          </h2>
          <p className="text-[#94A3B8] max-w-2xl mx-auto">
            Everything you need to secure your codebase and protect your applications
            from vulnerabilities.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="glass-card p-6 rounded-xl cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[#3B82F6]/20 to-[#06B6D4]/20 flex items-center justify-center mb-4 group-hover:from-[#3B82F6]/30 group-hover:to-[#06B6D4]/30 transition-all">
                <feature.icon className="h-6 w-6 text-[#3B82F6] group-hover:text-[#06B6D4] transition-colors" />
              </div>
              <h3 className="text-lg font-semibold text-[#E2E8F0] mb-2">{feature.title}</h3>
              <p className="text-sm text-[#94A3B8]">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}