"use client"

import { motion } from "framer-motion"
import { Shield, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react"

const stats = [
  { label: "Total Scans", value: "1,234", icon: Shield, color: "#3B82F6" },
  { label: "Vulnerabilities", value: "89", icon: AlertTriangle, color: "#EF4444" },
  { label: "Fixed Issues", value: "76", icon: CheckCircle, color: "#22C55E" },
  { label: "Security Score", value: "92%", icon: TrendingUp, color: "#06B6D4" },
]

const severityData = [
  { label: "Critical", value: 12, color: "#EF4444", width: "15%" },
  { label: "High", value: 23, color: "#F97316", width: "28%" },
  { label: "Medium", value: 34, color: "#EAB308", width: "42%" },
  { label: "Low", value: 20, color: "#22C55E", width: "25%" },
]

export function DashboardPreview() {
  return (
    <section className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-[#E2E8F0] mb-4">
            Powerful Analytics Dashboard
          </h2>
          <p className="text-[#94A3B8] max-w-2xl mx-auto">
            Monitor your security posture with real-time insights and comprehensive analytics
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glass-card rounded-2xl p-6 border border-[rgba(59,130,246,0.3)]"
        >
          {/* Stats Grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-[rgba(15,23,42,0.6)] rounded-xl p-4 border border-[rgba(59,130,246,0.2)]"
              >
                <div className="flex items-center justify-between mb-3">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${stat.color}20` }}
                  >
                    <stat.icon className="h-5 w-5" style={{ color: stat.color }} />
                  </div>
                </div>
                <div className="text-2xl font-bold text-[#E2E8F0]">{stat.value}</div>
                <div className="text-sm text-[#94A3B8]">{stat.label}</div>
              </motion.div>
            ))}
          </div>

          {/* Charts Row */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Security Score Circle */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="bg-[rgba(15,23,42,0.6)] rounded-xl p-6 border border-[rgba(59,130,246,0.2)]"
            >
              <h3 className="text-lg font-semibold text-[#E2E8F0] mb-6">Security Score</h3>
              <div className="flex items-center justify-center">
                <div className="relative w-40 h-40">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="rgba(59, 130, 246, 0.2)"
                      strokeWidth="12"
                      fill="none"
                    />
                    <motion.circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="url(#scoreGradient)"
                      strokeWidth="12"
                      fill="none"
                      strokeLinecap="round"
                      initial={{ strokeDasharray: "0 440" }}
                      whileInView={{ strokeDasharray: "404 440" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1.5, ease: "easeOut" }}
                    />
                    <defs>
                      <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3B82F6" />
                        <stop offset="100%" stopColor="#06B6D4" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center flex-col">
                    <span className="text-4xl font-bold gradient-text">92</span>
                    <span className="text-sm text-[#94A3B8]">/ 100</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Severity Distribution */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="bg-[rgba(15,23,42,0.6)] rounded-xl p-6 border border-[rgba(59,130,246,0.2)]"
            >
              <h3 className="text-lg font-semibold text-[#E2E8F0] mb-6">Severity Distribution</h3>
              <div className="space-y-4">
                {severityData.map((item, index) => (
                  <div key={item.label}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-[#94A3B8]">{item.label}</span>
                      <span className="text-sm font-medium text-[#E2E8F0]">{item.value}</span>
                    </div>
                    <div className="h-2 bg-[rgba(59,130,246,0.1)] rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: item.width }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: index * 0.1 }}
                        className="h-full rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}