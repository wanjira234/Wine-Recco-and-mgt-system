"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/router"
import { useSession } from "next-auth/react"
import Layout from "../../components/layout/Layout"
import { wineApi } from "../../lib/api"
import WineCard from "../../components/wines/WineCard"
import { X, Wine, Loader, AlertCircle, ChevronDown, Search, SlidersHorizontal } from "lucide-react"

// Wine categories
const categories = [
  { name: "Red Wine", description: "Wines made from red or black grapes" },
  { name: "White Wine", description: "Wines made from white grapes" },
  { name: "Rosé Wine", description: "Wines with a pink color, made from red grapes" },
  { name: "Sparkling Wine", description: "Wines with significant levels of carbon dioxide" },
]

// Wine trait categories
const trait_categories = {
  taste: ["sweet", "dry", "tart", "crisp", "tangy", "juicy", "rich", "smooth", "soft", "sharp"],
  aroma: [
    "almond",
    "anise",
    "apple",
    "apricot",
    "berry",
    "black_cherry",
    "blackberry",
    "blueberry",
    "citrus",
    "peach",
    "pear",
    "plum",
    "raspberry",
    "strawberry",
    "tropical_fruit",
    "vanilla",
    "chocolate",
    "coffee",
    "caramel",
    "honey",
    "spice",
    "cinnamon",
    "nutmeg",
    "pepper",
  ],
  body: ["light_bodied", "medium_bodied", "full_bodied", "dense", "thick", "weight", "robust", "hearty"],
  texture: ["silky", "velvety", "smooth", "round", "plush", "supple", "firm", "tannin", "gripping"],
  character: ["complex", "elegant", "fresh", "vibrant", "bright", "powerful", "concentrated", "refined"],
  notes: ["floral", "herbal", "earthy", "mineral", "oak", "smoke", "leather", "tobacco", "cedar"],
}

// Price ranges
const priceRanges = [
  { id: "all", name: "All Prices" },
  { id: "budget", name: "Budget ($10-20)" },
  { id: "mid", name: "Mid-Range ($20-50)" },
  { id: "premium", name: "Premium ($50-100)" },
  { id: "luxury", name: "Luxury ($100+)" },
]

