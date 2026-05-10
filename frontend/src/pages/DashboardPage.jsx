import { useState, useEffect } from 'react'
import { auditService } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { StatCard, LoadingSkeleton } from '../components/Common'

export const DashboardPage = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [chartData, setChartData] = useState([])

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const { data } = await auditService.getStats()
      setStats(data)
      
      // Process data for chart
      if (data.byStatus) {
        setChartData(Object.entries(data.byStatus).map(([key, value]) => ({
          name: key,
          count: value
        })))
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSkeleton />

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Dashboard</h1>

      <div className="grid md:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Audits" value={stats?.totalAudits || 0} icon="📊" />
        <StatCard title="Active" value={stats?.activeCount || 0} icon="✅" />
        <StatCard title="Pending" value={stats?.pendingCount || 0} icon="⏳" />
        <StatCard title="Avg Score" value={stats?.averageScore?.toFixed(1) || 'N/A'} icon="⭐" />
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Audits by Status</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#1B4F8A" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-500">No data available</p>
        )}
      </div>
    </div>
  )
}
