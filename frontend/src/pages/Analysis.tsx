import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { createAnalysis, getAnalysis } from '../services/api'
import { BarChart3, Lightbulb, TrendingUp, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Analysis() {
  const [analysisType, setAnalysisType] = useState('overall')
  const [keywords, setKeywords] = useState('')
  const [competitors, setCompetitors] = useState('')
  const [result, setResult] = useState<any>(null)

  const analysisMutation = useMutation({
    mutationFn: createAnalysis,
    onSuccess: async (data) => {
      toast.success('Analysis started!')
      // Poll for results
      const pollInterval = setInterval(async () => {
        try {
          const analysis = await getAnalysis(data.id)
          if (analysis.status === 'completed') {
            setResult(analysis)
            clearInterval(pollInterval)
            toast.success('Analysis completed!')
          } else if (analysis.status === 'failed') {
            clearInterval(pollInterval)
            toast.error('Analysis failed')
          }
        } catch (error) {
          clearInterval(pollInterval)
          toast.error('Error fetching analysis results')
        }
      }, 2000)
    },
    onError: () => {
      toast.error('Failed to start analysis')
    },
  })

  const handleAnalyze = () => {
    const analysisData: any = {
      analysis_type: analysisType,
    }

    if (keywords) {
      analysisData.keywords = keywords.split(',').map((k) => k.trim())
    }

    if (competitors) {
      analysisData.competitors = competitors.split(',').map((c) => c.trim())
    }

    analysisMutation.mutate(analysisData)
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }
  }

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'pattern':
        return TrendingUp
      case 'recommendation':
        return Lightbulb
      case 'gap':
        return AlertCircle
      default:
        return BarChart3
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI Analysis
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Get AI-powered insights from your ad data
        </p>
      </div>

      {/* Analysis Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Run New Analysis
        </h2>

        <div className="space-y-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Analysis Type
            </label>
            <select
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              className="input"
            >
              <option value="overall">Overall Analysis</option>
              <option value="keyword">Keyword Analysis</option>
              <option value="competitor">Competitor Analysis</option>
              <option value="timerange">Time Range Analysis</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Keywords (comma-separated)
            </label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="e.g., running shoes, nike shoes, athletic footwear"
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Competitors (comma-separated)
            </label>
            <input
              type="text"
              value={competitors}
              onChange={(e) => setCompetitors(e.target.value)}
              placeholder="e.g., nike.com, adidas.com"
              className="input"
            />
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={analysisMutation.isPending}
          className="btn btn-primary flex items-center gap-2"
        >
          <BarChart3 size={20} />
          {analysisMutation.isPending ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Analysis Summary
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Ads Analyzed
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {result.total_ads_analyzed || 0}
                </p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Headlines Analyzed
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {result.total_headlines_analyzed || 0}
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Insights Found
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {result.insights?.length || 0}
                </p>
              </div>
            </div>

            {result.summary && (
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-gray-700 dark:text-gray-300">{result.summary}</p>
              </div>
            )}
          </div>

          {/* Insights */}
          {result.insights && result.insights.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Insights
              </h2>

              <div className="space-y-4">
                {result.insights.map((insight: any) => {
                  const Icon = getInsightIcon(insight.insight_type)
                  return (
                    <div
                      key={insight.id}
                      className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <div className="flex-shrink-0 p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                          <Icon className="text-primary-600 dark:text-primary-300" size={20} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-bold text-gray-900 dark:text-white">
                              {insight.title}
                            </h3>
                            <span
                              className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(
                                insight.priority
                              )}`}
                            >
                              {insight.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {insight.description}
                          </p>

                          {insight.examples && insight.examples.length > 0 && (
                            <div className="mb-2">
                              <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Examples:
                              </p>
                              <div className="space-y-1">
                                {insight.examples.slice(0, 3).map((example: string, idx: number) => (
                                  <p
                                    key={idx}
                                    className="text-xs text-gray-600 dark:text-gray-400 pl-3 border-l-2 border-gray-200 dark:border-gray-600"
                                  >
                                    {example}
                                  </p>
                                ))}
                              </div>
                            </div>
                          )}

                          {insight.recommendations && insight.recommendations.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Recommendations:
                              </p>
                              <ul className="space-y-1">
                                {insight.recommendations.map((rec: string, idx: number) => (
                                  <li
                                    key={idx}
                                    className="text-xs text-gray-600 dark:text-gray-400 flex gap-2"
                                  >
                                    <span>•</span>
                                    <span>{rec}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
