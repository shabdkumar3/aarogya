import { useState, useRef } from 'react'
import { useDiagnoScan } from '../../api/ai'
import { usePatients } from '../../api/patients'
import Spinner from '../../components/Spinner'
import { Camera, Send, AlertTriangle, X } from 'lucide-react'
import toast from 'react-hot-toast'

const LANGS = ['English','Hindi','Bengali','Tamil','Telugu','Marathi']

export default function DiagnoScan() {
  const { data: patients = [] } = usePatients()
  const diagnose = useDiagnoScan()

  const [symptoms,    setSymptoms]    = useState('')
  const [language,    setLanguage]    = useState('Hindi')
  const [patientId,   setPatientId]   = useState('')
  const [imageB64,    setImageB64]    = useState(null)
  const [imagePreview,setImagePreview]= useState(null)
  const [result,      setResult]      = useState(null)
  const fileRef = useRef()

  const handleImage = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const b64 = reader.result.split(',')[1]
      setImageB64(b64)
      setImagePreview(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!symptoms.trim()) { toast.error('Please describe the symptoms'); return }
    try {
      const data = await diagnose.mutateAsync({ symptoms, language, image_b64: imageB64 })
      setResult(data.assessment)
    } catch {
      toast.error('DiagnoScan failed — check API connection')
    }
  }

  return (
    <div className="px-4 py-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-800">DiagnoScan</h2>
        <p className="text-sm text-gray-500">AI-assisted symptom triage</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Patient selector */}
        <select className="input" value={patientId} onChange={e => setPatientId(e.target.value)}>
          <option value="">Select patient (optional)</option>
          {patients.map(p => <option key={p.id} value={p.id}>{p.name} — {p.village}</option>)}
        </select>

        {/* Language */}
        <select className="input" value={language} onChange={e => setLanguage(e.target.value)}>
          {LANGS.map(l => <option key={l}>{l}</option>)}
        </select>

        {/* Symptoms */}
        <textarea
          className="input resize-none"
          rows={4}
          placeholder="Describe symptoms in detail… (e.g. fever for 3 days, rash on arms, cough)"
          value={symptoms}
          onChange={e => setSymptoms(e.target.value)}
        />

        {/* Image upload */}
        <div>
          <button type="button" onClick={() => fileRef.current?.click()}
            className="btn-secondary w-full flex items-center justify-center gap-2 text-sm">
            <Camera size={18} />
            {imagePreview ? 'Change Image' : 'Attach Skin / Wound Photo (optional)'}
          </button>
          <input ref={fileRef} type="file" accept="image/*" capture="environment"
            className="hidden" onChange={handleImage} />
          {imagePreview && (
            <div className="relative mt-2">
              <img src={imagePreview} alt="preview" className="w-full h-40 object-cover rounded-xl" />
              <button type="button" onClick={() => { setImageB64(null); setImagePreview(null) }}
                className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-1">
                <X size={14} />
              </button>
            </div>
          )}
        </div>

        <button type="submit" className="btn-primary flex items-center justify-center gap-2"
          disabled={diagnose.isPending}>
          {diagnose.isPending ? <><Spinner size="sm" /> Analysing…</> : <><Send size={16} /> Run DiagnoScan</>}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div className="mt-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={18} className="text-amber-500" />
            <h3 className="font-semibold text-gray-800">Triage Assessment</h3>
          </div>
          <div className="card bg-amber-50 border border-amber-100 whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
            {result}
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            ⚕️ This is AI triage support only — not a clinical diagnosis
          </p>
        </div>
      )}
    </div>
  )
}
