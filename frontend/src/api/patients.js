import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './client'

// Fetch all patients
export const usePatients = () =>
  useQuery({ queryKey: ['patients'], queryFn: () => api.get('/patients').then(r => r.data) })

// Fetch single patient
export const usePatient = (id) =>
  useQuery({ queryKey: ['patient', id], queryFn: () => api.get(`/patients/${id}`).then(r => r.data), enabled: !!id })

// Create patient
export const useCreatePatient = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post('/patients', data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['patients'] }),
  })
}

// Medications
export const useMedications = (patientId) =>
  useQuery({ queryKey: ['medications', patientId], queryFn: () => api.get(`/patients/${patientId}/medications`).then(r => r.data), enabled: !!patientId })

export const useCreateMedication = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post('/medications', data).then(r => r.data),
    onSuccess: (_, vars) => qc.invalidateQueries({ queryKey: ['medications', vars.patient_id] }),
  })
}

// Adherence
export const useAdherence = (patientId) =>
  useQuery({ queryKey: ['adherence', patientId], queryFn: () => api.get(`/patients/${patientId}/adherence`).then(r => r.data), enabled: !!patientId })

export const useLogAdherence = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post('/adherence', data).then(r => r.data),
    onSuccess: (_, vars) => qc.invalidateQueries({ queryKey: ['adherence', vars.patient_id] }),
  })
}

// Visits
export const useVisits = (patientId) =>
  useQuery({ queryKey: ['visits', patientId], queryFn: () => api.get(`/patients/${patientId}/visits`).then(r => r.data), enabled: !!patientId })

export const useCreateVisit = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post('/visits', data).then(r => r.data),
    onSuccess: (_, vars) => qc.invalidateQueries({ queryKey: ['visits', vars.patient_id] }),
  })
}

// Stats
export const useStats = () =>
  useQuery({ queryKey: ['stats'], queryFn: () => api.get('/stats').then(r => r.data) })
