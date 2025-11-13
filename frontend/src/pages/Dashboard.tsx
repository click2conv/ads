import { useQuery } from '@tanstack/react-query'
import { getAdStats, getKeywords } from '../services/api'
import { BarChart3, Search, Tags, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['adStats'],
    queryFn: getAdStats,
  })

  const { data: keywordsData } = useQuery({
    queryKey: ['keywords'],
    queryFn: () => getKeywords(true),
  })

  const statCards = [
    {
      title: 'Total Ads Captured',
      value: stats?.total_ads || 0,
      icon: Search,
      color: 'bg-blue-500',
    },
    {
      title: 'Active Keywords',
      value: keywordsData?.total || 0,
      icon: Tags,
      color: 'bg-green-500',
    },
    {
      title: 'Unique Advertisers',
      value: stats?.unique_advertisers || 0,
      icon: TrendingUp,
      color: 'bg-purple-500',
    },
    {
      title: 'Keywords Tracked',
      value: stats?.unique_keywords || 0,
      icon: BarChart3,
      color: 'bg-orange-500',
    },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Overview of your PPC competitive analysis
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <div
              key={card.title}
              className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`${card.color} p-3 rounded-lg`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">
                  {card.title}
                </p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {card.value.toLocaleString()}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h2>
          <div className="space-y-3">
            <a
              href="/search"
              className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Search size={20} className="text-primary-600" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    Search Ads
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Manually search for competitor ads
                  </p>
                </div>
              </div>
            </a>

            <a
              href="/keywords"
              className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Tags size={20} className="text-primary-600" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    Manage Keywords
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Add or edit monitored keywords
                  </p>
                </div>
              </div>
            </a>

            <a
              href="/analysis"
              className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <BarChart3 size={20} className="text-primary-600" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    Run Analysis
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Get AI-powered insights
                  </p>
                </div>
              </div>
            </a>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Getting Started
          </h2>
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <span className="text-primary-600 dark:text-primary-300 font-bold">
                  1
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  Add Keywords
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Start by adding keywords you want to monitor
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <span className="text-primary-600 dark:text-primary-300 font-bold">
                  2
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  Collect Ad Data
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Search or let automated monitoring collect ads
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <span className="text-primary-600 dark:text-primary-300 font-bold">
                  3
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  Analyze & Chat
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Use AI to analyze patterns and get insights
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
