import clsx from 'clsx'
import { ChevronRight } from 'lucide-react'

const URGENCY = {
  urgent:   { label: 'Urgent',   cls: 'badge-urgent'   },
  moderate: { label: 'Moderate', cls: 'badge-moderate' },
  stable:   { label: 'Stable',   cls: 'badge-stable'   },
}

export default function PatientCard({ patient, onClick, urgency = 'stable' }) {
  const u = URGENCY[urgency] || URGENCY.stable
  return (
    <button
      onClick={onClick}
      className="card w-full text-left flex items-center gap-4 hover:shadow-card-hover
                 active:scale-[0.98] transition-all cursor-pointer"
    >
      {/* Avatar */}
      <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center
                      text-primary-700 font-bold text-lg flex-shrink-0">
        {patient.name?.[0]?.toUpperCase() ?? '?'}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-gray-800 truncate">{patient.name}</span>
          <span className={clsx('flex-shrink-0', u.cls)}>{u.label}</span>
        </div>
        <div className="text-xs text-gray-500 mt-0.5">
          {patient.age}y · {patient.gender} · {patient.village}
        </div>
        {patient.conditions && (
          <div className="text-xs text-gray-400 truncate mt-0.5">{patient.conditions}</div>
        )}
      </div>

      <ChevronRight size={18} className="text-gray-300 flex-shrink-0" />
    </button>
  )
}
