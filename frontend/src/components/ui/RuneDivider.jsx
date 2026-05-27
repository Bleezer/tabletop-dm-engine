export default function RuneDivider({ symbol = '✦', style: extra = {} }) {
  return (
    <div className="rune-divider" style={extra}>
      <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.85rem' }}>{symbol}</span>
    </div>
  )
}
