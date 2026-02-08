"use client";

import { useState } from "react";
import Link from "next/link";
import { ShoppingCart, User, Menu, X, Search, Home } from "lucide-react";
import { useCartStore } from "@/lib/store";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const cartCount = useCartStore((state) => state.itemCount);

  return (
    <nav className="fixed w-full top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b-2 border-gradient-to-r from-pink-500 to-purple-600 shadow-lg">
      <div className="container-wide py-4">
        <div className="flex items-center justify-between">
          {/* Logo with Icon */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all transform group-hover:scale-105">
              <span className="text-xl font-bold text-white">👗</span>
            </div>
            <div className="flex flex-col">
              <div className="text-xl font-serif font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                Fatima Zehra
              </div>
              <span className="text-xs font-semibold text-pink-600 dark:text-pink-400">BOUTIQUE</span>
            </div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <Link
              href="/"
              className="flex items-center gap-1 px-4 py-2 text-slate-700 dark:text-slate-300 hover:text-pink-600 dark:hover:text-pink-400 font-semibold transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 dark:hover:border-pink-700"
            >
              <Home size={18} />
              Home
            </Link>
            <Link
              href="/products"
              className="px-4 py-2 text-slate-700 dark:text-slate-300 hover:text-pink-600 dark:hover:text-pink-400 font-semibold transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 dark:hover:border-pink-700"
            >
              Shop
            </Link>
            <Link
              href="/about"
              className="px-4 py-2 text-slate-700 dark:text-slate-300 hover:text-pink-600 dark:hover:text-pink-400 font-semibold transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 dark:hover:border-pink-700"
            >
              About
            </Link>
            <Link
              href="/contact"
              className="px-4 py-2 text-slate-700 dark:text-slate-300 hover:text-pink-600 dark:hover:text-pink-400 font-semibold transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 dark:hover:border-pink-700"
            >
              Contact
            </Link>
          </div>

          {/* Right Icons */}
          <div className="flex items-center gap-3">
            {/* Search */}
            <button className="hidden sm:flex p-2 border-2 border-slate-200 dark:border-slate-700 hover:border-pink-500 dark:hover:border-pink-400 rounded-lg transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20">
              <Search size={20} className="text-slate-700 dark:text-slate-300 hover:text-pink-600" />
            </button>

            {/* Cart */}
            <Link
              href="/cart"
              className="relative p-2 border-2 border-slate-200 dark:border-slate-700 hover:border-pink-500 dark:hover:border-pink-400 rounded-lg transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20"
            >
              <ShoppingCart size={20} className="text-slate-700 dark:text-slate-300 hover:text-pink-600" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-br from-pink-500 to-purple-600 text-white text-xs rounded-full flex items-center justify-center font-bold shadow-lg">
                  {cartCount}
                </span>
              )}
            </Link>

            {/* User */}
            <Link
              href="/auth/login"
              className="hidden sm:flex p-2 border-2 border-slate-200 dark:border-slate-700 hover:border-pink-500 dark:hover:border-pink-400 rounded-lg transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20"
            >
              <User size={20} className="text-slate-700 dark:text-slate-300 hover:text-pink-600" />
            </Link>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden p-2 border-2 border-slate-200 dark:border-slate-700 hover:border-pink-500 dark:hover:border-pink-400 rounded-lg transition-all hover:bg-pink-50 dark:hover:bg-pink-900/20"
            >
              {isOpen ? (
                <X size={20} className="text-slate-700 dark:text-slate-300 hover:text-pink-600" />
              ) : (
                <Menu size={20} className="text-slate-700 dark:text-slate-300 hover:text-pink-600" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden mt-4 pt-4 border-t-2 border-slate-200 dark:border-slate-700 space-y-2 animate-fade-in-down">
            <Link
              href="/"
              className="block px-4 py-3 text-slate-700 dark:text-slate-300 hover:text-pink-600 font-semibold hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 transition-all"
              onClick={() => setIsOpen(false)}
            >
              🏠 Home
            </Link>
            <Link
              href="/products"
              className="block px-4 py-3 text-slate-700 dark:text-slate-300 hover:text-pink-600 font-semibold hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 transition-all"
              onClick={() => setIsOpen(false)}
            >
              🛍️ Shop
            </Link>
            <Link
              href="/about"
              className="block px-4 py-3 text-slate-700 dark:text-slate-300 hover:text-pink-600 font-semibold hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 transition-all"
              onClick={() => setIsOpen(false)}
            >
              ℹ️ About
            </Link>
            <Link
              href="/contact"
              className="block px-4 py-3 text-slate-700 dark:text-slate-300 hover:text-pink-600 font-semibold hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 transition-all"
              onClick={() => setIsOpen(false)}
            >
              📧 Contact
            </Link>
            <Link
              href="/auth/login"
              className="block px-4 py-3 text-slate-700 dark:text-slate-300 hover:text-pink-600 font-semibold hover:bg-pink-50 dark:hover:bg-pink-900/20 rounded-lg border border-transparent hover:border-pink-300 transition-all"
              onClick={() => setIsOpen(false)}
            >
              👤 Login
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
