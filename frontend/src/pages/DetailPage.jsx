import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { auditService, aiService } from '../services/api'
import { Badge, LoadingSkeleton } from '../components/Common'
import { ArrowLeft, Loader } from 'lucide-react'

export const DetailPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [audit, setAudit] = useState(null)
  const [loading, setLoading] = useState(true)
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    fetchAudit()
  }, [id])

  const fetchAudit = async () => {
    try {
      const { data } = await auditService.getById(id)
      setAudit(data)
    } catch (error) {
      console.error('Failed to fetch audit:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      const { data } = await aiService.describe(audit?.description || '')
      setAiAnalysis(data)
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure?')) {
      try {
        await auditService.delete(id)
        navigate('/audits')
      } catch (error) {
        console.error('Delete failed:', error)
      }
    }
  }

  if (loading) return <LoadingSkeleton />

  if (!audit) return <div className="p-4">Audit not found</div>

  return (
    <div className="max-w-4xl mx-auto p-4">
      <button
        onClick={() => navigate('/audits')}
        className="flex items-center gap-2 text-primary hover:underline mb-6"
      >
        <ArrowLeft size={20} />
        Back to Audits
      </button>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              {audit?.title || 'Audit'}
            </h1>
            <Badge status={audit?.status || 'PENDING'} />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate(`/audits/${id}/edit`)}
              className="bg-primary text-white px-4 py-2 rounded hover:bg-secondary"
            >
              Edit
            </button>
            <button
              onClick={handleDelete}
              className="bg-danger text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="font-semibold text-gray-700 mb-2">Description</h3>
            <p className="text-gray-600">{audit?.description}</p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-700 mb-2">Details</h3>
            <div className="space-y-2 text-sm">
              <p><span className="font-semibold">Created:</span> {new Date(audit?.createdDate).toLocaleDateString()}</p>
              <p><span className="font-semibold">Score:</span> {audit?.score || 'N/A'}/10</p>
              <p><span className="font-semibold">Category:</span> {audit?.category || 'N/A'}</p>
            </div>
          </div>
        </div>

        <div className="border-t pt-6">
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded hover:bg-secondary disabled:opacity-50"
          >
            {analyzing ? <Loader className="animate-spin" /> : '🤖'}
            {analyzing ? 'Analyzing...' : 'AI Analysis'}
          </button>

          {aiAnalysis && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
              <h3 className="font-semibold text-blue-900 mb-2">AI Analysis</h3>
              <p className="text-blue-800">{aiAnalysis?.generated_text || 'Analysis completed'}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
