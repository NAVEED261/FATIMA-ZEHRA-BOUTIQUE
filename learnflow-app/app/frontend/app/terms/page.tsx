"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <section className="bg-gradient-to-r from-pink-500 to-purple-600 text-white py-12">
        <div className="container-wide">
          <Link href="/" className="inline-flex items-center gap-2 text-pink-100 hover:text-white transition-colors mb-4">
            <ArrowLeft size={20} />
            Back to Home
          </Link>
          <h1 className="text-5xl font-bold mb-4">Terms & Conditions</h1>
          <p className="text-xl text-pink-50">Last updated: January 2026</p>
        </div>
      </section>

      {/* Content */}
      <section className="py-16 bg-white dark:bg-slate-800">
        <div className="container-wide max-w-4xl mx-auto prose dark:prose-invert">
          <div className="space-y-8">
            {/* Introduction */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">1. Introduction</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                Welcome to Fatima Zehra Boutique ("we," "our," or "us"). These Terms and Conditions ("Terms") govern your use of our website and services. By accessing and using this website, you accept and agree to be bound by the terms and provision of this agreement.
              </p>
            </div>

            {/* Intellectual Property */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">2. Intellectual Property Rights</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                All content included in or made available through our website, such as text, graphics, logos, images, audio clips, digital downloads, and data compilations, is the property of Fatima Zehra Boutique or its content suppliers and is protected by international copyright laws.
              </p>
            </div>

            {/* User Responsibilities */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">3. User Responsibilities</h2>
              <div className="space-y-4">
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">You agree to:</p>
                <ul className="list-disc list-inside space-y-2 text-slate-600 dark:text-slate-300">
                  <li>Provide accurate and complete information in all forms and interactions</li>
                  <li>Maintain the confidentiality of your account information</li>
                  <li>Not engage in any unlawful or prohibited activities</li>
                  <li>Respect the intellectual property rights of others</li>
                  <li>Not attempt to gain unauthorized access to our systems</li>
                </ul>
              </div>
            </div>

            {/* Product Information */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">4. Product Information</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                We strive to provide accurate descriptions and pricing of all products. However, we do not warrant that product descriptions, pricing, or other content is accurate, complete, reliable, current, or error-free. If a product offered by Fatima Zehra Boutique is not as described, your sole remedy is to return it in unused condition.
              </p>
            </div>

            {/* Return & Refund Policy */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">5. Return & Refund Policy</h2>
              <div className="space-y-4">
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  <strong>Return Window:</strong> Products can be returned within 14 days of delivery in original condition with all tags attached.
                </p>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  <strong>Condition Requirements:</strong> Items must be unworn, unwashed, and undamaged. Original packaging must be included.
                </p>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  <strong>Refund Processing:</strong> Once approved, refunds will be processed within 5-7 business days to the original payment method.
                </p>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  <strong>Exclusions:</strong> Sale items and custom orders cannot be returned.
                </p>
              </div>
            </div>

            {/* Shipping Policy */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">6. Shipping Policy</h2>
              <div className="space-y-4">
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  <strong>Delivery Time:</strong> Orders are typically delivered within 5-7 business days within Pakistan.
                </p>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  <strong>Shipping Charges:</strong> Free shipping on orders over Rs 3,000. Orders below Rs 3,000 incur standard shipping charges.
                </p>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  <strong>International Shipping:</strong> Currently available to selected countries. Additional customs duties may apply.
                </p>
              </div>
            </div>

            {/* Payment Terms */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">7. Payment Terms</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                We accept multiple payment methods including credit cards, debit cards, online banking transfers, and mobile wallets. All payment information is securely encrypted and transmitted. Your payment method will be charged at the time of order confirmation.
              </p>
            </div>

            {/* Limitation of Liability */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">8. Limitation of Liability</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                To the fullest extent permitted by law, Fatima Zehra Boutique shall not be liable for any indirect, incidental, special, consequential, or punitive damages, even if advised of the possibility of such damages. Our total liability shall not exceed the amount paid by you in the last transaction.
              </p>
            </div>

            {/* Governing Law */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">9. Governing Law</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                These Terms and Conditions are governed by and construed in accordance with the laws of Pakistan, and you irrevocably submit to the exclusive jurisdiction of the courts located in Lahore, Pakistan.
              </p>
            </div>

            {/* Changes to Terms */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">10. Changes to Terms</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                We reserve the right to modify these Terms and Conditions at any time. Your continued use of the website following any such modification constitutes your agreement to abide by and be bound by these Terms as modified.
              </p>
            </div>

            {/* Contact Information */}
            <div className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900 dark:to-purple-900 p-8 rounded-lg">
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">11. Contact Information</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                If you have any questions about these Terms and Conditions, please contact us at:
              </p>
              <div className="space-y-2 text-slate-600 dark:text-slate-300">
                <p><strong>Email:</strong> <a href="mailto:HAFIZNAVEEDCHUHAN@GMAIL.COM" className="text-pink-600 dark:text-pink-400 hover:underline">HAFIZNAVEEDCHUHAN@GMAIL.COM</a></p>
                <p><strong>Phone:</strong> <a href="tel:+923001234567" className="text-pink-600 dark:text-pink-400 hover:underline">+92 300 1234567</a></p>
                <p><strong>Address:</strong> Lahore, Pakistan</p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="mt-12 pt-8 border-t border-slate-200 dark:border-slate-700">
            <div className="flex justify-center gap-6 flex-wrap">
              <Link href="/privacy" className="text-pink-600 dark:text-pink-400 hover:underline font-semibold">
                Privacy Policy
              </Link>
              <span className="text-slate-400">•</span>
              <Link href="/contact" className="text-pink-600 dark:text-pink-400 hover:underline font-semibold">
                Contact Us
              </Link>
              <span className="text-slate-400">•</span>
              <Link href="/" className="text-pink-600 dark:text-pink-400 hover:underline font-semibold">
                Home
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
