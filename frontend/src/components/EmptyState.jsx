export default function EmptyState({ icon = '📭', title, message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="text-5xl mb-4">{icon}</div>
      {title && <div className="font-semibold text-gray-700 mb-1">{title}</div>}
      {message && <div className="text-sm text-gray-400">{message}</div>}
    </div>
  )
}
