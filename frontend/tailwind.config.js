/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'th-bg':          'var(--th-bg)',
        'th-surface':     'var(--th-surface)',
        'th-surface2':    'var(--th-surface2)',
        'th-border':      'var(--th-border)',
        'th-text':        'var(--th-text)',
        'th-muted':       'var(--th-muted)',
        'th-accent':      'var(--th-accent)',
        'th-accent-lt':   'var(--th-accent-lt)',
        'th-paper':       'var(--th-paper)',
        'th-paper-dk':    'var(--th-paper-dk)',
        'th-ink':         'var(--th-ink)',
        'th-ink-muted':   'var(--th-ink-muted)',
        'th-gold':        'var(--th-gold)',
        'th-gold-lt':     'var(--th-gold-lt)',
      },
      fontFamily: {
        display: 'var(--font-display)',
        body:    'var(--font-body)',
      },
      boxShadow: {
        'glow-accent': '0 0 16px var(--th-accent-glow)',
        'glow-gold':   '0 0 12px var(--th-gold-glow)',
      },
    },
  },
}
