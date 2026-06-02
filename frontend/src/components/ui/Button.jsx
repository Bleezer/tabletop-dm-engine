const VARIANTS = {
  primary: {
    background: '#8a2020',
    color: '#e7dcc8',
    border: '1px solid #6b1818',
    hoverBg: 'var(--th-accent-lt)',
  },
  secondary: {
    background: 'var(--th-surface2)',
    color: 'var(--th-muted)',
    border: '1px solid var(--th-border-strong)',
    hoverBg: 'var(--th-bg-muted)',
  },
  gold: {
    background: 'transparent',
    color: 'var(--th-gold)',
    border: '1px solid var(--th-gold)',
    hoverBg: 'rgba(176, 138, 74, 0.12)',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--th-faint)',
    border: '1px solid transparent',
    hoverBg: 'rgba(255,255,255,0.04)',
  },
  danger: {
    background: 'rgba(122, 30, 30, 0.2)',
    color: 'var(--th-danger)',
    border: '1px solid var(--th-accent)',
    hoverBg: 'rgba(122, 30, 30, 0.38)',
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
  const padding  = size === 'sm' ? '0.3rem 0.7rem' : size === 'lg' ? '0.7rem 1.5rem' : '0.5rem 1.1rem'
  const fontSize = size === 'sm' ? '0.72rem' : size === 'lg' ? '0.95rem' : '0.8rem'

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        background: v.background,
        color: v.color,
        border: v.border,
        borderRadius: '2px',
        padding,
        fontSize,
        fontFamily: 'var(--font-display)',
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.45 : 1,
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
