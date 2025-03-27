import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-3.5rem)] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">
            Welcome to WineRecco
          </h1>
          <p className="mt-3 text-xl text-muted-foreground">
            Your personal wine recommendation system
          </p>
        </div>
        <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4 justify-center">
          <Link href="/wines">
            <Button size="lg">
              Browse Wines
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline">
              Get Recommendations
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
} 