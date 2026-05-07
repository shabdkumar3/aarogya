import { useMedications, useAdherence, useLogAdherence } from '../../api/patients'
import AdherenceBar from '../../components/AdherenceBar'
import Spinner from '../../components/Spinner'
import EmptyState from '../../components/EmptyState'
import useAppStore from '../../store/useAppStore'
import { Check, X } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function PatientMeds() {
  const selfId = useAppStore(s => s.selfPatientId)
  const { data: meds = [],  isLoading } = useMedications(selfId)
  const { data: adh  = [] }              = useAdherence(selfId)
  const logAdh = useLogAdherence()
  const today  = format(new Date(), 'yyyy-MM-dd')

  const took   = adh.filter(a => a.status === 'Took').length
  const adhPct = adh.length ? Math.round((took / adh.length) * 100) : 0
  const todayLogs = adh.filter(a => a.date === today)

  const log = async (medId, status) => {
    if (!selfId) return
    try {
      await logAdh.mutateAsync({ medication_id: medId, patient_id: selfId, date: today, status })
      toast.success(status === 'Took' ? '✅ Great! Medicine recorded' : '⚠️ Missed dose recorded')
    } catch { toast.error('Could not save') }
  }

  if (!selfId) return <EmptyState icon="👤" title="Profile not selected" message="Go to Home and select your profile first" />
  if (isLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  if (meds.length === 0) return <EmptyState icon="💊" title="No medications" message="Your ASHA worker will add your medicines" />

  return (
    <div className="px-4 py-6">
      <div className="mb-5">
        <h2 className="text-xl font-bold text-gray-800">My Medicines</h2>
        <p className="text-sm text-gray-500">{format(new Date(), 'EEEE, dd MMM yyyy')}</p>
      </div>

      {/* Adherence */}
      <div className="card mb-5">
        <div className="flex justify-between mb-2">
          <span className="font-semibold text-gray-700">My Adherence</span>
          <span className="font-bold text-primary-600">{adhPct}%</span>
        </div>
        <AdherenceBar pct={adhPct} />
        <p className="text-xs text-gray-400 mt-2">
          {adhPct >= 80 ? '🌟 Excellent! Keep taking your medicines regularly.'
           : adhPct >= 50 ? '⚠️ Try not to miss your medicines.'
           : '🚨 Please take your medicines regularly. Talk to your ASHA worker.'}
        </p>
      </div>

      {/* Today check-in */}
      <h3 className="font-semibold text-gray-700 mb-3">Today's Medicines</h3>
      <div className="flex flex-col gap-3">
        {meds.map(med => {
          const logged = todayLogs.find(a => a.medication_id === med.id)
          return (
            <div key={med.id} className="card flex items-center gap-4">
              <div className="text-3xl">💊</div>
              <div className="flex-1">
                <div className="font-semibold text-gray-800">{med.name}</div>
                <div className="text-xs text-gray-500">{med.dose} · {med.frequency}</div>
              </div>
              {logged ? (
                <span className={`text-sm font-semibold px-3 py-1.5 rounded-xl ${logged.status === 'Took' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {logged.status === 'Took' ? '✅ Took' : '❌ Missed'}
                </span>
              ) : (
                <div className="flex flex-col gap-1">
                  <button onClick={() => log(med.id, 'Took')}
                    className="bg-green-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-green-600 flex items-center gap-1">
                    <Check size={12} /> Took
                  </button>
                  <button onClick={() => log(med.id, 'Missed')}
                    className="bg-red-100 text-red-600 text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-red-200 flex items-center gap-1">
                    <X size={12} /> Missed
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
