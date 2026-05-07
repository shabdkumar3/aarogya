export default function StatCard({ label, value, icon, color = 'green' }) {
  const colors = {
    green:  'bg-primary-50 text-primary-600',
    orange: 'bg-amber-50 text-accent-500',
    blue:   'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
  }
  return (
    <div className="card flex flex-col items-center justify-center text-center gap-1 py-5">
      <div className={`text-3xl mb-1 rounded-xl w-12 h-12 flex items-center justify-center ${colors[color]}`}>
        {icon}
      </div>
      <div className="text-2xl font-bold text-gray-800">{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  )
}
