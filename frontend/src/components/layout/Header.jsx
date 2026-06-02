export default function Header({ title, subtitle }) {
  return (
    <header
      style={{
        padding: '1.25rem 2rem 1rem',
        borderBottom: '1px solid var(--th-border)',
        background: 'var(--th-surface)',
      }}
    >
      <p
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '0.62rem',
          letterSpacing: '0.22em',
          textTransform: 'uppercase',
          color: 'var(--th-faint)',
          margin: '0 0 0.15rem',
        }}
      >
        MAGUS · Mesélői Eszközök
      </p>
      <h2
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1rem',
          letterSpacing: '0.14em',
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
            fontSize: '0.85rem',
            color: 'var(--th-faint)',
            fontFamily: 'var(--font-lore)',
            fontStyle: 'italic',
          }}
        >
          {subtitle}
        </p>
      )}
    </header>
  )
}
