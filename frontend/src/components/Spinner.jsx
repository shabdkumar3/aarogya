export default function Spinner({ size = 'md' }) {
  const s = size === 'lg' ? 'w-10 h-10' : size === 'sm' ? 'w-4 h-4' : 'w-6 h-6'
  return (
    <div className={`${s} border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin`} />
  )
}
