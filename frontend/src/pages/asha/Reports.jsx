import { useStats, usePatients, useAdherence } from '../../api/patients'
import StatCard from '../../components/StatCard'
import AdherenceBar from '../../components/AdherenceBar'
import Spinner from '../../components/Spinner'
import { format } from 'date-fns'

export default function Reports() {
  const { data: stats,    isLoading } = useStats()
  const { data: patients = [] }        = usePatients()

  if (isLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>

  const today = format(new Date(), 'dd MMM yyyy')

  return (
    <div className="px-4 py-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-800">Health Reports</h2>
        <p className="text-sm text-gray-500">Village summary · {today}</p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <StatCard label="Patients Registered" value={stats?.total_patients ?? 0}      icon="👥" color="green"  />
        <StatCard label="Active Medications"   value={stats?.total_medications ?? 0}  icon="💊" color="blue"   />
        <StatCard label="Visit Records"        value={stats?.total_visits ?? 0}       icon="🏥" color="purple" />
        <StatCard label="Adherence Rate"       value={`${stats?.adherence_percentage ?? 0}%`} icon="📈" color="orange" />
      </div>

      {/* Adherence gauge */}
      <div className="card mb-4">
        <h3 className="font-semibold text-gray-700 mb-3">Medication Compliance</h3>
        <AdherenceBar pct={stats?.adherence_percentage ?? 0} label="Overall village adherence" />
        <div className="mt-3 grid grid-cols-3 text-center gap-2">
          <div className="bg-green-50 rounded-xl py-2">
            <div className="text-lg font-bold text-green-700">
              {stats?.adherence_percentage >= 80 ? '✅' : stats?.adherence_percentage >= 50 ? '⚠️' : '🚨'}
            </div>
            <div className="text-xs text-gray-500">Status</div>
          </div>
          <div className="bg-blue-50 rounded-xl py-2">
            <div className="text-lg font-bold text-blue-700">{stats?.total_patients ?? 0}</div>
            <div className="text-xs text-gray-500">Patients</div>
          </div>
          <div className="bg-purple-50 rounded-xl py-2">
            <div className="text-lg font-bold text-purple-700">{stats?.total_medications ?? 0}</div>
            <div className="text-xs text-gray-500">Medicines</div>
          </div>
        </div>
      </div>

      {/* Patient list summary */}
      <div className="card">
        <h3 className="font-semibold text-gray-700 mb-3">Patient Summary</h3>
        <div className="flex flex-col gap-2">
          {patients.slice(0, 10).map(p => (
            <div key={p.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
              <div>
                <div className="text-sm font-medium text-gray-800">{p.name}</div>
                <div className="text-xs text-gray-400">{p.village} · {p.age}y</div>
              </div>
              <span className="text-xs text-gray-400">{p.conditions || 'No conditions listed'}</span>
            </div>
          ))}
          {patients.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-4">No patients registered yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
