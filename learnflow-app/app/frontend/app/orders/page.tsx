'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { orderAPI } from '@/lib/api'
import { auth } from '@/lib/auth'
import { Package, ChevronDown, ChevronRight } from 'lucide-react'

interface OrderItem {
  productId: number
  name: string
  quantity: number
  price: number
}

interface Order {
  id: string
  items: OrderItem[]
  total: number
  status: string
  createdAt: string
}

export default function OrdersPage() {
  const router = useRouter()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedOrder, setExpandedOrder] = useState<string | null>(null)

  useEffect(() => {
    const fetchOrders = async () => {
      if (!auth.isAuthenticated()) {
        router.push('/auth/login')
        return
      }

      try {
        const response = await orderAPI.getOrders()
        setOrders(response.orders || [])
      } catch (error) {
        console.error('Failed to fetch orders:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchOrders()
  }, [router])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center pt-20">
        <div className="text-gray-500">Loading orders...</div>
      </div>
    )
  }

  if (orders.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pt-20">
        <div className="container-wide py-16">
          <div className="text-center">
            <Package className="mx-auto text-gray-400 mb-6" size={80} />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              No Orders Yet
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              You haven't placed any orders yet.
            </p>
            <Link
              href="/products"
              className="inline-block bg-pink-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-pink-700 transition"
            >
              Start Shopping
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pt-20">
      <div className="container-wide py-12">
        <h1 className="text-4xl font-serif font-bold text-gray-900 dark:text-white mb-8">
          Order History
        </h1>

        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              {/* Order Header */}
              <button
                onClick={() => setExpandedOrder(expandedOrder === order.id ? null : order.id)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                <div className="text-left flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                      Order #{order.id}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(order.status)}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                  </div>
                  <div className="flex gap-8 text-sm text-gray-600 dark:text-gray-400">
                    <div>
                      <span className="text-gray-500">Date: </span>
                      {new Date(order.createdAt).toLocaleDateString()}
                    </div>
                    <div>
                      <span className="text-gray-500">Total: </span>
                      <span className="font-semibold text-pink-600">Rs {order.total.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                {expandedOrder === order.id ? (
                  <ChevronDown className="text-gray-400" size={24} />
                ) : (
                  <ChevronRight className="text-gray-400" size={24} />
                )}
              </button>

              {/* Order Details (Expanded) */}
              {expandedOrder === order.id && (
                <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Items</h4>
                  <div className="space-y-2">
                    {order.items.map((item, idx) => (
                      <div key={idx} className="flex justify-between text-sm py-2 border-b border-gray-100 dark:border-gray-700">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{item.name}</p>
                          <p className="text-gray-600 dark:text-gray-400">Qty: {item.quantity}</p>
                        </div>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          Rs {(item.price * item.quantity).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex justify-between font-semibold text-lg">
                      <span className="text-gray-900 dark:text-white">Total</span>
                      <span className="text-pink-600">Rs {order.total.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
