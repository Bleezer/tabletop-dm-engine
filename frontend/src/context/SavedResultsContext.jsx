import { createContext, useContext, useState, useEffect } from 'react'

const SavedResultsContext = createContext(null)

const STORAGE_KEY = 'dm-saved-results'

export function SavedResultsProvider({ children }) {
  const [saved, setSaved] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    } catch {
      return []
    }
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved))
  }, [saved])

  function saveLocation(result) {
    setSaved(prev => [
      { type: 'location', id: Date.now(), savedAt: new Date().toISOString(), data: result },
      ...prev,
    ])
  }

  function saveNpc(result) {
    setSaved(prev => [
      { type: 'npc', id: Date.now(), savedAt: new Date().toISOString(), data: result },
      ...prev,
    ])
  }

  function remove(id) {
    setSaved(prev => prev.filter(item => item.id !== id))
  }

  function clearAll() {
    setSaved([])
  }

  return (
    <SavedResultsContext.Provider value={{ saved, saveLocation, saveNpc, remove, clearAll }}>
      {children}
    </SavedResultsContext.Provider>
  )
}

export const useSaved = () => useContext(SavedResultsContext)
