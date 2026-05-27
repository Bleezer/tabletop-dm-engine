export default function Header({ title, subtitle }) {
  return (
    <header
      style={{
        padding: '1.5rem 2rem 1rem',
        borderBottom: '1px solid var(--th-border)',
        background: 'var(--th-surface)',
      }}
    >
      <h2
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.1rem',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: 'var(--th-gold)',
          margin: 0,
        }}
      >
        {title}
      </h2>
      {subtitle && (
        <p
          style={{
            margin: '0.2rem 0 0',
            fontSize: '0.9rem',
            color: 'var(--th-muted)',
            fontStyle: 'italic',
          }}
        >
          {subtitle}
        </p>
      )}
    </header>
  )
}
