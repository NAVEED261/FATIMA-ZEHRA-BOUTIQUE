"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <section className="bg-gradient-to-r from-pink-500 to-purple-600 text-white py-12">
        <div className="container-wide">
          <Link href="/" className="inline-flex items-center gap-2 text-pink-100 hover:text-white transition-colors mb-4">
            <ArrowLeft size={20} />
            Back to Home
          </Link>
          <h1 className="text-5xl font-bold mb-4">Privacy Policy</h1>
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
                Fatima Zehra Boutique ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website, including any other media form, media channel, mobile website, or mobile application related or connected to it (collectively, the "Site").
              </p>
            </div>

            {/* Information We Collect */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">2. Information We Collect</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Personal Information</h3>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    We collect information you provide directly to us, such as when you create an account, make a purchase, or contact us. This includes your name, email address, postal address, phone number, and payment information.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Automatic Information</h3>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    We automatically collect certain information about your device and how you interact with our Site, including IP address, browser type, pages visited, and the time and date of your visit.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Cookies</h3>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    We use cookies to enhance your experience on our Site. You can control cookies through your browser settings.
                  </p>
                </div>
              </div>
            </div>

            {/* Use of Information */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">3. Use of Information</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">We use the information we collect to:</p>
              <ul className="list-disc list-inside space-y-2 text-slate-600 dark:text-slate-300 mb-4">
                <li>Process your orders and send order-related information</li>
                <li>Provide customer support and respond to your inquiries</li>
                <li>Send promotional emails, newsletters, and marketing communications (with your consent)</li>
                <li>Improve our Site, products, and services</li>
                <li>Comply with legal obligations</li>
                <li>Prevent fraud and enhance security</li>
              </ul>
            </div>

            {/* Data Protection */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">4. Data Protection & Security</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                We implement appropriate administrative, technical, and physical security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. All payment information is encrypted using SSL technology.
              </p>
            </div>

            {/* Sharing of Information */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">5. Sharing of Information</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                We do not sell, trade, or rent your personal information to third parties. We may share information with:
              </p>
              <ul className="list-disc list-inside space-y-2 text-slate-600 dark:text-slate-300 mb-4">
                <li>Service providers who assist us in operating our Site and conducting our business</li>
                <li>Legal authorities if required by law or to protect our rights</li>
                <li>Business partners with your consent</li>
              </ul>
            </div>

            {/* Your Rights */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">6. Your Rights</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">You have the right to:</p>
              <ul className="list-disc list-inside space-y-2 text-slate-600 dark:text-slate-300 mb-4">
                <li>Access the personal information we hold about you</li>
                <li>Request correction of inaccurate information</li>
                <li>Request deletion of your information (subject to legal obligations)</li>
                <li>Opt-out of marketing communications</li>
                <li>Data portability upon request</li>
              </ul>
            </div>

            {/* Third-Party Links */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">7. Third-Party Links</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                Our Site may contain links to third-party websites. We are not responsible for the privacy practices of these external sites. We encourage you to review their privacy policies before providing any personal information.
              </p>
            </div>

            {/* Children's Privacy */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">8. Children's Privacy</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                Our Site is not intended for children under 18 years of age. We do not knowingly collect personal information from children. If we become aware that we have collected information from a child, we will delete such information immediately.
              </p>
            </div>

            {/* International Transfers */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">9. International Transfers</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                Your information may be transferred to, stored in, and processed in countries other than your country of residence. By using our Site, you consent to the transfer of your information to countries outside your country of residence.
              </p>
            </div>

            {/* Policy Changes */}
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">10. Changes to Privacy Policy</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                We may update this Privacy Policy from time to time to reflect changes in our practices or for other operational, legal, or regulatory reasons. Your continued use of our Site following any such modification constitutes your acceptance of the updated Privacy Policy.
              </p>
            </div>

            {/* Contact & Rights */}
            <div className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900 dark:to-purple-900 p-8 rounded-lg">
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">11. Contact & Your Rights</h2>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                If you have questions about this Privacy Policy, wish to access your information, or want to exercise your privacy rights, please contact us at:
              </p>
              <div className="space-y-2 text-slate-600 dark:text-slate-300">
                <p><strong>Email:</strong> <a href="mailto:HAFIZNAVEEDCHUHAN@GMAIL.COM" className="text-pink-600 dark:text-pink-400 hover:underline">HAFIZNAVEEDCHUHAN@GMAIL.COM</a></p>
                <p><strong>Phone:</strong> <a href="tel:+923001234567" className="text-pink-600 dark:text-pink-400 hover:underline">+92 300 1234567</a></p>
                <p><strong>Address:</strong> Lahore, Pakistan</p>
              </div>
            </div>

            {/* GDPR Notice */}
            <div className="bg-blue-50 dark:bg-blue-900 p-8 rounded-lg border-l-4 border-blue-500">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">GDPR & Data Privacy</h3>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                For users in the European Union and United Kingdom, we comply with the General Data Protection Regulation (GDPR) and UK Data Protection Act. You have additional rights including data access, portability, and the right to be forgotten. Please contact us to exercise these rights.
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="mt-12 pt-8 border-t border-slate-200 dark:border-slate-700">
            <div className="flex justify-center gap-6 flex-wrap">
              <Link href="/terms" className="text-pink-600 dark:text-pink-400 hover:underline font-semibold">
                Terms & Conditions
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
