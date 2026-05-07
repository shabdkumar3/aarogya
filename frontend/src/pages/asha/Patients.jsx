import { useState } from 'react'
import { usePatients, useCreatePatient } from '../../api/patients'
import PatientCard from '../../components/PatientCard'
import Spinner from '../../components/Spinner'
import EmptyState from '../../components/EmptyState'
import { Plus, X, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import useAppStore from '../../store/useAppStore'

const INITIAL = { name:'', age:'', gender:'Female', village:'', phone:'', conditions:'', language:'Hindi' }
const GENDERS = ['Female','Male','Other']
const LANGS   = ['Hindi','English','Bengali','Tamil','Telugu','Marathi','Kannada','Gujarati']

export default function Patients() {
  const { data: patients = [], isLoading } = usePatients()
  const createPatient = useCreatePatient()
  const setSelected   = useAppStore(s => s.setSelectedPatient)

  const [showForm, setShowForm] = useState(false)
  const [form, setForm]         = useState(INITIAL)
  const [search, setSearch]     = useState('')

  const filtered = patients.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.village.toLowerCase().includes(search.toLowerCase())
  )

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name || !form.age || !form.village) {
      toast.error('Name, age, and village are required')
      return
    }
    try {
      await createPatient.mutateAsync({ ...form, age: Number(form.age) })
      toast.success('Patient registered!')
      setForm(INITIAL)
      setShowForm(false)
    } catch {
      toast.error('Failed to register patient')
    }
  }

  return (
    <div className="px-4 py-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Patients</h2>
          <p className="text-sm text-gray-500">{patients.length} registered</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-1 px-4 py-2 text-sm">
          <Plus size={16} /> Add
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          className="input pl-9"
          placeholder="Search by name or village…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : filtered.length === 0 ? (
        <EmptyState icon="👥" title="No patients found"
          message={search ? 'Try a different search' : 'Tap + to register a patient'} />
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.map(p => (
            <PatientCard key={p.id} patient={p} onClick={() => setSelected(p)} />
          ))}
        </div>
      )}

      {/* Add Patient Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end">
          <div className="bg-white w-full rounded-t-3xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-800">Register Patient</h3>
              <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600">
                <X size={22} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <input className="input" placeholder="Full name *" value={form.name}
                onChange={e => setForm(f => ({...f, name: e.target.value}))} />
              <div className="grid grid-cols-2 gap-3">
                <input className="input" type="number" placeholder="Age *" value={form.age}
                  onChange={e => setForm(f => ({...f, age: e.target.value}))} />
                <select className="input" value={form.gender}
                  onChange={e => setForm(f => ({...f, gender: e.target.value}))}>
                  {GENDERS.map(g => <option key={g}>{g}</option>)}
                </select>
              </div>
              <input className="input" placeholder="Village / District *" value={form.village}
                onChange={e => setForm(f => ({...f, village: e.target.value}))} />
              <input className="input" placeholder="Phone number" value={form.phone}
                onChange={e => setForm(f => ({...f, phone: e.target.value}))} />
              <input className="input" placeholder="Known conditions (e.g. Diabetes, HTN)" value={form.conditions}
                onChange={e => setForm(f => ({...f, conditions: e.target.value}))} />
              <select className="input" value={form.language}
                onChange={e => setForm(f => ({...f, language: e.target.value}))}>
                {LANGS.map(l => <option key={l}>{l}</option>)}
              </select>

              <button type="submit" className="btn-primary w-full mt-2"
                disabled={createPatient.isPending}>
                {createPatient.isPending ? 'Registering…' : 'Register Patient'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
