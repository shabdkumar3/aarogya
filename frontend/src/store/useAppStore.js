import { create } from 'zustand'

const useAppStore = create((set) => ({
  // Auth / role
  role: null,  // 'asha' | 'patient'
  setRole: (role) => set({ role }),

  // Language
  language: 'English',
  setLanguage: (language) => set({ language }),

  // Selected patient (for ASHA flow)
  selectedPatient: null,
  setSelectedPatient: (patient) => set({ selectedPatient: patient }),

  // Patient self-id (for Patient Lite flow)
  selfPatientId: null,
  setSelfPatientId: (id) => set({ selfPatientId: id }),
}))

export default useAppStore
