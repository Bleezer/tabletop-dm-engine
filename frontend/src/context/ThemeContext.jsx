import { createContext, useContext, useState, useEffect } from 'react'

export const THEMES = {
  magus: {
    id: 'magus',
    label: 'MAGUS',
    icon: '⚔',
    subtitle: 'Ynev világa',
  },
  starwars: {
    id: 'starwars',
    label: 'Star Wars',
    icon: '✦',
    subtitle: 'A galaxis messze-messze...',
  },
}

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [themeId, setThemeId] = useState(
    () => localStorage.getItem('dm-theme') || 'magus'
  )

  useEffect(() => {
    document.body.dataset.theme = themeId
    localStorage.setItem('dm-theme', themeId)
  }, [themeId])

  const theme = THEMES[themeId] ?? THEMES.magus

  return (
    <ThemeContext.Provider value={{ themeId, theme, setThemeId, themes: THEMES }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
