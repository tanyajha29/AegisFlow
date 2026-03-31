"use client"

import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { motion } from "framer-motion"
import { Eye, Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const navLinks = [
    { href: "/", label: "Home", type: "route" },
    { href: "/app/scan", label: "Scan", type: "route" },
    { href: "#features", label: "Features", type: "anchor" },
    { href: "#security", label: "Security", type: "anchor" },
    { href: "/app/reports", label: "Reports", type: "route" },
  ]

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-[#0B1220]/80 backdrop-blur-xl border-b border-[rgba(59,130,246,0.2)]"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-[#3B82F6] to-[#06B6D4] flex items-center justify-center shadow-glow relative overflow-hidden">
              <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
              <Eye className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">DristiScan</span>
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) =>
              link.type === "anchor" ? (
                <a
                  key={link.href}
                  href={link.href}
                  className="text-[#94A3B8] hover:text-[#E2E8F0] transition-colors relative group"
                >
                  {link.label}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-[#3B82F6] to-[#06B6D4] group-hover:w-full transition-all duration-300" />
                </a>
              ) : (
                <Link
                  key={link.href}
                  to={link.href}
                  className="text-[#94A3B8] hover:text-[#E2E8F0] transition-colors relative group"
                >
                  {link.label}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-[#3B82F6] to-[#06B6D4] group-hover:w-full transition-all duration-300" />
                </Link>
              )
            )}
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <Link to="/login">
              <Button
                variant="ghost"
                className="text-[#E2E8F0] hover:text-white hover:bg-[rgba(59,130,246,0.1)]"
              >
                Login
              </Button>
            </Link>
            <Link to="/login">
              <Button className="btn-gradient text-white border-0">
                Sign Up
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-[#E2E8F0]"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden py-4 border-t border-[rgba(59,130,246,0.2)]"
          >
            <div className="flex flex-col gap-4">
              {navLinks.map((link) =>
                link.type === "anchor" ? (
                  <a
                    key={link.href}
                    href={link.href}
                    className="text-[#94A3B8] hover:text-[#E2E8F0] transition-colors px-4 py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {link.label}
                  </a>
                ) : (
                  <Link
                    key={link.href}
                    to={link.href}
                    className="text-[#94A3B8] hover:text-[#E2E8F0] transition-colors px-4 py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {link.label}
                  </Link>
                )
              )}
              <div className="flex flex-col gap-2 px-4 pt-4 border-t border-[rgba(59,130,246,0.2)]">
                <Link to="/login">
                  <Button variant="ghost" className="w-full text-[#E2E8F0]">
                    Login
                  </Button>
                </Link>
                <Link to="/login">
                  <Button className="w-full btn-gradient text-white border-0">
                    Sign Up
                  </Button>
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  )
}
