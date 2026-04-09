import ForceGraph2D from 'react-force-graph-2d'

type GraphNode = {
  id: string
  labels: string[]
  properties: Record<string, unknown>
  x?: number
  y?: number
}
type GraphLink = {
  id: string
  type: string
  source: string
  target: string
  properties: Record<string, unknown>
}

type Props = {
  nodes: GraphNode[]
  links: GraphLink[]
}

function truncateLabel(value: string, max = 42): string {
  if (value.length <= max) {
    return value
  }
  return `${value.slice(0, max - 1)}…`
}

export default function GraphPanel({ nodes, links }: Props) {
  return (
    <section className="panel graph-panel">
      <h3>Graph</h3>
      <div className="graph-wrap">
        <ForceGraph2D
          graphData={{ nodes, links }}
          backgroundColor="#f8fafc"
          nodeRelSize={8}
          linkWidth={1.2}
          linkColor={() => '#94a3b8'}
          cooldownTicks={120}
          nodeLabel={(n) => {
            const node = n as GraphNode
            const title = (node.properties.name ?? node.properties.label ?? node.id) as string
            return `${node.labels[0] ?? 'Node'}: ${title}`
          }}
          linkLabel={(l) => (l as GraphLink).type}
          nodeAutoColorBy={(n) => ((n as GraphNode).labels[0] ?? 'Node') as string}
          nodeCanvasObjectMode={() => 'after'}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const n = node as GraphNode
            const showDenseLabels = nodes.length <= 50
            if (!showDenseLabels && globalScale < 2) {
              return
            }

            const label = truncateLabel(String(n.properties.name ?? n.properties.label ?? n.id))
            const fontSize = Math.max(10 / globalScale, 3.5)
            ctx.font = `${fontSize}px Inter, Segoe UI, Arial, sans-serif`
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillStyle = 'rgba(248, 250, 252, 0.92)'
            ctx.fillRect((n.x ?? 0) - (label.length * fontSize) / 4 - 2, (n.y ?? 0) + 9, (label.length * fontSize) / 2 + 4, fontSize + 2)
            ctx.fillStyle = '#334155'
            ctx.fillText(label, n.x ?? 0, (n.y ?? 0) + 15)
          }}
        />
      </div>
    </section>
  )
}
