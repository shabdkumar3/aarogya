import { useState, useRef, useEffect } from 'react'
import { useChat } from '../../api/ai'
import { usePatient } from '../../api/patients'
import useAppStore from '../../store/useAppStore'
import Spinner from '../../components/Spinner'
import { Send, MessageCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const LANGS    = ['Hindi','English','Bengali','Tamil','Telugu','Marathi']
const STARTERS = [
  'मुझे बुखार है, क्या करूं?',
  'What foods should I avoid with diabetes?',
  'When should I take my blood pressure medicine?',
  'मेरे बच्चे को खांसी है',
]

export default function PatientChat() {
  const selfId     = useAppStore(s => s.selfPatientId)
  const language   = useAppStore(s => s.language)
  const setLang    = useAppStore(s => s.setLanguage)
  const { data: patient } = usePatient(selfId)
  const chat       = useChat()

  const [messages,  setMessages]  = useState([
    { role: 'assistant', text: 'नमस्ते! 🌿 I am Aarogya, your AI health companion. How can I help you today?' }
  ])
  const [input, setInput]         = useState('')
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const msg = text || input.trim()
    if (!msg) return
    setInput('')
    setMessages(m => [...m, { role: 'user', text: msg }])
    try {
      const ctx = patient ? `Patient: ${patient.name}, Age: ${patient.age}, Conditions: ${patient.conditions}` : ''
      const res = await chat.mutateAsync({ message: msg, language, patient_context: ctx })
      setMessages(m => [...m, { role: 'assistant', text: res.response }])
    } catch {
      toast.error('Could not reach AI — check connection')
      setMessages(m => [...m, { role: 'assistant', text: '⚠️ Sorry, I could not connect right now. Please try again.' }])
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-112px)]">
      {/* Header */}
      <div className="px-4 pt-4 pb-2 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageCircle size={20} className="text-accent-500" />
            <span className="font-semibold text-gray-800">Ask Aarogya AI</span>
          </div>
          <select className="text-xs border border-gray-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-accent-400"
            value={language} onChange={e => setLang(e.target.value)}>
            {LANGS.map(l => <option key={l}>{l}</option>)}
          </select>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm mr-2 flex-shrink-0 mt-1">
                🌿
              </div>
            )}
            <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
              m.role === 'user'
                ? 'bg-accent-500 text-white rounded-br-sm'
                : 'bg-white shadow-card text-gray-700 rounded-bl-sm'
            }`}>
              {m.text}
            </div>
          </div>
        ))}

        {chat.isPending && (
          <div className="flex justify-start">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm mr-2">
              🌿
            </div>
            <div className="bg-white shadow-card rounded-2xl rounded-bl-sm px-4 py-3">
              <Spinner size="sm" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Starter chips */}
      {messages.length <= 1 && (
        <div className="px-4 pb-2 flex flex-wrap gap-2">
          {STARTERS.map(s => (
            <button key={s} onClick={() => send(s)}
              className="text-xs bg-white border border-gray-200 text-gray-600 px-3 py-1.5 rounded-full hover:border-accent-400 hover:text-accent-500 transition-colors">
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-4 pb-4 pt-2 border-t border-gray-100 flex gap-3">
        <input
          className="input flex-1"
          placeholder="Type your health question…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
        />
        <button onClick={() => send()}
          className="bg-accent-500 text-white rounded-xl w-12 h-12 flex items-center justify-center hover:bg-accent-600 active:scale-95 transition-all flex-shrink-0"
          disabled={chat.isPending}>
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
