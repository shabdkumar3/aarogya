import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, Stethoscope, Pill, FileText, LogOut } from 'lucide-react'
import clsx from 'clsx'
import useAppStore from '../store/useAppStore'

const NAV = [
  { to: '/asha/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/asha/patients',  icon: Users,           label: 'Patients'  },
  { to: '/asha/diagnoscan',icon: Stethoscope,     label: 'Scan'      },
  { to: '/asha/medtrack',  icon: Pill,            label: 'MedTrack'  },
  { to: '/asha/reports',   icon: FileText,        label: 'Reports'   },
]

export default function AshaLayout() {
  const navigate = useNavigate()
  const setRole  = useAppStore(s => s.setRole)

  return (
    <div className="flex flex-col min-h-screen bg-surface-50">
      {/* Top bar */}
      <header className="bg-primary-600 text-white px-4 py-3 flex items-center justify-between sticky top-0 z-50 shadow-md">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🌿</span>
          <div>
            <div className="font-bold text-lg leading-none">Aarogya</div>
            <div className="text-xs text-primary-200">ASHA Worker Mode</div>
          </div>
        </div>
        <button
          onClick={() => { setRole(null); navigate('/') }}
          className="flex items-center gap-1 text-primary-200 hover:text-white transition-colors text-sm"
        >
          <LogOut size={16} /> Exit
        </button>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-auto pb-24">
        <Outlet />
      </main>

      {/* Bottom navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 shadow-lg z-50">
        <div className="flex">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => clsx(
                'flex-1 flex flex-col items-center justify-center py-2 gap-0.5 min-h-[56px] text-xs font-medium transition-colors',
                isActive
                  ? 'text-primary-600'
                  : 'text-gray-400 hover:text-primary-500'
              )}
            >
              {({ isActive }) => (
                <>
                  <Icon size={22} strokeWidth={isActive ? 2.5 : 1.8} />
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
