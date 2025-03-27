"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/router"
import { useSession } from "next-auth/react"
import Image from "next/image"
import Link from "next/link"
import Layout from "../../components/layout/Layout"
import { wineApi } from "../../lib/api"
import {
  Star,
  ArrowLeft,
  Loader,
  AlertCircle,
  Heart,
  Share2,
  ShoppingCart,
  WineIcon,
  Grape,
  MapPin,
  Calendar,
  Tag,
} from "lucide-react"

// Format trait name for display
const formatTraitName = (trait) => {
  return trait
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

export default function WineDetailsPage() {
  const router = useRouter()
  const { data: session } = useSession()
  const { id } = router.query
  const [wine, setWine] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [isFavorite, setIsFavorite] = useState(false)
  const [similarWines, setSimilarWines] = useState([])
  const [loadingSimilar, setLoadingSimilar] = useState(false)

  useEffect(() => {
    if (router.isReady && id) {
      fetchWineDetails(id)
    }
  }, [router.isReady, id])

  const fetchWineDetails = async (wineId) => {
    setLoading(true)
    setError("")

    try {
      const wineData = await wineApi.getWineById(wineId)
      setWine(wineData)

      // Check if wine is in user's favorites
      if (session?.user) {
        const isFav = await wineApi.checkFavorite(wineId)
        setIsFavorite(isFav)
      }

      // Fetch similar wines
      fetchSimilarWines(wineId)
    } catch (err) {
      setError(err.message || "Failed to fetch wine details. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const fetchSimilarWines = async (wineId) => {
    setLoadingSimilar(true)
    try {
      const similar = await wineApi.getSimilarWines(wineId)
      setSimilarWines(similar || [])
    } catch (err) {
      console.error("Error fetching similar wines:", err)
    } finally {
      setLoadingSimilar(false)
    }
  }

  const toggleFavorite = async () => {
    if (!session) {
      router.push("/auth/signin?callbackUrl=" + encodeURIComponent(router.asPath))
      return
    }

    try {
      if (isFavorite) {
        await wineApi.removeFromFavorites(wine.id)
      } else {
        await wineApi.addToFavorites(wine.id)
      }
      setIsFavorite(!isFavorite)
    } catch (err) {
      console.error("Error toggling favorite:", err)
    }
  }

  const addToCart = async () => {
    if (!session) {
      router.push("/auth/signin?callbackUrl=" + encodeURIComponent(router.asPath))
      return
    }

    try {
      await wineApi.addToCart(wine.id)
      // Show success notification or update cart count
    } catch (err) {
      console.error("Error adding to cart:", err)
    }
  }

  const shareWine = () => {
    if (navigator.share) {
      navigator.share({
        title: wine?.name,
        text: `Check out this wine: ${wine?.name} from ${wine?.winery}`,
        url: window.location.href,
      })
    } else {
      // Fallback for browsers that don't support the Web Share API
      navigator.clipboard.writeText(window.location.href)
      // Show a notification that the link was copied
    }
  }

  if (loading) {
    return (
      <Layout title="Loading Wine Details" description="Loading wine details...">
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <Loader className="h-12 w-12 animate-spin text-burgundy-600 dark:text-burgundy-400" />
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">Loading wine details...</p>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout title="Error" description="Error loading wine details">
        <div className="container mx-auto px-4 py-12">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 flex flex-col items-center">
            <AlertCircle className="h-12 w-12 text-red-500 dark:text-red-400 mb-4" />
            <h2 className="text-xl font-medium text-red-800 dark:text-red-300 mb-2">Error Loading Wine Details</h2>
            <p className="text-red-600 dark:text-red-400 text-center">{error}</p>
            <Link
              href="/wines/browse"
              className="mt-6 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-burgundy-600 hover:bg-burgundy-700"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Browse
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  if (!wine) {
    return (
      <Layout title="Wine Not Found" description="Wine not found">
        <div className="container mx-auto px-4 py-12">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 flex flex-col items-center">
            <AlertCircle className="h-12 w-12 text-yellow-500 dark:text-yellow-400 mb-4" />
            <h2 className="text-xl font-medium text-yellow-800 dark:text-yellow-300 mb-2">Wine Not Found</h2>
            <p className="text-yellow-600 dark:text-yellow-400 text-center">
              We couldn't find the wine you're looking for. It may have been removed or is no longer available.
            </p>
            <Link
              href="/wines/browse"
              className="mt-6 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-burgundy-600 hover:bg-burgundy-700"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Browse
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout
      title={`${wine.name} | ${wine.winery}`}
      description={`${wine.name} - ${wine.description?.substring(0, 160) || "Explore this wine"}`}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back button */}
        <div className="mb-8">
          <Link
            href="/wines/browse"
            className="inline-flex items-center text-burgundy-600 dark:text-burgundy-400 hover:text-burgundy-800 dark:hover:text-burgundy-300"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Browse
          </Link>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="md:flex">
            {/* Wine Image */}
            <div className="md:w-1/3 bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-8">
              <div className="relative h-80 w-full">
                {wine.image_url ? (
                  <Image src={wine.image_url || "/placeholder.svg"} alt={wine.name} fill className="object-contain" />
                ) : (
                  <div className="h-full w-full flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-md">
                    <WineIcon className="h-24 w-24 text-gray-400 dark:text-gray-600" />
                  </div>
                )}
              </div>
            </div>

            {/* Wine Details */}
            <div className="md:w-2/3 p-8">
              <div className="flex flex-col h-full">
                <div className="flex-grow">
                  {/* Wine Category */}
                  <div className="mb-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-burgundy-100 text-burgundy-800 dark:bg-burgundy-900/30 dark:text-burgundy-400">
                      {wine.category}
                    </span>
                    {wine.rating >= 90 && (
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
                        Top Rated
                      </span>
                    )}
                  </div>

                  {/* Wine Name and Winery */}
                  <h1 className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-1">{wine.name}</h1>
                  <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">{wine.winery}</p>

                  {/* Rating */}
                  <div className="flex items-center mb-6">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`h-5 w-5 ${
                            i < Math.floor(wine.rating / 20)
                              ? "text-amber-400 fill-amber-400"
                              : i < Math.ceil(wine.rating / 20)
                                ? "text-amber-400 fill-amber-400 opacity-50"
                                : "text-gray-300 dark:text-gray-600"
                          }`}
                        />
                      ))}
                    </div>
                    <span className="ml-2 text-gray-700 dark:text-gray-300 font-medium">
                      {(wine.rating / 20).toFixed(1)}
                    </span>
                    <span className="ml-1 text-gray-500 dark:text-gray-400">({wine.reviews_count || 0} reviews)</span>
                  </div>

                  {/* Wine Details Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="flex items-center">
                      <Grape className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                      <span className="text-gray-700 dark:text-gray-300">
                        {wine.grape_variety || "Variety not specified"}
                      </span>
                    </div>
                    <div className="flex items-center">
                      <MapPin className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                      <span className="text-gray-700 dark:text-gray-300">
                        {wine.region || wine.country || "Region not specified"}
                      </span>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                      <span className="text-gray-700 dark:text-gray-300">
                        {wine.vintage || "Vintage not specified"}
                      </span>
                    </div>
                    <div className="flex items-center">
                      <Tag className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                      <span className="text-gray-700 dark:text-gray-300">
                        {wine.price ? `$${wine.price.toFixed(2)}` : "Price not available"}
                      </span>
                    </div>
                  </div>

                  {/* Wine Description */}
                  <div className="mb-6">
                    <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Description</h2>
                    <p className="text-gray-700 dark:text-gray-300">
                      {wine.description || "No description available for this wine."}
                    </p>
                  </div>

                  {/* Wine Characteristics */}
                  {wine.traits && wine.traits.length > 0 && (
                    <div className="mb-6">
                      <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Characteristics</h2>
                      <div className="flex flex-wrap gap-2">
                        {wine.traits.map((trait) => (
                          <span
                            key={trait}
                            className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
                          >
                            {formatTraitName(trait)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Food Pairings */}
                  {wine.food_pairings && wine.food_pairings.length > 0 && (
                    <div className="mb-6">
                      <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Food Pairings</h2>
                      <div className="flex flex-wrap gap-2">
                        {wine.food_pairings.map((pairing) => (
                          <span
                            key={pairing}
                            className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                          >
                            {pairing}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-4 mt-8">
                  <button
                    onClick={addToCart}
                    className="flex-1 min-w-[120px] inline-flex items-center justify-center px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-burgundy-600 hover:bg-burgundy-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-burgundy-500"
                  >
                    <ShoppingCart className="h-5 w-5 mr-2" />
                    Add to Cart
                  </button>
                  <button
                    onClick={toggleFavorite}
                    className={`inline-flex items-center justify-center px-4 py-3 border ${
                      isFavorite
                        ? "border-burgundy-600 text-burgundy-600 dark:border-burgundy-400 dark:text-burgundy-400"
                        : "border-gray-300 text-gray-700 dark:border-gray-600 dark:text-gray-300"
                    } rounded-md shadow-sm text-base font-medium hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-burgundy-500`}
                  >
                    <Heart className={`h-5 w-5 ${isFavorite ? "fill-burgundy-600 dark:fill-burgundy-400" : ""}`} />
                  </button>
                  <button
                    onClick={shareWine}
                    className="inline-flex items-center justify-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-burgundy-500"
                  >
                    <Share2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Similar Wines Section */}
        <div className="mt-12">
          <h2 className="text-2xl font-serif font-bold text-gray-900 dark:text-white mb-6">You May Also Like</h2>

          {loadingSimilar ? (
            <div className="flex justify-center py-8">
              <Loader className="h-8 w-8 animate-spin text-burgundy-600 dark:text-burgundy-400" />
            </div>
          ) : similarWines.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {similarWines.map((similarWine) => (
                <Link
                  key={similarWine.id}
                  href={`/wines/${similarWine.id}`}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
                >
                  <div className="p-4">
                    <div className="aspect-w-2 aspect-h-3 bg-gray-100 dark:bg-gray-900 rounded-md mb-4">
                      {similarWine.image_url ? (
                        <Image
                          src={similarWine.image_url || "/placeholder.svg"}
                          alt={similarWine.name}
                          width={150}
                          height={200}
                          className="object-contain mx-auto"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <WineIcon className="h-12 w-12 text-gray-400 dark:text-gray-600" />
                        </div>
                      )}
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white line-clamp-1">
                      {similarWine.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{similarWine.winery}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Star className="h-4 w-4 text-amber-400 fill-amber-400" />
                        <span className="ml-1 text-sm text-gray-700 dark:text-gray-300">
                          {(similarWine.rating / 20).toFixed(1)}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {similarWine.price ? `$${similarWine.price.toFixed(2)}` : "N/A"}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600 dark:text-gray-400">No similar wines found.</div>
          )}
        </div>
      </div>
    </Layout>
  )
}

