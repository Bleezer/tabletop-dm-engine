import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { SavedResultsProvider } from './context/SavedResultsContext'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import LocationGenerator from './pages/LocationGenerator'
import NpcGenerator from './pages/NpcGenerator'
import SavedResults from './pages/SavedResults'
import CharacterSheet from './pages/CharacterSheet'
import ArchetypeManager from './pages/ArchetypeManager'

export default function App() {
  return (
    <ThemeProvider>
      <SavedResultsProvider>
        <BrowserRouter>
          <Routes>
            {/* Full-page printable character sheet — outside the app chrome */}
            <Route path="karakterek/:id" element={<CharacterSheet />} />

            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="location" element={<LocationGenerator />} />
              <Route path="npc" element={<NpcGenerator />} />
              <Route path="saved" element={<SavedResults />} />
              <Route path="archetipusok" element={<ArchetypeManager />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </SavedResultsProvider>
    </ThemeProvider>
  )
}
