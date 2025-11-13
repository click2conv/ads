import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getKeywords, createKeyword, deleteKeyword, updateKeyword } from '../services/api'
import { Plus, Trash2, Edit, Play, Pause } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Keywords() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [newKeyword, setNewKeyword] = useState({
    keyword_text: '',
    location: '',
    device_type: 'desktop',
    check_interval_hours: 1,
    notes: '',
  })

  const { data: keywordsData, isLoading } = useQuery({
    queryKey: ['keywords'],
    queryFn: () => getKeywords(true),
  })

  const createMutation = useMutation({
    mutationFn: createKeyword,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      toast.success('Keyword added successfully')
      setShowAddForm(false)
      setNewKeyword({
        keyword_text: '',
        location: '',
        device_type: 'desktop',
        check_interval_hours: 1,
        notes: '',
      })
    },
    onError: () => {
      toast.error('Failed to add keyword')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteKeyword,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      toast.success('Keyword deleted')
    },
    onError: () => {
      toast.error('Failed to delete keyword')
    },
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      updateKeyword(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })

  const handleAddKeyword = () => {
    if (!newKeyword.keyword_text) {
      toast.error('Please enter a keyword')
      return
    }
    createMutation.mutate(newKeyword)
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Keywords
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage keywords for automated monitoring
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Add Keyword
        </button>
      </div>

      {/* Add Keyword Form */}
      {showAddForm && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Add New Keyword
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Keyword *
              </label>
              <input
                type="text"
                value={newKeyword.keyword_text}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, keyword_text: e.target.value })
                }
                placeholder="e.g., running shoes"
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Location
              </label>
              <input
                type="text"
                value={newKeyword.location}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, location: e.target.value })
                }
                placeholder="e.g., United States"
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Device Type
              </label>
              <select
                value={newKeyword.device_type}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, device_type: e.target.value })
                }
                className="input"
              >
                <option value="desktop">Desktop</option>
                <option value="mobile">Mobile</option>
                <option value="tablet">Tablet</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Check Interval (hours)
              </label>
              <input
                type="number"
                min="1"
                max="168"
                value={newKeyword.check_interval_hours}
                onChange={(e) =>
                  setNewKeyword({
                    ...newKeyword,
                    check_interval_hours: parseInt(e.target.value),
                  })
                }
                className="input"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Notes
              </label>
              <textarea
                value={newKeyword.notes}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, notes: e.target.value })
                }
                placeholder="Optional notes..."
                className="input"
                rows={3}
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleAddKeyword}
              disabled={createMutation.isPending}
              className="btn btn-primary"
            >
              {createMutation.isPending ? 'Adding...' : 'Add Keyword'}
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Keywords List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            Loading keywords...
          </div>
        ) : keywordsData?.keywords && keywordsData.keywords.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Keyword
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Device
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Interval
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Stats
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {keywordsData.keywords.map((keyword: any) => (
                  <tr key={keyword.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">
                          {keyword.keyword_text}
                        </div>
                        {keyword.notes && (
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {keyword.notes}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                      {keyword.location || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                      {keyword.device_type}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                      Every {keyword.check_interval_hours}h
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                      <div>{keyword.total_checks} checks</div>
                      <div>{keyword.total_ads_found} ads found</div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          keyword.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                      >
                        {keyword.is_active ? 'Active' : 'Paused'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() =>
                            toggleMutation.mutate({
                              id: keyword.id,
                              is_active: !keyword.is_active,
                            })
                          }
                          className="text-primary-600 hover:text-primary-800"
                          title={keyword.is_active ? 'Pause' : 'Resume'}
                        >
                          {keyword.is_active ? <Pause size={18} /> : <Play size={18} />}
                        </button>
                        <button
                          onClick={() => {
                            if (
                              confirm(
                                'Are you sure you want to delete this keyword?'
                              )
                            ) {
                              deleteMutation.mutate(keyword.id)
                            }
                          }}
                          className="text-red-600 hover:text-red-800"
                          title="Delete"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              No keywords yet. Add your first keyword to start monitoring.
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn btn-primary"
            >
              Add Keyword
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
