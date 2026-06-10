export function formatRelativeTime(isoString) {
  const diffMs = Date.now() - new Date(isoString).getTime()
  const diffMin = Math.floor(diffMs / 60000)

  if (diffMin < 1) return 'most'
  if (diffMin < 60) return `${diffMin} perce`

  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} órája`

  const diffDay = Math.floor(diffHour / 24)
  return `${diffDay} napja`
}
