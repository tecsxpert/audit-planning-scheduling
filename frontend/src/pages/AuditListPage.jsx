import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { auditService } from '../services/api'
import { LoadingSkeleton, EmptyState, Badge } from '../components/Common'
import { Plus, Download, Search } from 'lucide-react'

export const AuditListPage = () => {
  const [audits, setAudits] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [totalPages, setTotalPages] = useState(0)

  useEffect(() => {
    fetchAudits()
  }, [page, search, status])

  const fetchAudits = async () => {
    setLoading(true)
    try {
      let data
      if (search) {
        const { data: searchData } = await auditService.search(search)
        data = searchData
      } else {
        const { data: listData } = await auditService.getAll(page, 10)
        data = listData
      }
      
      setAudits(data.content || data)
      setTotalPages(data.totalPages || 1)
    } catch (error) {
      console.error('Failed to fetch audits:', error)
      setAudits([])
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      const blob = await auditService.export('csv')
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'audits.csv'
      a.click()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Audits</h1>
        <Link to="/audits/new" className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded hover:bg-secondary">
          <Plus size={20} />
          New Audit
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search audits..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(0)
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value)
              setPage(0)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="PENDING">Pending</option>
            <option value="COMPLETED">Completed</option>
          </select>
          <button
            onClick={handleExport}
            className="flex items-center gap-2 bg-success text-white px-4 py-2 rounded hover:bg-green-600"
          >
            <Download size={20} />
            Export
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton />
      ) : audits.length === 0 ? (
        <EmptyState message="No audits found" icon="🔍" />
      ) : (
        <div className="bg-white rounded-lg shadow-lg overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-100 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Title</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Score</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {audits.map((audit) => (
                <tr key={audit.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-3">{audit.title}</td>
                  <td className="px-6 py-3">
                    <Badge status={audit.status} />
                  </td>
                  <td className="px-6 py-3">{audit.score || 'N/A'}/10</td>
                  <td className="px-6 py-3 text-sm text-gray-600">
                    {new Date(audit.createdDate).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-3">
                    <Link
                      to={`/audits/${audit.id}`}
                      className="text-primary hover:underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex justify-center gap-2 mt-6">
        <button
          onClick={() => setPage(Math.max(0, page - 1))}
          disabled={page === 0}
          className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
        >
          Previous
        </button>
        <span className="px-4 py-2 bg-gray-100 rounded">
          Page {page + 1} of {totalPages}
        </span>
        <button
          onClick={() => setPage(page + 1)}
          disabled={page >= totalPages - 1}
          className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  )
}
