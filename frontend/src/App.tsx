import { Routes, Route, Link, useLocation } from 'react-router-dom'
import {
  BarChart3,
  Search,
  Tags,
  MessageSquare,
  Settings,
  Home
} from 'lucide-react'

// Pages
import Dashboard from './pages/Dashboard'
import AdSearch from './pages/AdSearch'
import Keywords from './pages/Keywords'
import Analysis from './pages/Analysis'
import Chat from './pages/Chat'

function App() {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: 'Ad Search', path: '/search', icon: Search },
    { name: 'Keywords', path: '/keywords', icon: Tags },
    { name: 'Analysis', path: '/analysis', icon: BarChart3 },
    { name: 'Chat', path: '/chat', icon: MessageSquare },
  ]

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-primary-600">PPC Analysis</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Google Ads Tool</p>
        </div>

        <nav className="px-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                  ${
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }
                `}
              >
                <Icon size={20} />
                <span className="font-medium">{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/search" element={<AdSearch />} />
          <Route path="/keywords" element={<Keywords />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
