import { useState } from 'react'
import {
  usePatients, useMedications, useCreateMedication,
  useAdherence, useLogAdherence
} from '../../api/patients'
import AdherenceBar from '../../components/AdherenceBar'
import Spinner from '../../components/Spinner'
import EmptyState from '../../components/EmptyState'
import { Plus, Check, X as XIcon } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

const MED_INIT = { name:'', dose:'', frequency:'Once daily', start_date: format(new Date(),'yyyy-MM-dd'), end_date:'' }
const FREQS    = ['Once daily','Twice daily','Three times daily','As needed','Weekly']

export default function MedTrack() {
  const { data: patients = [] } = usePatients()
  const [selPid, setSelPid]     = useState('')
  const { data: meds = [], isLoading: medsLoading } = useMedications(selPid || null)
  const { data: adh  = [] }                          = useAdherence(selPid || null)
  const createMed     = useCreateMedication()
  const logAdherence  = useLogAdherence()

  const [showForm, setShowForm] = useState(false)
  const [form, setForm]         = useState(MED_INIT)

  const today = format(new Date(), 'yyyy-MM-dd')

  // Compute adherence % for selected patient
  const took  = adh.filter(a => a.status === 'Took').length
  const adhPct = adh.length ? Math.round((took / adh.length) * 100) : 0

  // Today's logs
  const todayLogs = adh.filter(a => a.date === today)

  const handleAddMed = async (e) => {
    e.preventDefault()
    if (!selPid) { toast.error('Select a patient first'); return }
    if (!form.name || !form.dose) { toast.error('Medicine name and dose required'); return }
    try {
      await createMed.mutateAsync({ ...form, patient_id: Number(selPid) })
      toast.success('Medication added')
      setForm(MED_INIT); setShowForm(false)
    } catch { toast.error('Failed to add medication') }
  }

  const log = async (medId, status) => {
    if (!selPid) return
    try {
      await logAdherence.mutateAsync({ medication_id: medId, patient_id: Number(selPid), date: today, status })
      toast.success(`Marked as ${status}`)
    } catch { toast.error('Failed to log adherence') }
  }

  return (
    <div className="px-4 py-6">
      <div className="mb-5">
        <h2 className="text-xl font-bold text-gray-800">MedTrack</h2>
        <p className="text-sm text-gray-500">Medication adherence tracker</p>
      </div>

      {/* Patient picker */}
      <select className="input mb-4" value={selPid} onChange={e => setSelPid(e.target.value)}>
        <option value="">— Select patient —</option>
        {patients.map(p => <option key={p.id} value={p.id}>{p.name} · {p.village}</option>)}
      </select>

      {selPid && (
        <>
          {/* Adherence summary */}
          <div className="card mb-4">
            <div className="flex justify-between items-center mb-3">
              <span className="font-semibold text-gray-700">Adherence Rate</span>
              <span className="text-sm font-bold text-primary-600">{adhPct}%</span>
            </div>
            <AdherenceBar pct={adhPct} />
          </div>

          {/* Today's check-in */}
          {meds.length > 0 && (
            <div className="card mb-4">
              <h3 className="font-semibold text-gray-700 mb-3">Today's Check-in</h3>
              <div className="flex flex-col gap-2">
                {meds.map(med => {
                  const logged = todayLogs.find(a => a.medication_id === med.id)
                  return (
                    <div key={med.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                      <div>
                        <div className="font-medium text-sm text-gray-800">{med.name}</div>
                        <div className="text-xs text-gray-400">{med.dose} · {med.frequency}</div>
                      </div>
                      {logged ? (
                        <span className={`text-xs font-semibold px-2 py-1 rounded-full ${logged.status === 'Took' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {logged.status}
                        </span>
                      ) : (
                        <div className="flex gap-2">
                          <button onClick={() => log(med.id, 'Took')}
                            className="p-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors">
                            <Check size={16} />
                          </button>
                          <button onClick={() => log(med.id, 'Missed')}
                            className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors">
                            <XIcon size={16} />
                          </button>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Medications list */}
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-700">Medications ({meds.length})</h3>
            <button onClick={() => setShowForm(true)}
              className="flex items-center gap-1 text-primary-600 text-sm font-medium">
              <Plus size={16} /> Add
            </button>
          </div>

          {medsLoading ? <div className="flex justify-center py-8"><Spinner /></div>
          : meds.length === 0 ? <EmptyState icon="💊" title="No medications" message="Tap + to add" />
          : (
            <div className="flex flex-col gap-2">
              {meds.map(m => (
                <div key={m.id} className="card py-3">
                  <div className="font-medium text-gray-800">{m.name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{m.dose} · {m.frequency}</div>
                  <div className="text-xs text-gray-400 mt-0.5">From {m.start_date}{m.end_date ? ` → ${m.end_date}` : ''}</div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!selPid && <EmptyState icon="💊" title="Select a patient" message="Choose a patient above to view their medications" />}

      {/* Add Medication Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end">
          <div className="bg-white w-full rounded-t-3xl p-6 max-h-[85vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-gray-800 mb-5">Add Medication</h3>
            <form onSubmit={handleAddMed} className="flex flex-col gap-4">
              <input className="input" placeholder="Medicine name *" value={form.name}
                onChange={e => setForm(f => ({...f, name: e.target.value}))} />
              <input className="input" placeholder="Dose (e.g. 500mg) *" value={form.dose}
                onChange={e => setForm(f => ({...f, dose: e.target.value}))} />
              <select className="input" value={form.frequency}
                onChange={e => setForm(f => ({...f, frequency: e.target.value}))}>
                {FREQS.map(fr => <option key={fr}>{fr}</option>)}
              </select>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-500 mb-1 block">Start date</label>
                  <input className="input" type="date" value={form.start_date}
                    onChange={e => setForm(f => ({...f, start_date: e.target.value}))} />
                </div>
                <div>
                  <label className="text-xs text-gray-500 mb-1 block">End date (optional)</label>
                  <input className="input" type="date" value={form.end_date}
                    onChange={e => setForm(f => ({...f, end_date: e.target.value}))} />
                </div>
              </div>
              <div className="flex gap-3">
                <button type="button" className="btn-secondary flex-1" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn-primary flex-1" disabled={createMed.isPending}>
                  {createMed.isPending ? 'Adding…' : 'Add Medication'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