// Format trait name for display
const formatTraitName = (trait) => {
  return trait
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

export default function BrowsePage() {
  const { data: session } = useSession()
  const router = useRouter()
  const [wines, setWines] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const [filters, setFilters] = useState({
    category: "all",
    price: "all",
    traits: [],
    minRating: 0,
  })
  const [showFilters, setShowFilters] = useState(false)
  const [expandedCategories, setExpandedCategories] = useState({
    taste: false,
    aroma: false,
    body: false,
    texture: false,
    character: false,
    notes: false,
  })
  const [totalWines, setTotalWines] = useState(0)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [isMobile, setIsMobile] = useState(false)
  const WINES_PER_PAGE = 12

  // Check if we're on the client-side and set mobile state
  useEffect(() => {
    setIsMobile(window.innerWidth < 768)

    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }

    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  // Initialize filters from URL query params on mount
  useEffect(() => {
    if (router.isReady) {
      const { category, price, traits, rating, search, page: pageParam } = router.query

      const initialFilters = {
        category: category || "all",
        price: price || "all",
        traits: traits ? (Array.isArray(traits) ? traits : [traits]) : [],
        minRating: rating ? Number.parseFloat(rating as string) : 0,
      }

      setFilters(initialFilters)
      setSearchQuery((search as string) || "")
      setPage(pageParam ? Number.parseInt(pageParam as string) : 1)
    }
  }, [router.isReady, router.query])

  // Fetch wines when filters or page changes
  useEffect(() => {
    if (router.isReady) {
      fetchWines()
    }
  }, [filters, page, router.isReady])

  const fetchWines = async () => {
    setLoading(true)
    setError("")

    try {
      const result = await wineApi.getWines({
        category: filters.category !== "all" ? filters.category : undefined,
        price: filters.price !== "all" ? filters.price : undefined,
        traits: filters.traits.length > 0 ? filters.traits.join(",") : undefined,
        min_rating: filters.minRating > 0 ? filters.minRating : undefined,
        search: searchQuery || undefined,
        page: page,
        limit: WINES_PER_PAGE,
      })

      if (page === 1) {
        setWines(result.wines || [])
      } else {
        setWines((prev) => [...prev, ...(result.wines || [])])
      }

      setTotalWines(result.total || 0)
      setHasMore((result.wines || []).length === WINES_PER_PAGE)
    } catch (err) {
      setError(err.message || "Failed to fetch wines. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (filterType, value) => {
    if (filterType === "traits") {
      setFilters((prev) => {
        const newTraits = prev.traits.includes(value) ? prev.traits.filter((t) => t !== value) : [...prev.traits, value]
        return { ...prev, traits: newTraits }
      })
    } else {
      setFilters((prev) => ({ ...prev, [filterType]: value }))
    }
  }

  const applyFilters = () => {
    // Update URL with filter params
    router.push(
      {
        pathname: router.pathname,
        query: {
          ...(filters.category !== "all" && { category: filters.category }),
          ...(filters.price !== "all" && { price: filters.price }),
          ...(filters.traits.length > 0 && { traits: filters.traits }),
          ...(filters.minRating > 0 && { rating: filters.minRating }),
          ...(searchQuery && { search: searchQuery }),
          page: 1,
        },
      },
      undefined,
      { shallow: true },
    )

    setPage(1)

    if (isMobile) {
      setShowFilters(false)
    }
  }

  const resetFilters = () => {
    setFilters({
      category: "all",
      price: "all",
      traits: [],
      minRating: 0,
    })
    setSearchQuery("")
    setPage(1)

    router.push(
      {
        pathname: router.pathname,
      },
      undefined,
      { shallow: true },
    )
  }

  const toggleFilters = () => {
    setShowFilters(!showFilters)
  }

  const toggleTraitCategory = (category) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [category]: !prev[category],
    }))
  }

  const loadMore = () => {
    setPage((prev) => prev + 1)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    applyFilters()
  }

  return (
    <Layout title="Browse Wines" description="Explore our extensive wine collection with advanced filtering options">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-serif font-bold text-gray-900 dark:text-white mb-4">Wine Catalog</h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Explore our extensive collection of wines. Use the filters to find wines that match your taste preferences.
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex w-full max-w-2xl mx-auto">
            <div className="relative flex-grow">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search wines by name, winery, or region..."
                className="w-full px-4 py-3 pl-10 border border-gray-300 dark:border-gray-600 rounded-l-md shadow-sm focus:outline-none focus:ring-burgundy-500 focus:border-burgundy-500 dark:bg-gray-800 dark:text-white"
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
            <button
              type="submit"
              className="px-4 py-3 bg-burgundy-600 text-white rounded-r-md hover:bg-burgundy-700 focus:outline-none focus:ring-2 focus:ring-burgundy-500"
            >
              Search
            </button>
          </form>
        </div>

        {/* Mobile filter toggle */}
        <div className="md:hidden mb-6">
          <button
            onClick={toggleFilters}
            className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <SlidersHorizontal className="h-4 w-4 mr-2" />
            {showFilters ? "Hide Filters" : "Show Filters"}
          </button>
        </div>

        <div className="flex flex-col md:flex-row gap-8">
          {/* Filters sidebar */}
          {(showFilters || !isMobile) && (
            <div className="w-full md:w-64 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 md:sticky md:top-24 h-fit">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-medium text-gray-900 dark:text-white">Filters</h2>
                <button
                  onClick={resetFilters}
                  className="text-sm text-burgundy-600 dark:text-burgundy-400 hover:text-burgundy-800 dark:hover:text-burgundy-300"
                >
                  Reset All
                </button>
              </div>

              <div className="space-y-6">
                {/* Wine Category Filter */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Wine Type</h3>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <input
                        id="category-all"
                        name="wine-category"
                        type="radio"
                        checked={filters.category === "all"}
                        onChange={() => handleFilterChange("category", "all")}
                        className="h-4 w-4 text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                      />
                      <label htmlFor="category-all" className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                        All Types
                      </label>
                    </div>

                    {categories.map((category) => (
                      <div key={category.name} className="flex items-center">
                        <input
                          id={`category-${category.name}`}
                          name="wine-category"
                          type="radio"
                          checked={filters.category === category.name}
                          onChange={() => handleFilterChange("category", category.name)}
                          className="h-4 w-4 text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                        />
                        <label
                          htmlFor={`category-${category.name}`}
                          className="ml-3 text-sm text-gray-700 dark:text-gray-300"
                        >
                          {category.name}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Price Range Filter */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Price Range</h3>
                  <div className="space-y-2">
                    {priceRanges.map((range) => (
                      <div key={range.id} className="flex items-center">
                        <input
                          id={`price-${range.id}`}
                          name="price-range"
                          type="radio"
                          checked={filters.price === range.id}
                          onChange={() => handleFilterChange("price", range.id)}
                          className="h-4 w-4 text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                        />
                        <label htmlFor={`price-${range.id}`} className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                          {range.name}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Minimum Rating Filter */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Minimum Rating</h3>
                  <div className="flex items-center">
                    <input
                      type="range"
                      min="0"
                      max="5"
                      step="0.5"
                      value={filters.minRating}
                      onChange={(e) => handleFilterChange("minRating", Number.parseFloat(e.target.value))}
                      className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-burgundy-600"
                    />
                  </div>
                  <div className="mt-2 text-sm text-gray-700 dark:text-gray-300 text-center">
                    {filters.minRating > 0 ? `${filters.minRating} stars and above` : "Any rating"}
                  </div>
                </div>

                {/* Trait Filters */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Wine Characteristics</h3>

                  {/* Taste Traits */}
                  <div className="mb-3 border-b border-gray-200 dark:border-gray-700 pb-3">
                    <button
                      onClick={() => toggleTraitCategory("taste")}
                      className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-burgundy-600 dark:hover:text-burgundy-400"
                    >
                      <span>Taste</span>
                      <ChevronDown
                        className={`h-4 w-4 transition-transform ${expandedCategories.taste ? "rotate-180" : ""}`}
                      />
                    </button>

                    {expandedCategories.taste && (
                      <div className="mt-2 space-y-2 pl-2">
                        {trait_categories.taste.map((trait) => (
                          <div key={trait} className="flex items-center">
                            <input
                              id={`trait-${trait}`}
                              type="checkbox"
                              checked={filters.traits.includes(trait)}
                              onChange={() => handleFilterChange("traits", trait)}
                              className="h-4 w-4 rounded text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                            />
                            <label htmlFor={`trait-${trait}`} className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                              {formatTraitName(trait)}
                            </label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Aroma Traits */}
                  <div className="mb-3 border-b border-gray-200 dark:border-gray-700 pb-3">
                    <button
                      onClick={() => toggleTraitCategory("aroma")}
                      className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-burgundy-600 dark:hover:text-burgundy-400"
                    >
                      <span>Aroma</span>
                      <ChevronDown
                        className={`h-4 w-4 transition-transform ${expandedCategories.aroma ? "rotate-180" : ""}`}
                      />
                    </button>

                    {expandedCategories.aroma && (
                      <div className="mt-2 space-y-2 pl-2">
                        {trait_categories.aroma.map((trait) => (
                          <div key={trait} className="flex items-center">
                            <input
                              id={`trait-${trait}`}
                              type="checkbox"
                              checked={filters.traits.includes(trait)}
                              onChange={() => handleFilterChange("traits", trait)}
                              className="h-4 w-4 rounded text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                            />
                            <label htmlFor={`trait-${trait}`} className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                              {formatTraitName(trait)}
                            </label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Body Traits */}
                  <div className="mb-3 border-b border-gray-200 dark:border-gray-700 pb-3">
                    <button
                      onClick={() => toggleTraitCategory("body")}
                      className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-burgundy-600 dark:hover:text-burgundy-400"
                    >
                      <span>Body</span>
                      <ChevronDown
                        className={`h-4 w-4 transition-transform ${expandedCategories.body ? "rotate-180" : ""}`}
                      />
                    </button>

                    {expandedCategories.body && (
                      <div className="mt-2 space-y-2 pl-2">
                        {trait_categories.body.map((trait) => (
                          <div key={trait} className="flex items-center">
                            <input
                              id={`trait-${trait}`}
                              type="checkbox"
                              checked={filters.traits.includes(trait)}
                              onChange={() => handleFilterChange("traits", trait)}
                              className="h-4 w-4 rounded text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                            />
                            <label htmlFor={`trait-${trait}`} className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                              {formatTraitName(trait)}
                            </label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Texture Traits */}
                  <div className="mb-3 border-b border-gray-200 dark:border-gray-700 pb-3">
                    <button
                      onClick={() => toggleTraitCategory("texture")}
                      className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-burgundy-600 dark:hover:text-burgundy-400"
                    >
                      <span>Texture</span>
                      <ChevronDown
                        className={`h-4 w-4 transition-transform ${expandedCategories.texture ? "rotate-180" : ""}`}
                      />
                    </button>

                    {expandedCategories.texture && (
                      <div className="mt-2 space-y-2 pl-2">
                        {trait_categories.texture.map((trait) => (
                          <div key={trait} className="flex items-center">
                            <input
                              id={`trait-${trait}`}
                              type="checkbox"
                              checked={filters.traits.includes(trait)}
                              onChange={() => handleFilterChange("traits", trait)}
                              className="h-4 w-4 rounded text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                            />
                            <label htmlFor={`trait-${trait}`} className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                              {formatTraitName(trait)}
                            </label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Character Traits */}
                  <div className="mb-3 border-b border-gray-200 dark:border-gray-700 pb-3">
                    <button
                      onClick={() => toggleTraitCategory("character")}
                      className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-burgundy-600 dark:hover:text-burgundy-400"
                    >
                      <span>Character</span>
                      <ChevronDown
                        className={`h-4 w-4 transition-transform ${expandedCategories.character ? "rotate-180" : ""}`}
                      />
                    </button>

                    {expandedCategories.character && (
                      <div className="mt-2 space-y-2 pl-2">
                        {trait_categories.character.map((trait) => (
                          <div key={trait} className="flex items-center">
                            <input
                              id={`trait-${trait}`}
                              type="checkbox"
                              checked={filters.traits.includes(trait)}
                              onChange={() => handleFilterChange("traits", trait)}
                              className="h-4 w-4 rounded text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                            />
                            <label htmlFor={`trait-${trait}`} className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                              {formatTraitName(trait)}
                            </label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Notes Traits */}
                  <div className="mb-3">
                    <button
                      onClick={() => toggleTraitCategory("notes")}
                      className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-burgundy-600 dark:hover:text-burgundy-400"
                    >
                      <span>Notes</span>
                      <ChevronDown
                        className={`h-4 w-4 transition-transform ${expandedCategories.notes ? "rotate-180" : ""}`}
                      />
                    </button>

                    {expandedCategories.notes && (
                      <div className="mt-2 space-y-2 pl-2">
                        {trait_categories.notes.map((trait) => (
                          <div key={trait} className="flex items-center">
                            <input
                              id={`trait-${trait}`}
                              type="checkbox"
                              checked={filters.traits.includes(trait)}
                              onChange={() => handleFilterChange("traits", trait)}
                              className="h-4 w-4 rounded text-burgundy-600 focus:ring-burgundy-500 border-gray-300 dark:border-gray-600"
                            />
                            <label htmlFor={`trait-${trait}`} className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                              {formatTraitName(trait)}
                            </label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <button
                  onClick={applyFilters}
                  className="w-full mt-6 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-burgundy-600 hover:bg-burgundy-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-burgundy-500"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          )}

          {/* Wine listings */}
          <div className="flex-1">
            {/* Active filters */}
            {(filters.category !== "all" ||
              filters.price !== "all" ||
              filters.traits.length > 0 ||
              filters.minRating > 0 ||
              searchQuery) && (
              <div className="mb-6 flex flex-wrap gap-2">
                <span className="text-sm text-gray-700 dark:text-gray-300 mr-2 py-1">Active Filters:</span>

                {searchQuery && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                    Search: {searchQuery}
                    <button
                      onClick={() => {
                        setSearchQuery("")
                        applyFilters()
                      }}
                      className="ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}

                {filters.category !== "all" && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-burgundy-100 text-burgundy-800 dark:bg-burgundy-900/30 dark:text-burgundy-400">
                    {filters.category}
                    <button
                      onClick={() => {
                        handleFilterChange("category", "all")
                        applyFilters()
                      }}
                      className="ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-burgundy-200 dark:hover:bg-burgundy-800"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}

                {filters.price !== "all" && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-burgundy-100 text-burgundy-800 dark:bg-burgundy-900/30 dark:text-burgundy-400">
                    {priceRanges.find((p) => p.id === filters.price)?.name}
                    <button
                      onClick={() => {
                        handleFilterChange("price", "all")
                        applyFilters()
                      }}
                      className="ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-burgundy-200 dark:hover:bg-burgundy-800"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}

                {filters.traits.length > 0 &&
                  filters.traits.map((trait) => (
                    <span
                      key={trait}
                      className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-burgundy-100 text-burgundy-800 dark:bg-burgundy-900/30 dark:text-burgundy-400"
                    >
                      {formatTraitName(trait)}
                      <button
                        onClick={() => {
                          handleFilterChange("traits", trait)
                          applyFilters()
                        }}
                        className="ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-burgundy-200 dark:hover:bg-burgundy-800"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}

                {filters.minRating > 0 && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-burgundy-100 text-burgundy-800 dark:bg-burgundy-900/30 dark:text-burgundy-400">
                    {`${filters.minRating}+ Stars`}
                    <button
                      onClick={() => {
                        handleFilterChange("minRating", 0)
                        applyFilters()
                      }}
                      className="ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center hover:bg-burgundy-200 dark:hover:bg-burgundy-800"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                )}

                <button
                  onClick={() => {
                    resetFilters()
                    applyFilters()
                  }}
                  className="text-xs text-burgundy-600 dark:text-burgundy-400 hover:text-burgundy-800 dark:hover:text-burgundy-300 underline"
                >
                  Clear All
                </button>
              </div>
            )}

            {/* Results count */}
            <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
              {!loading && (
                <p>
                  Showing {wines.length} of {totalWines} wines
                  {filters.category !== "all" ||
                  filters.price !== "all" ||
                  filters.traits.length > 0 ||
                  filters.minRating > 0 ||
                  searchQuery
                    ? " matching your filters"
                    : ""}
                </p>
              )}
            </div>

            {error && (
              <div className="mb-8 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start">
                <AlertCircle className="h-5 w-5 text-red-500 dark:text-red-400 mt-0.5 mr-3 flex-shrink-0" />
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {loading && page === 1 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader className="h-8 w-8 animate-spin text-burgundy-600 dark:text-burgundy-400" />
                <p className="mt-4 text-gray-600 dark:text-gray-400">Loading wines...</p>
              </div>
            ) : wines.length > 0 ? (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {wines.map((wine) => (
                    <WineCard key={wine.id} wine={wine} />
                  ))}
                </div>

                {/* Load more button */}
                {hasMore && (
                  <div className="mt-8 flex justify-center">
                    <button
                      onClick={loadMore}
                      disabled={loading}
                      className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-burgundy-500 disabled:opacity-50"
                    >
                      {loading ? (
                        <>
                          <Loader className="h-4 w-4 animate-spin mr-2 inline" />
                          Loading...
                        </>
                      ) : (
                        "Load More Wines"
                      )}
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Wine className="h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No wines found</h3>
                <p className="text-gray-600 dark:text-gray-400 max-w-md">
                  We couldn't find any wines matching your current filters. Try adjusting your filters or check back
                  later for new additions.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}

