"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { AlertTriangle, Shield, CheckCircle } from "lucide-react"

const codeLines = [
  { code: 'const express = require("express");', vulnerable: false },
  { code: 'const app = express();', vulnerable: false },
  { code: '', vulnerable: false },
  { code: 'app.get("/user", (req, res) => {', vulnerable: false },
  { code: '  const userId = req.query.id;', vulnerable: false },
  { code: '  const query = "SELECT * FROM users WHERE id=" + userId;', vulnerable: true, type: "SQL Injection", severity: "critical" },
  { code: '  db.query(query, (err, result) => {', vulnerable: false },
  { code: '    res.json(result);', vulnerable: false },
  { code: '  });', vulnerable: false },
  { code: '});', vulnerable: false },
  { code: '', vulnerable: false },
  { code: 'const apiKey = "sk-live-abc123xyz789secret";', vulnerable: true, type: "Hardcoded Secret", severity: "high" },
]

export function LiveScanDemo() {
  const [currentLine, setCurrentLine] = useState(0)
  const [scanning, setScanning] = useState(true)
  const [findings, setFindings] = useState<typeof codeLines>([])
  const [showResults, setShowResults] = useState(false)

  useEffect(() => {
    if (scanning && currentLine < codeLines.length) {
      const timer = setTimeout(() => {
        if (codeLines[currentLine].vulnerable) {
          setFindings((prev) => [...prev, codeLines[currentLine]])
        }
        setCurrentLine((prev) => prev + 1)
      }, 300)
      return () => clearTimeout(timer)
    } else if (currentLine >= codeLines.length) {
      setScanning(false)
      setTimeout(() => setShowResults(true), 500)
      // Reset after 5 seconds
      setTimeout(() => {
        setCurrentLine(0)
        setScanning(true)
        setFindings([])
        setShowResults(false)
      }, 6000)
    }
  }, [currentLine, scanning])

  return (
    <div className="relative">
      {/* Glow effect */}
      <div className="absolute -inset-4 bg-gradient-to-r from-[#3B82F6]/20 to-[#06B6D4]/20 rounded-2xl blur-2xl" />
      
      <div className="relative glass-card rounded-2xl overflow-hidden border border-[rgba(59,130,246,0.3)]">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[rgba(59,130,246,0.2)] bg-[rgba(15,23,42,0.8)]">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#EF4444]" />
              <div className="w-3 h-3 rounded-full bg-[#EAB308]" />
              <div className="w-3 h-3 rounded-full bg-[#22C55E]" />
            </div>
            <span className="text-sm text-[#94A3B8] ml-2">server.js</span>
          </div>
          <div className="flex items-center gap-2">
            {scanning ? (
              <motion.div
                animate={{ opacity: [1, 0.5, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="flex items-center gap-2 text-[#06B6D4]"
              >
                <Shield className="h-4 w-4" />
                <span className="text-sm">Scanning...</span>
              </motion.div>
            ) : (
              <div className="flex items-center gap-2 text-[#22C55E]">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm">Complete</span>
              </div>
            )}
          </div>
        </div>

        {/* Code Area */}
        <div className="p-4 font-mono text-sm relative">
          {/* Scanning beam */}
          {scanning && (
            <motion.div
              className="absolute left-0 right-0 h-6 bg-gradient-to-r from-transparent via-[#3B82F6]/20 to-transparent pointer-events-none"
              style={{ top: `${currentLine * 24 + 8}px` }}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
          )}

          {codeLines.map((line, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0.3 }}
              animate={{
                opacity: index <= currentLine ? 1 : 0.3,
                backgroundColor: line.vulnerable && index <= currentLine
                  ? "rgba(239, 68, 68, 0.1)"
                  : "transparent",
              }}
              className={`relative flex items-start py-0.5 px-2 rounded ${
                line.vulnerable && index <= currentLine ? "border-l-2 border-[#EF4444]" : ""
              }`}
            >
              <span className="text-[#4B5563] w-8 select-none">{index + 1}</span>
              <span className={line.vulnerable ? "text-[#FCA5A5]" : "text-[#E2E8F0]"}>
                {line.code || "\u00A0"}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Results Panel */}
        <AnimatePresence>
          {showResults && findings.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="border-t border-[rgba(59,130,246,0.2)] bg-[rgba(15,23,42,0.9)] p-4"
            >
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="h-4 w-4 text-[#EF4444]" />
                <span className="text-sm font-medium text-[#E2E8F0]">
                  {findings.length} Vulnerabilities Detected
                </span>
              </div>
              <div className="space-y-2">
                {findings.map((finding, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.2 }}
                    className="flex items-center justify-between p-3 rounded-lg bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.3)]"
                  >
                    <div className="flex items-center gap-3">
                      <AlertTriangle className="h-4 w-4 text-[#EF4444]" />
                      <span className="text-sm text-[#E2E8F0]">{finding.type}</span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      finding.severity === "critical"
                        ? "bg-[#EF4444]/20 text-[#EF4444]"
                        : "bg-[#F97316]/20 text-[#F97316]"
                    }`}>
                      {finding.severity?.toUpperCase()}
                    </span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}