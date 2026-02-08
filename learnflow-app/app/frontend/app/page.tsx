"use client";

import Image from "next/image";
import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import { CATEGORIES, getProductsByCategory } from "@/lib/products";
import { ArrowRight, Heart, Truck, Shield } from "lucide-react";

export default function HomePage() {
  const handleAddToCart = (product: any) => {
    alert(`${product.name} added to cart!`);
  };

  return (
    <main className="min-h-screen">
      {/* ==================== HERO SECTION ==================== */}
      <section className="relative min-h-screen gradient-bg-hero dark:gradient-bg-hero-dark overflow-hidden">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23000000" fill-opacity="0.1"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          }}
        ></div>

        <div className="container-wide relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center py-20 md:py-32">
            <div className="animate-fade-in">
              <div className="mb-6">
                <span className="badge-pink text-sm">Welcome to Luxury Fashion</span>
              </div>

              <h1 className="gradient-text text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
                Fatima Zehra <br />
                <span className="gradient-text-elegant">Boutique</span>
              </h1>

              <p className="text-lg md:text-xl text-gray-700 dark:text-gray-300 mb-8 max-w-lg leading-relaxed">
                Discover the finest collection of premium ladies suits, shalwar qameez, and designer wear. Crafted with elegance and style for the modern Pakistani woman.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/products" className="btn-primary">
                  Explore Collection <ArrowRight size={20} />
                </Link>
                <button className="btn-secondary">
                  View Categories
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4 mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <Truck className="text-pink-500" size={24} />
                  <div>
                    <p className="font-semibold text-sm">Free Delivery</p>
                    <p className="text-xs text-gray-600">Orders over Rs 3000</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Shield className="text-pink-500" size={24} />
                  <div>
                    <p className="font-semibold text-sm">Secure Checkout</p>
                    <p className="text-xs text-gray-600">100% Safe</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Heart className="text-pink-500" size={24} />
                  <div>
                    <p className="font-semibold text-sm">Premium Quality</p>
                    <p className="text-xs text-gray-600">Guaranteed</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative h-96 md:h-full min-h-[600px] animate-fade-in-right">
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500/10 via-purple-500/10 to-amber-500/10 rounded-3xl"></div>
              <Image
                src="/images/fancy-suits/fancy-suits-01.jpg"
                alt="Fatima Zehra Boutique - Ladies Fashion Suit"
                fill
                className="object-cover rounded-3xl shadow-2xl"
                priority
              />
            </div>
          </div>
        </div>
      </section>

      {/* ==================== CATEGORIES SECTION ==================== */}
      <section className="section-padding bg-white dark:bg-gray-900">
        <div className="container-wide">
          <div className="text-center mb-16 animate-fade-in-up">
            <span className="badge-gold">Collections</span>
            <h2 className="text-4xl md:text-5xl font-bold gradient-text-elegant mt-4 mb-4">
              Browse Our Categories
            </h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Choose from our curated selection of premium suits and traditional wear
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {CATEGORIES.map((category) => (
              <Link key={category.id} href={`/products?category=${category.name}`}>
                <div className="group card-hover p-8 rounded-2xl text-center cursor-pointer border-2 border-transparent hover:border-pink-500 transition-all">
                  <div className="text-6xl mb-4 transform group-hover:scale-125 transition-transform duration-300">
                    {category.icon}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white group-hover:text-pink-500 transition-colors">
                    {category.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    10 Products
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ==================== FEATURED PRODUCTS ==================== */}
      {CATEGORIES.map((category) => (
        <section
          key={category.id}
          className="section-padding bg-gray-50 dark:bg-gray-800/50"
        >
          <div className="container-wide">
            <div className="flex items-center justify-between mb-12 animate-fade-in-up">
              <div>
                <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                  {category.name}
                </h2>
                <div className="w-20 h-1 gradient-bg-primary rounded-full"></div>
              </div>
              <Link
                href={`/products?category=${category.name}`}
                className="text-pink-600 dark:text-pink-400 font-semibold flex items-center gap-2 hover:gap-3 transition-all"
              >
                View All <ArrowRight size={20} />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              {getProductsByCategory(category.name)
                .slice(0, 5)
                .map((product, index) => (
                  <div
                    key={product.id}
                    className="animate-fade-in-up"
                    style={{
                      animationDelay: `${index * 50}ms`,
                    }}
                  >
                    <ProductCard
                      product={product}
                      onAddToCart={handleAddToCart}
                    />
                  </div>
                ))}
            </div>
          </div>
        </section>
      ))}

      {/* ==================== TESTIMONIALS SECTION ==================== */}
      <section className="section-padding bg-white dark:bg-gray-900">
        <div className="container-wide">
          <div className="text-center mb-16 animate-fade-in-up">
            <span className="badge-pink">Customer Love</span>
            <h2 className="text-4xl md:text-5xl font-bold gradient-text mt-4 mb-4">
              Testimonials
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                name: "Aisha Khan",
                text: "The quality of suits here is absolutely amazing. I love every piece I bought!",
                rating: 5,
                image: "/images/testimonials/customer-1.jpg",
              },
              {
                name: "Fatima Ali",
                text: "Excellent customer service and beautiful designs. Highly recommend!",
                rating: 5,
                image: "/images/testimonials/customer-2.jpg",
              },
              {
                name: "Sara Ahmed",
                text: "Premium quality at reasonable prices. Best boutique in town!",
                rating: 5,
                image: "/images/testimonials/customer-3.jpg",
              },
            ].map((testimonial, i) => (
              <div
                key={i}
                className="glass-card p-8 rounded-2xl text-center hover:shadow-lg transition-all"
              >
                <Image
                  src={testimonial.image}
                  alt={testimonial.name}
                  width={80}
                  height={80}
                  className="rounded-full mx-auto mb-4 border-4 border-pink-500"
                />
                <div className="flex justify-center gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, j) => (
                    <span key={j} className="text-amber-400 text-lg">
                      ★
                    </span>
                  ))}
                </div>
                <p className="text-gray-700 dark:text-gray-300 mb-4 italic">
                  "{testimonial.text}"
                </p>
                <p className="font-bold text-pink-600 dark:text-pink-400">
                  {testimonial.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ==================== CTA SECTION ==================== */}
      <section className="section-padding gradient-bg-primary relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 animate-gradient"></div>
        <div className="container-wide relative z-10 text-center">
          <div className="animate-fade-in-up">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Find Your Perfect Suit?
            </h2>
            <p className="text-pink-100 text-lg mb-8 max-w-2xl mx-auto">
              Explore our complete collection of 40+ premium ladies suits
            </p>
            <Link href="/products" className="btn-gold">
              Shop Now <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
