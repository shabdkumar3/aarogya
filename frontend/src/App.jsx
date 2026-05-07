import { Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import AshaLayout from './layouts/AshaLayout'
import PatientLayout from './layouts/PatientLayout'
import Dashboard from './pages/asha/Dashboard'
import Patients from './pages/asha/Patients'
import DiagnoScan from './pages/asha/DiagnoScan'
import MedTrack from './pages/asha/MedTrack'
import Reports from './pages/asha/Reports'
import PatientHome from './pages/patient/PatientHome'
import PatientMeds from './pages/patient/PatientMeds'
import PatientChat from './pages/patient/PatientChat'
import useAppStore from './store/useAppStore'

export default function App() {
  const role = useAppStore(s => s.role)

  return (
    <Routes>
      <Route path="/" element={<Landing />} />

      {/* ASHA Worker routes */}
      <Route path="/asha" element={<AshaLayout />}>
        <Route index element={<Navigate to="/asha/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="patients" element={<Patients />} />
        <Route path="diagnoscan" element={<DiagnoScan />} />
        <Route path="medtrack" element={<MedTrack />} />
        <Route path="reports" element={<Reports />} />
      </Route>

      {/* Patient Lite routes */}
      <Route path="/patient" element={<PatientLayout />}>
        <Route index element={<Navigate to="/patient/home" replace />} />
        <Route path="home" element={<PatientHome />} />
        <Route path="meds" element={<PatientMeds />} />
        <Route path="chat" element={<PatientChat />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
