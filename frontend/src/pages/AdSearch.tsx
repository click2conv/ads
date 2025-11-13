import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchAds } from '../services/api'
import { Search, Filter } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AdSearch() {
  const [keyword, setKeyword] = useState('')
  const [location, setLocation] = useState('')
  const [deviceType, setDeviceType] = useState('desktop')
  const [advertiser, setAdvertiser] = useState('')

  const { data, refetch, isLoading } = useQuery({
    queryKey: ['adSearch', keyword, location, deviceType, advertiser],
    queryFn: () =>
      searchAds({
        keyword: keyword || undefined,
        location: location || undefined,
        device_type: deviceType || undefined,
        advertiser: advertiser || undefined,
        limit: 50,
      }),
    enabled: false,
  })

  const handleSearch = () => {
    if (!keyword && !advertiser) {
      toast.error('Please enter a keyword or advertiser')
      return
    }
    refetch()
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Ad Search
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Search and browse captured ad data
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Keyword
            </label>
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="e.g., running shoes"
              className="input"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Location
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., United States"
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Device Type
            </label>
            <select
              value={deviceType}
              onChange={(e) => setDeviceType(e.target.value)}
              className="input"
            >
              <option value="desktop">Desktop</option>
              <option value="mobile">Mobile</option>
              <option value="tablet">Tablet</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Advertiser
            </label>
            <input
              type="text"
              value={advertiser}
              onChange={(e) => setAdvertiser(e.target.value)}
              placeholder="e.g., nike.com"
              className="input"
            />
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="btn btn-primary flex items-center gap-2"
        >
          <Search size={20} />
          {isLoading ? 'Searching...' : 'Search Ads'}
        </button>
      </div>

      {/* Results */}
      {data && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Search Results
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Found {data.total} ads
            </p>
          </div>

          <div className="space-y-4">
            {data.ads && data.ads.length > 0 ? (
              data.ads.map((ad: any) => (
                <div
                  key={ad.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {ad.advertiser_name || ad.advertiser_domain || 'Unknown'}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Keyword: {ad.keyword}
                      </p>
                    </div>
                    <span className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                      Position {ad.ad_position || 'N/A'}
                    </span>
                  </div>

                  {ad.headlines && ad.headlines.length > 0 && (
                    <div className="mb-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Headlines:
                      </p>
                      <div className="space-y-1">
                        {ad.headlines.map((h: any, idx: number) => (
                          <p
                            key={idx}
                            className="text-sm text-gray-600 dark:text-gray-400"
                          >
                            • {h.headline_text}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  {ad.descriptions && ad.descriptions.length > 0 && (
                    <div className="mb-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Descriptions:
                      </p>
                      <div className="space-y-1">
                        {ad.descriptions.map((d: any, idx: number) => (
                          <p
                            key={idx}
                            className="text-sm text-gray-600 dark:text-gray-400"
                          >
                            • {d.description_text}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex gap-4 mt-3 text-xs text-gray-500 dark:text-gray-400">
                    {ad.display_url && <span>URL: {ad.display_url}</span>}
                    {ad.captured_at && (
                      <span>
                        Captured: {new Date(ad.captured_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                No ads found. Try adjusting your search criteria.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
