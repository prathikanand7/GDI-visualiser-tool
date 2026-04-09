import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export type GraphPayload = {
  nodes: Array<{ id: string; labels: string[]; properties: Record<string, unknown> }>
  relationships: Array<{
    id: string
    type: string
    source: string
    target: string
    properties: Record<string, unknown>
  }>
  rows: number
}

export async function fetchSchema() {
  const { data } = await api.get('/graph/schema')
  return data as { labels: string[]; relationshipTypes: string[]; propertyKeys: string[] }
}

export async function runGraphQuery(cypher: string, limit = 200) {
  const { data } = await api.post('/graph/query', { cypher, limit })
  return data as GraphPayload
}

export async function draftCypher(prompt: string) {
  const { data } = await api.post('/chat/draft-cypher', { prompt })
  return data as { cypher: string; explanation: string }
}
