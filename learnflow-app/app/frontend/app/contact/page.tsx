"use client";

import { useState } from "react";
import { Mail, Phone, MapPin, Send } from "lucide-react";
import Link from "next/link";

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    feedback: "",
  });

  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    // Simulate form submission
    await new Promise((resolve) => setTimeout(resolve, 1000));

    setSubmitted(true);
    setFormData({ name: "", email: "", phone: "", feedback: "" });
    setLoading(false);

    // Hide success message after 5 seconds
    setTimeout(() => setSubmitted(false), 5000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-pink-500 to-purple-600 text-white py-20">
        <div className="container-wide text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-4">Get In Touch</h1>
          <p className="text-xl text-pink-50 max-w-2xl mx-auto">
            We'd love to hear from you. Send us your feedback, questions, or inquiries and we'll get back to you as soon as possible.
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16 bg-white dark:bg-slate-800">
        <div className="container-wide">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6 text-slate-900 dark:text-white">Our Mission</h2>
              <p className="text-lg text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
                At Fatima Zehra Boutique, our mission is to empower every woman with access to premium, elegant fashion that celebrates her unique style and personality.
              </p>
              <p className="text-lg text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
                We believe that fashion is not just about clothing—it's about confidence, expression, and celebrating the beauty within every individual.
              </p>
              <p className="text-lg text-slate-600 dark:text-slate-300 leading-relaxed">
                Every piece in our collection is carefully curated to ensure quality, style, and affordability, making luxury fashion accessible to all.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-pink-100 to-pink-200 dark:from-pink-900 dark:to-pink-800 p-8 rounded-lg text-center">
                <div className="text-4xl font-bold text-pink-600 dark:text-pink-300 mb-2">40+</div>
                <p className="text-slate-700 dark:text-slate-300 font-semibold">Premium Products</p>
              </div>
              <div className="bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-900 dark:to-purple-800 p-8 rounded-lg text-center">
                <div className="text-4xl font-bold text-purple-600 dark:text-purple-300 mb-2">4</div>
                <p className="text-slate-700 dark:text-slate-300 font-semibold">Collections</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Info Section */}
      <section className="py-16 bg-slate-50 dark:bg-slate-700">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-center mb-12 text-slate-900 dark:text-white">Contact Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white dark:bg-slate-800 p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-pink-100 dark:bg-pink-900 p-4 rounded-full">
                  <Mail className="text-pink-600 dark:text-pink-300" size={24} />
                </div>
              </div>
              <h3 className="text-xl font-bold text-center mb-2 text-slate-900 dark:text-white">Email</h3>
              <p className="text-center text-slate-600 dark:text-slate-300">
                <a href="mailto:HAFIZNAVEEDCHUHAN@GMAIL.COM" className="hover:text-pink-600 dark:hover:text-pink-400 transition-colors">
                  HAFIZNAVEEDCHUHAN@GMAIL.COM
                </a>
              </p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-purple-100 dark:bg-purple-900 p-4 rounded-full">
                  <Phone className="text-purple-600 dark:text-purple-300" size={24} />
                </div>
              </div>
              <h3 className="text-xl font-bold text-center mb-2 text-slate-900 dark:text-white">Phone</h3>
              <p className="text-center text-slate-600 dark:text-slate-300">
                <a href="tel:+923001234567" className="hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                  +92 300 1234567
                </a>
              </p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-blue-100 dark:bg-blue-900 p-4 rounded-full">
                  <MapPin className="text-blue-600 dark:text-blue-300" size={24} />
                </div>
              </div>
              <h3 className="text-xl font-bold text-center mb-2 text-slate-900 dark:text-white">Location</h3>
              <p className="text-center text-slate-600 dark:text-slate-300">
                Lahore, Pakistan
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Form Section */}
      <section className="py-16 bg-white dark:bg-slate-800">
        <div className="container-wide max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-slate-900 dark:text-white">Send us a Message</h2>

          {submitted && (
            <div className="mb-8 p-4 bg-green-100 dark:bg-green-900 border border-green-400 dark:border-green-600 text-green-800 dark:text-green-200 rounded-lg">
              ✓ Thank you! Your message has been received. We'll get back to you soon.
            </div>
          )}

          <form onSubmit={handleSubmit} className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-600 p-8 rounded-lg shadow-lg">
            {/* Name Field */}
            <div className="mb-6">
              <label className="block text-slate-900 dark:text-white font-semibold mb-2">Full Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
                className="w-full px-4 py-3 border border-slate-300 dark:border-slate-500 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
              />
            </div>

            {/* Email Field */}
            <div className="mb-6">
              <label className="block text-slate-900 dark:text-white font-semibold mb-2">Email Address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email address"
                className="w-full px-4 py-3 border border-slate-300 dark:border-slate-500 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
              />
            </div>

            {/* Contact Number Field */}
            <div className="mb-6">
              <label className="block text-slate-900 dark:text-white font-semibold mb-2">Contact Number</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                required
                placeholder="Enter your contact number"
                className="w-full px-4 py-3 border border-slate-300 dark:border-slate-500 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
              />
            </div>

            {/* Feedback Field */}
            <div className="mb-6">
              <label className="block text-slate-900 dark:text-white font-semibold mb-2">Feedback & Message</label>
              <textarea
                name="feedback"
                value={formData.feedback}
                onChange={handleChange}
                required
                rows={6}
                placeholder="Share your feedback, questions, or inquiries..."
                className="w-full px-4 py-3 border border-slate-300 dark:border-slate-500 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 resize-none"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
              {loading ? "Sending..." : "Send Message"}
            </button>
          </form>

          {/* Additional Links */}
          <div className="mt-8 text-center">
            <p className="text-slate-600 dark:text-slate-300 mb-4">
              Want to know more about us?
            </p>
            <div className="flex justify-center gap-4 flex-wrap">
              <Link href="/about" className="text-pink-600 dark:text-pink-400 hover:underline font-semibold">
                About Us
              </Link>
              <span className="text-slate-400">•</span>
              <Link href="/products" className="text-pink-600 dark:text-pink-400 hover:underline font-semibold">
                Shop Now
              </Link>
              <span className="text-slate-400">•</span>
              <Link href="/terms" className="text-pink-600 dark:text-pink-400 hover:underline font-semibold">
                Terms & Conditions
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
