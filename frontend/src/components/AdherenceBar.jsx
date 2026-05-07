import clsx from 'clsx'

export default function AdherenceBar({ pct = 0, label }) {
  const color = pct >= 80 ? 'bg-primary-500' : pct >= 50 ? 'bg-amber-400' : 'bg-red-400'
  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{label}</span>
          <span className="font-semibold">{pct}%</span>
        </div>
      )}
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-700', color)}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  )
}
