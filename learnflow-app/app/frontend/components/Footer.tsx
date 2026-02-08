"use client";

import Link from "next/link";
import { Mail, MapPin, Phone, Facebook, Instagram, Twitter } from "lucide-react";
import { useState } from "react";

export default function Footer() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      setSubscribed(true);
      setEmail("");
      setTimeout(() => setSubscribed(false), 3000);
    }
  };

  return (
    <footer className="gradient-bg-footer text-white">
      <div className="container-wide py-16 md:py-20">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12 pb-12 border-b border-white/10">
          {/* Company Info */}
          <div>
            <h3 className="text-2xl font-serif font-bold mb-4 gradient-text">
              Fatima Zehra Boutique
            </h3>
            <p className="text-gray-300 mb-6">
              Discover elegance and style with our premium collection of ladies suits, shalwar qameez, and designer wear.
            </p>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <MapPin size={20} className="text-pink-400 mt-1 flex-shrink-0" />
                <p className="text-gray-300">Lahore, Pakistan</p>
              </div>
              <div className="flex items-start gap-3">
                <Phone size={20} className="text-pink-400 mt-1 flex-shrink-0" />
                <p className="text-gray-300">+92 300 1234567</p>
              </div>
              <div className="flex items-start gap-3">
                <Mail size={20} className="text-pink-400 mt-1 flex-shrink-0" />
                <p className="text-gray-300">info@fatimazehra.com</p>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-bold mb-6">Quick Links</h4>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/products"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  Shop All Products
                </Link>
              </li>
              <li>
                <Link
                  href="/about"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  About Us
                </Link>
              </li>
              <li>
                <Link
                  href="/contact"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  Contact
                </Link>
              </li>
              <li>
                <Link
                  href="/orders"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  Track Order
                </Link>
              </li>
            </ul>
          </div>

          {/* Customer Service */}
          <div>
            <h4 className="text-lg font-bold mb-6">Legal & Policies</h4>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/privacy"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  Terms & Conditions
                </Link>
              </li>
              <li>
                <Link
                  href="/contact"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  Contact Support
                </Link>
              </li>
              <li>
                <a
                  href="mailto:HAFIZNAVEEDCHUHAN@GMAIL.COM"
                  className="text-gray-300 hover:text-pink-400 transition-colors"
                >
                  Email Support
                </a>
              </li>
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h4 className="text-lg font-bold mb-6">Newsletter</h4>
            <p className="text-gray-300 mb-4">
              Subscribe to get special offers and updates!
            </p>
            <form onSubmit={handleSubscribe} className="space-y-3">
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Your email"
                  className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full py-2 bg-gradient-to-r from-pink-500 to-purple-600 rounded-lg font-semibold hover:from-pink-600 hover:to-purple-700 transition-all"
              >
                Subscribe
              </button>
            </form>
            {subscribed && (
              <p className="text-green-400 text-sm mt-2 animate-fade-in">
                ✓ Thanks for subscribing!
              </p>
            )}
          </div>
        </div>

        {/* Developer Credit & Social Links */}
        <div className="mb-8 pb-8 border-b border-white/10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="text-center md:text-left">
              <p className="text-sm text-gray-400 mb-2">
                <span className="text-pink-400 font-semibold">Developer:</span> HAFIZ NAVEED UDDIN / AGENTIC AI DEVELOPER
              </p>
              <p className="text-sm text-gray-400">
                <span className="text-pink-400 font-semibold">Email:</span>{' '}
                <a
                  href="mailto:HAFIZNAVEEDCHUHAN@GMAIL.COM"
                  className="hover:text-pink-400 transition-colors"
                >
                  HAFIZNAVEEDCHUHAN@GMAIL.COM
                </a>
              </p>
            </div>
            <div className="flex items-center gap-6">
              <a
                href="#"
                className="text-gray-300 hover:text-pink-400 transition-colors"
                aria-label="Facebook"
              >
                <Facebook size={24} />
              </a>
              <a
                href="#"
                className="text-gray-300 hover:text-pink-400 transition-colors"
                aria-label="Instagram"
              >
                <Instagram size={24} />
              </a>
              <a
                href="#"
                className="text-gray-300 hover:text-pink-400 transition-colors"
                aria-label="Twitter"
              >
                <Twitter size={24} />
              </a>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="text-center">
          <p className="text-gray-400">
            © {new Date().getFullYear()} Fatima Zehra Boutique. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
