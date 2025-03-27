import React from 'react';
import { Wine, TrendingUp, Package, DollarSign } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="p-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border p-4">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-blue-100 p-2">
              <Wine className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Total Wines</p>
              <p className="text-2xl font-bold">1,234</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-green-100 p-2">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Recommendations</p>
              <p className="text-2xl font-bold">89</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-purple-100 p-2">
              <Package className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Inventory</p>
              <p className="text-2xl font-bold">567</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border p-4">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-yellow-100 p-2">
              <DollarSign className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Revenue</p>
              <p className="text-2xl font-bold">$12,345</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border p-6">
          <h2 className="text-lg font-semibold">Recent Wines</h2>
          <div className="mt-4 space-y-4">
            {[1, 2, 3].map((wine) => (
              <div key={wine} className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gray-200" />
                <div className="flex-1">
                  <h3 className="font-medium">Wine Name {wine}</h3>
                  <p className="text-sm text-gray-500">Region • Varietal</p>
                </div>
                <button className="rounded-full bg-gray-100 p-2 hover:bg-gray-200">
                  <span className="sr-only">View details</span>
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border p-6">
          <h2 className="text-lg font-semibold">Popular Recommendations</h2>
          <div className="mt-4 space-y-4">
            {[1, 2, 3].map((rec) => (
              <div key={rec} className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gray-200" />
                <div className="flex-1">
                  <h3 className="font-medium">Recommendation {rec}</h3>
                  <p className="text-sm text-gray-500">Based on preferences</p>
                </div>
                <button className="rounded-full bg-gray-100 p-2 hover:bg-gray-200">
                  <span className="sr-only">View details</span>
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 