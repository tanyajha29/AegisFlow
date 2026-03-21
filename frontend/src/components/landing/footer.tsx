"use client"

import Link from "next/link"
import { Shield, Github, Twitter, Linkedin } from "lucide-react"

const footerLinks = {
  Product: [
    { label: "Features", href: "#features" },
    { label: "Pricing", href: "/pricing" },
    { label: "Security", href: "#security" },
    { label: "Changelog", href: "/changelog" },
  ],
  Resources: [
    { label: "Documentation", href: "/docs" },
    { label: "API Reference", href: "/api" },
    { label: "Blog", href: "/blog" },
    { label: "Support", href: "/support" },
  ],
  Company: [
    { label: "About", href: "/about" },
    { label: "Careers", href: "/careers" },
    { label: "Contact", href: "/contact" },
    { label: "Partners", href: "/partners" },
  ],
  Legal: [
    { label: "Privacy", href: "/privacy" },
    { label: "Terms", href: "/terms" },
    { label: "Security", href: "/security" },
    { label: "Cookies", href: "/cookies" },
  ],
}

export function Footer() {
  return (
    <footer className="border-t border-[rgba(59,130,246,0.2)] bg-[rgba(11,18,32,0.8)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid sm:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Shield className="h-8 w-8 text-[#3B82F6]" />
              <span className="text-xl font-bold gradient-text">DristiScan</span>
            </Link>
            <p className="text-sm text-[#94A3B8] mb-4 max-w-xs">
              AI-powered code security scanning for modern development teams. Detect
              vulnerabilities before they reach production.
            </p>
            <div className="flex gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#94A3B8] hover:text-[#E2E8F0] transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#94A3B8] hover:text-[#E2E8F0] transition-colors"
              >
                <Twitter className="h-5 w-5" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#94A3B8] hover:text-[#E2E8F0] transition-colors"
              >
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="text-sm font-semibold text-[#E2E8F0] mb-4">{category}</h3>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-[#94A3B8] hover:text-[#E2E8F0] transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 pt-8 border-t border-[rgba(59,130,246,0.2)] flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-[#94A3B8]">
            &copy; {new Date().getFullYear()} DristiScan. All rights reserved.
          </p>
          <p className="text-sm text-[#94A3B8]">Built with security in mind.</p>
        </div>
      </div>
    </footer>
  )
}