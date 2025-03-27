const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'

export async function fetchWines() {
  const response = await fetch(`${API_URL}/wines`)
  if (!response.ok) {
    throw new Error('Failed to fetch wines')
  }
  return response.json()
}

export async function fetchWineById(id: number) {
  const response = await fetch(`${API_URL}/wines/${id}`)
  if (!response.ok) {
    throw new Error('Failed to fetch wine details')
  }
  return response.json()
}

export async function getRecommendations(userId?: number) {
  const response = await fetch(`${API_URL}/recommendations${userId ? `?user_id=${userId}` : ''}`)
  if (!response.ok) {
    throw new Error('Failed to fetch recommendations')
  }
  return response.json()
}

export async function searchWines(query: string) {
  const response = await fetch(`${API_URL}/wines/search?q=${encodeURIComponent(query)}`)
  if (!response.ok) {
    throw new Error('Failed to search wines')
  }
  return response.json()
} 