import { useNavigate } from 'react-router-dom'
import { Stethoscope, Heart, Shield, Globe } from 'lucide-react'
import useAppStore from '../store/useAppStore'

const FEATURES = [
  { icon: Stethoscope, title: 'AI Triage',     desc: 'Symptom assessment powered by Gemma 4' },
  { icon: Heart,       title: 'Med Tracker',   desc: 'Medication adherence monitoring'        },
  { icon: Globe,       title: 'Multilingual',  desc: 'Hindi, Bengali, Tamil and more'         },
  { icon: Shield,      title: 'Offline Ready', desc: 'Works via Ollama without internet'       },
]

export default function Landing() {
  const navigate   = useNavigate()
  const setRole    = useAppStore(s => s.setRole)

  const go = (role) => {
    setRole(role)
    navigate(role === 'asha' ? '/asha/dashboard' : '/patient/home')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 flex flex-col items-center justify-center px-6 py-12">
      {/* Logo */}
      <div className="mb-8 text-center">
        <div className="text-7xl mb-3">🌿</div>
        <h1 className="text-4xl font-bold text-white mb-1">Aarogya</h1>
        <p className="text-primary-200 text-sm font-medium tracking-wide uppercase">
          AI Health Companion
        </p>
        <p className="text-primary-300 text-xs mt-2">
          For ASHA Workers &amp; Rural Patients
        </p>
      </div>

      {/* Role cards */}
      <div className="w-full max-w-sm flex flex-col gap-4 mb-10">
        <button
          onClick={() => go('asha')}
          className="bg-white text-primary-700 font-bold py-5 rounded-2xl shadow-card-hover
                     hover:bg-primary-50 active:scale-95 transition-all flex items-center gap-4 px-6"
        >
          <span className="text-3xl">👩‍⚕️</span>
          <div className="text-left">
            <div className="text-lg">ASHA Worker</div>
            <div className="text-xs text-gray-500 font-normal">Manage patients, run triage, track meds</div>
          </div>
        </button>

        <button
          onClick={() => go('patient')}
          className="bg-accent-500 text-white font-bold py-5 rounded-2xl shadow-card-hover
                     hover:bg-accent-600 active:scale-95 transition-all flex items-center gap-4 px-6"
        >
          <span className="text-3xl">🧑‍🤝‍🧑</span>
          <div className="text-left">
            <div className="text-lg">Patient / Family</div>
            <div className="text-xs text-orange-100 font-normal">View medicines, ask health questions</div>
          </div>
        </button>
      </div>

      {/* Features grid */}
      <div className="grid grid-cols-2 gap-3 w-full max-w-sm">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="bg-white/10 backdrop-blur rounded-xl p-3 text-white">
            <Icon size={20} className="mb-1 text-primary-200" />
            <div className="font-semibold text-sm">{title}</div>
            <div className="text-xs text-primary-200 mt-0.5">{desc}</div>
          </div>
        ))}
      </div>

      <p className="mt-8 text-primary-300 text-xs text-center max-w-xs">
        ⚕️ Triage support only — does not replace clinical diagnosis
      </p>
    </div>
  )
}
