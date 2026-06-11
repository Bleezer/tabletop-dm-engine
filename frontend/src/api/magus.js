const API_BASE = '/api/magus'

async function post(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText)
    throw new Error(`API ${res.status}: ${detail}`)
  }
  return res.json()
}

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText)
    throw new Error(`API ${res.status}: ${detail}`)
  }
  return res.json()
}

async function patch(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText)
    throw new Error(`API ${res.status}: ${detail}`)
  }
  return res.json()
}

async function del(path) {
  const res = await fetch(`${API_BASE}${path}`, { method: 'DELETE' })
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText)
    throw new Error(`API ${res.status}: ${detail}`)
  }
  return res.json()
}

export function generateLocation(locationName) {
  return post('/location', { location_name: locationName })
}

export function generateNpc(locationContext, roleHint) {
  return post('/npc', { location_context: locationContext, role_hint: roleHint })
}

export function listKarakterek() {
  return get('/karakterek')
}

export function getKarakter(id) {
  return get(`/karakterek/${id}`)
}

export function updateKarakter(id, fields) {
  return patch(`/karakterek/${id}`, fields)
}

export function deleteKarakter(id) {
  return del(`/karakterek/${id}`)
}

export function listKepzettsegek() {
  return get('/kepzettsegek')
}

export function listArchetipusok() {
  return get('/archetipusok')
}

export function getArchetipus(id) {
  return get(`/archetipusok/${id}`)
}

export function createArchetipus(body) {
  return post('/archetipusok', body)
}

export function updateArchetipus(id, body) {
  return fetch(`${API_BASE}/archetipusok/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(async res => {
    if (!res.ok) {
      const detail = await res.text().catch(() => res.statusText)
      throw new Error(`API ${res.status}: ${detail}`)
    }
    return res.json()
  })
}

export function deleteArchetipus(id) {
  return del(`/archetipusok/${id}`)
}
