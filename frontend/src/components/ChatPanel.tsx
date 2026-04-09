type Props = {
  prompt: string
  setPrompt: (value: string) => void
  onDraft: () => Promise<void>
  explanation: string
  loading: boolean
}

export default function ChatPanel({ prompt, setPrompt, onDraft, explanation, loading }: Props) {
  return (
    <section className="panel">
      <h3>Chat (NL → Cypher)</h3>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Example: show function call dependencies for 2 hops"
        rows={4}
      />
      <button onClick={() => void onDraft()} disabled={loading || !prompt.trim()}>
        {loading ? 'Drafting...' : 'Draft Cypher'}
      </button>
      {explanation && <p className="muted">{explanation}</p>}
    </section>
  )
}
