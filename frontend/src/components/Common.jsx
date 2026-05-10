export const LoadingSkeleton = () => (
  <div className="space-y-4">
    {[...Array(5)].map((_, i) => (
      <div key={i} className="bg-gray-200 h-12 rounded animate-pulse"></div>
    ))}
  </div>
)

export const EmptyState = ({ message, icon = '📭' }) => (
  <div className="text-center py-12">
    <div className="text-4xl mb-4">{icon}</div>
    <p className="text-gray-500 text-lg">{message}</p>
  </div>
)

export const StatCard = ({ title, value, icon }) => (
  <div className="bg-white p-6 rounded-lg shadow border-l-4 border-primary">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-600 text-sm">{title}</p>
        <p className="text-3xl font-bold text-primary mt-2">{value}</p>
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
)

export const Badge = ({ status }) => {
  const colors = {
    ACTIVE: 'bg-success text-white',
    PENDING: 'bg-warning text-white',
    COMPLETED: 'bg-blue-500 text-white',
    CRITICAL: 'bg-danger text-white',
    INACTIVE: 'bg-gray-400 text-white'
  }
  
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${colors[status] || 'bg-gray-300'}`}>
      {status}
    </span>
  )
}
