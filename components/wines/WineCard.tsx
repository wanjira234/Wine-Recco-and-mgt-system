import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface WineCardProps {
  id: number
  name: string
  type: string
  price: number
  rating: number
  imageUrl?: string
}

export default function WineCard({ id, name, type, price, rating, imageUrl }: WineCardProps) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="p-0">
        <div className="relative h-48 w-full">
          <Image
            src={imageUrl || '/placeholder-wine.jpg'}
            alt={name}
            fill
            className="object-cover"
          />
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <CardTitle className="text-lg mb-2">{name}</CardTitle>
        <div className="text-sm text-muted-foreground">
          <p>{type}</p>
          <p className="font-medium">${price}</p>
          <div className="flex items-center mt-1">
            <span className="text-yellow-400">★</span>
            <span className="ml-1">{rating}/5</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <Link href={`/wines/${id}`} className="w-full">
          <Button className="w-full">View Details</Button>
        </Link>
      </CardFooter>
    </Card>
  )
} 