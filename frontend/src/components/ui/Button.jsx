const VARIANTS = {
  primary: {
    background: 'var(--th-accent)',
    color: '#fff',
    border: '1px solid var(--th-accent)',
    hoverBg: 'var(--th-accent-lt)',
  },
  secondary: {
    background: 'var(--th-surface2)',
    color: 'var(--th-text)',
    border: '1px solid var(--th-border)',
    hoverBg: 'var(--th-surface)',
  },
  gold: {
    background: 'transparent',
    color: 'var(--th-gold)',
    border: '1px solid var(--th-gold)',
    hoverBg: 'rgba(201,149,14,0.1)',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--th-muted)',
    border: '1px solid transparent',
    hoverBg: 'rgba(255,255,255,0.05)',
  },
}

export default function Button({
  children,
  variant = 'primary',
  disabled = false,
  onClick,
  fullWidth = false,
  size = 'md',
  style: extraStyle = {},
}) {
  const v = VARIANTS[variant] ?? VARIANTS.primary
  const padding = size === 'sm' ? '0.35rem 0.75rem' : size === 'lg' ? '0.75rem 1.5rem' : '0.55rem 1.1rem'
  const fontSize = size === 'sm' ? '0.75rem' : size === 'lg' ? '1rem' : '0.85rem'

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        background: v.background,
        color: v.color,
        border: v.border,
        borderRadius: '3px',
        padding,
        fontSize,
        fontFamily: 'var(--font-display)',
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'all 0.15s ease',
        width: fullWidth ? '100%' : undefined,
        ...extraStyle,
      }}
      onMouseEnter={e => {
        if (!disabled) e.currentTarget.style.background = v.hoverBg
      }}
      onMouseLeave={e => {
        if (!disabled) e.currentTarget.style.background = v.background
      }}
    >
      {children}
    </button>
  )
}
