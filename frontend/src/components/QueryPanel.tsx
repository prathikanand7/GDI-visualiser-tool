type Props = {
  cypher: string
  setCypher: (value: string) => void
  onRun: () => Promise<void>
  loading: boolean
}

export default function QueryPanel({ cypher, setCypher, onRun, loading }: Props) {
  return (
    <section className="panel">
      <h3>Cypher Query</h3>
      <textarea value={cypher} onChange={(e) => setCypher(e.target.value)} rows={10} />
      <button onClick={() => void onRun()} disabled={loading || !cypher.trim()}>
        {loading ? 'Running...' : 'Render Graph'}
      </button>
    </section>
  )
}
