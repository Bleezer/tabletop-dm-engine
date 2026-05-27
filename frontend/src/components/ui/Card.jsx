export default function Card({ children, paper = false, style: extra = {} }) {
  const base = {
    border: '1px solid var(--th-border)',
    borderRadius: '3px',
    padding: '1.25rem',
    ...extra,
  }

  if (paper) {
    return (
      <div className="paper-card" style={{ padding: '1.25rem', ...extra }}>
        {children}
      </div>
    )
  }

  return (
    <div style={{ background: 'var(--th-surface)', ...base }}>
      {children}
    </div>
  )
}
