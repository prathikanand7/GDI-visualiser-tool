import { useEffect, useMemo, useState } from 'react'

import { draftCypher, fetchSchema, runGraphQuery, type GraphPayload } from './api/client'
import ChatPanel from './components/ChatPanel'
import GraphPanel from './components/GraphPanel'
import QueryPanel from './components/QueryPanel'

const DEFAULT_CYPHER = 'MATCH (n)-[r]-(m) RETURN n, r, m LIMIT 100'

export default function App() {
  const [cypher, setCypher] = useState(DEFAULT_CYPHER)
  const [prompt, setPrompt] = useState('')
  const [explanation, setExplanation] = useState('')
  const [schemaText, setSchemaText] = useState('loading schema...')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [graph, setGraph] = useState<GraphPayload>({ nodes: [], relationships: [], rows: 0 })

  useEffect(() => {
    void (async () => {
      try {
        const schema = await fetchSchema()
        setSchemaText(`${schema.labels.length} labels • ${schema.relationshipTypes.length} rel-types`)
      } catch {
        setSchemaText('schema unavailable')
      }
    })()
  }, [])

  async function onRun() {
    setLoading(true)
    setError('')
    try {
      const data = await runGraphQuery(cypher)
      setGraph(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed')
    } finally {
      setLoading(false)
    }
  }

  async function onDraft() {
    setLoading(true)
    setError('')
    try {
      const data = await draftCypher(prompt)
      setCypher(data.cypher)
      setExplanation(data.explanation)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Draft failed')
    } finally {
      setLoading(false)
    }
  }

  const links = useMemo(
    () => graph.relationships.map((r) => ({ ...r, source: r.source, target: r.target })),
    [graph.relationships],
  )

  return (
    <main className="page">
      <header className="app-header">
        <h1 className="app-title">GDI visualiser tool</h1>
        <p className="muted app-subtitle">FastAPI + React + Neo4j • {schemaText}</p>
      </header>

      <div className="grid">
        <div className="left-column">
          <ChatPanel
            prompt={prompt}
            setPrompt={setPrompt}
            onDraft={onDraft}
            explanation={explanation}
            loading={loading}
          />
          <QueryPanel cypher={cypher} setCypher={setCypher} onRun={onRun} loading={loading} />
          {error && <p className="error">{error}</p>}
        </div>
        <GraphPanel nodes={graph.nodes} links={links} />
      </div>
    </main>
  )
}
