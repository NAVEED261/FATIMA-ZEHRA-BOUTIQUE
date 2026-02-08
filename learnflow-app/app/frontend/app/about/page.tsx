import Image from 'next/image'
import Link from 'next/link'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-pink-500 via-purple-500 to-pink-500 py-24">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <h1 className="text-7xl md:text-8xl font-serif font-bold mb-6 text-white drop-shadow-lg">
            Fatima Zehra <br />
            <span className="bg-gradient-to-r from-yellow-200 to-pink-200 bg-clip-text text-transparent">
              Boutique
            </span>
          </h1>
          <p className="text-2xl md:text-3xl text-white font-light drop-shadow">
            Elegant Fashion for Every Occasion
          </p>
        </div>
      </div>

      {/* About Section */}
      <div className="max-w-5xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          <div>
            <h2 className="text-4xl font-serif font-bold mb-6">Our Story</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              Founded with a passion for elegant fashion, Fatima Zehra Boutique
              has been serving customers who appreciate quality and style.
              Every piece in our collection is carefully selected to ensure that
              our customers feel confident and beautiful.
            </p>
            <p className="text-gray-700 leading-relaxed">
              We believe that fashion is more than just clothing—it's a form of
              self-expression. Our mission is to provide our customers with
              access to the finest fashion pieces that make them feel special
              on every occasion.
            </p>
          </div>
          <div className="relative h-96 rounded-lg overflow-hidden shadow-xl">
            <Image
              src="/images/about-hero.jpg"
              alt="Elegant Ladies Suit - Fatima Zehra Boutique"
              width={500}
              height={600}
              className="object-cover rounded-lg"
              priority
            />
          </div>
        </div>

        {/* Mission & Values */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-5xl mb-4">✨</div>
            <h3 className="text-2xl font-serif font-bold mb-4">Quality</h3>
            <p className="text-gray-600">
              Every item is selected for its quality, ensuring our customers
              get the best value for their investment.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-5xl mb-4">💎</div>
            <h3 className="text-2xl font-serif font-bold mb-4">Style</h3>
            <p className="text-gray-600">
              Our curated collection features the latest trends and timeless
              pieces that work for every occasion.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-5xl mb-4">❤️</div>
            <h3 className="text-2xl font-serif font-bold mb-4">Service</h3>
            <p className="text-gray-600">
              We're committed to providing exceptional customer service and
              ensuring every shopping experience is delightful.
            </p>
          </div>
        </div>

        {/* Contact Section */}
        <div className="bg-white rounded-lg shadow-md p-12 text-center mb-16">
          <h2 className="text-3xl font-serif font-bold mb-6">Get in Touch</h2>
          <p className="text-gray-600 mb-8">
            Have questions? We'd love to hear from you!
          </p>
          <div className="space-y-3 text-gray-700 mb-8">
            <p>
              <strong>Email:</strong> info@fatimaboutique.com
            </p>
            <p>
              <strong>Phone:</strong> +1 (555) 123-4567
            </p>
            <p>
              <strong>Hours:</strong> Monday - Friday, 9 AM - 6 PM
            </p>
          </div>
          <button className="bg-pink-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-pink-700 transition">
            Contact Us
          </button>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <h2 className="text-3xl font-serif font-bold mb-6">
            Discover Our Collection
          </h2>
          <p className="text-gray-600 mb-8 text-lg">
            Browse our beautiful selection of elegant fashion pieces
          </p>
          <Link
            href="/products"
            className="inline-block bg-pink-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-pink-700 transition"
          >
            Shop Now
          </Link>
        </div>
      </div>
    </div>
  )
}
