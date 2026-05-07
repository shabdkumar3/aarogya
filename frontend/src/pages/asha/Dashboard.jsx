import { useStats } from '../../api/patients'
import StatCard from '../../components/StatCard'
import AdherenceBar from '../../components/AdherenceBar'
import Spinner from '../../components/Spinner'

export default function Dashboard() {
  const { data: stats, isLoading } = useStats()

  return (
    <div className="px-4 py-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-800">Dashboard</h2>
        <p className="text-sm text-gray-500">Village health overview</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3 mb-6">
            <StatCard label="Total Patients" value={stats?.total_patients ?? 0}    icon="👥" color="green"  />
            <StatCard label="Medications"    value={stats?.total_medications ?? 0} icon="💊" color="blue"   />
            <StatCard label="Adherence"      value={`${stats?.adherence_percentage ?? 0}%`} icon="✅" color="orange" />
            <StatCard label="Visits"         value={stats?.total_visits ?? 0}      icon="🏥" color="purple" />
          </div>

          <div className="card mb-4">
            <h3 className="font-semibold text-gray-700 mb-3">Overall Adherence</h3>
            <AdherenceBar pct={stats?.adherence_percentage ?? 0} label="Medication compliance" />
            <p className="text-xs text-gray-400 mt-3">
              {stats?.adherence_percentage >= 80
                ? '✅ Excellent compliance rate — keep it up!'
                : stats?.adherence_percentage >= 50
                ? '⚠️ Moderate compliance — follow up with patients'
                : '🚨 Low compliance — urgent outreach needed'}
            </p>
          </div>

          <div className="card">
            <h3 className="font-semibold text-gray-700 mb-3">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: '👤', label: 'Register Patient', href: '/asha/patients' },
                { icon: '🔬', label: 'Run DiagnoScan',   href: '/asha/diagnoscan' },
                { icon: '💊', label: 'Add Medication',   href: '/asha/medtrack'   },
                { icon: '📋', label: 'View Reports',     href: '/asha/reports'    },
              ].map(({ icon, label, href }) => (
                <a key={label} href={href}
                   className="flex flex-col items-center justify-center gap-2 py-4 bg-surface-100
                              rounded-xl text-sm font-medium text-gray-700 hover:bg-primary-50
                              hover:text-primary-700 transition-colors">
                  <span className="text-2xl">{icon}</span>
                  <span>{label}</span>
                </a>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
