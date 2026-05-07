import { useMutation } from '@tanstack/react-query'
import api from './client'

export const useChat = () =>
  useMutation({ mutationFn: (data) => api.post('/chat', data).then(r => r.data) })

export const useDiagnoScan = () =>
  useMutation({ mutationFn: (data) => api.post('/diagnoscan', data).then(r => r.data) })
