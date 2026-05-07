import { useState } from 'react'
import { usePatients, useVisits } from '../../api/patients'
import Spinner from '../../components/Spinner'
import EmptyState from '../../components/EmptyState'
import useAppStore from '../../store/useAppStore'
import { format } from 'date-fns'

export default function PatientHome() {
  const { data: patients = [], isLoading } = usePatients()
  const selfId   = useAppStore(s => s.selfPatientId)
  const setSelf  = useAppStore(s => s.setSelfPatientId)
  const [search, setSearch] = useState('')

  const me = patients.find(p => p.id === selfId)
  const { data: visits = [] } = useVisits(selfId)

  if (isLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>

  // Not selected yet — show search
  if (!me) {
    const filtered = patients.filter(p =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.village.toLowerCase().includes(search.toLowerCase())
    )
    return (
      <div className="px-4 py-6">
        <div className="mb-6 text-center">
          <div className="text-4xl mb-2">🌿</div>
          <h2 className="text-xl font-bold text-gray-800">Find Your Profile</h2>
          <p className="text-sm text-gray-500">Search by name or village</p>
        </div>
        <input className="input mb-4" placeholder="Your name or village…"
          value={search} onChange={e => setSearch(e.target.value)} />
        <div className="flex flex-col gap-3">
          {filtered.map(p => (
            <button key={p.id} onClick={() => setSelf(p.id)}
              className="card text-left hover:shadow-card-hover active:scale-[0.98] transition-all">
              <div className="font-semibold text-gray-800">{p.name}</div>
              <div className="text-xs text-gray-500">{p.age}y · {p.gender} · {p.village}</div>
              {p.conditions && <div className="text-xs text-gray-400 mt-1">{p.conditions}</div>}
            </button>
          ))}
          {filtered.length === 0 && search && (
            <EmptyState icon="🔍" title="No results" message="Ask your ASHA worker to register you" />
          )}
        </div>
      </div>
    )
  }

  // Profile found
  return (
    <div className="px-4 py-6">
      {/* Profile card */}
      <div className="bg-gradient-to-br from-accent-500 to-accent-600 text-white rounded-2xl p-5 mb-5 shadow-card-hover">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center text-2xl font-bold">
            {me.name[0]}
          </div>
          <div>
            <div className="text-xl font-bold">{me.name}</div>
            <div className="text-orange-100 text-sm">{me.age}y · {me.gender} · {me.village}</div>
          </div>
        </div>
        {me.conditions && (
          <div className="bg-white/20 rounded-xl px-3 py-2 text-sm">
            📋 {me.conditions}
          </div>
        )}
      </div>

      {/* Recent visits */}
      <div className="card">
        <h3 className="font-semibold text-gray-700 mb-3">Recent Visits</h3>
        {visits.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">No visits recorded yet</p>
        ) : (
          <div className="flex flex-col gap-2">
            {visits.slice(0, 5).map((v, i) => (
              <div key={i} className="border-b border-gray-50 pb-2 last:border-0 last:pb-0">
                <div className="text-xs text-gray-400">{v.date}</div>
                <div className="text-sm text-gray-700 mt-0.5">{v.notes}</div>
                {v.vitals && <div className="text-xs text-gray-400 mt-0.5">Vitals: {v.vitals}</div>}
              </div>
            ))}
          </div>
        )}
      </div>

      <button onClick={() => setSelf(null)}
        className="mt-4 text-center w-full text-sm text-gray-400 hover:text-gray-600">
        Switch profile
      </button>
    </div>
  )
}
