import { ref } from 'vue'
import axios from 'axios'

// Shared by the read-only viewer (InteractiveRoadmapGraph.vue) and the
// Career Path view - fetches a roadmap's nodes/edges into vue-flow-shaped
// state, and owns the progress-cycling logic both consumers need. The
// Studio (RoadmapStudioView.vue) does its own fetching since it also needs
// write operations (create/update/delete) that don't belong here.
//
// roadmapSlugSource may be a plain string OR a getter function (`() =>
// props.roadmapSlug`). Accepting a getter lets fetchRoadmapData() re-read
// the CURRENT slug on every call instead of closing over whatever value was
// passed in at setup time - a plain string here previously meant switching
// roadmaps via a dropdown silently kept re-fetching the original slug.
export function useRoadmapGraph(roadmapSlugSource) {
  const resolveSlug = () => (typeof roadmapSlugSource === 'function' ? roadmapSlugSource() : roadmapSlugSource)
  const roadmapTitle = ref('')
  const rawNodes = ref([])
  const nodes = ref([])
  const edges = ref([])
  const progressPercent = ref(0)
  const doneCount = ref(0)
  const totalCount = ref(0)
  const updatingProgress = ref(false)

  // Nodes without a saved position (e.g. content seeded before the Studio
  // existed) fall back to a simple grid by array order, purely so nothing
  // ever stacks at (0,0) on top of other nodes.
  const toFlowNode = (n, idx) => ({
    id: String(n.id),
    type: 'roadmapNode',
    position: {
      x: n.position_x ?? (idx % 4) * 240,
      y: n.position_y ?? Math.floor(idx / 4) * 160
    },
    data: { ...n }
  })

  const fetchRoadmapData = async () => {
    try {
      const res = await axios.get(`/api/roadmaps/${resolveSlug()}`, { withCredentials: true })
      roadmapTitle.value = res.data.roadmap?.title || 'Roadmap'
      rawNodes.value = res.data.nodes || []
      progressPercent.value = res.data.progress_percent || 0
      doneCount.value = res.data.done_count || 0
      totalCount.value = res.data.total_count || 0

      nodes.value = rawNodes.value.map(toFlowNode)
      edges.value = (res.data.edges || []).map(e => {
        const edgeType = e.edge_type || 'default'
        return {
          id: `e${e.id}`,
          source: String(e.source_node_id),
          target: String(e.target_node_id),
          label: e.label || '',
          data: { edge_type: edgeType },
          style: edgeType === 'alternative'
            ? { stroke: '#fbbf24', strokeWidth: 2.5, strokeDasharray: '8 6' }
            : { stroke: '#9fef00', strokeWidth: 2.5 }
        }
      })
    } catch (e) {
      console.error('Failed to fetch roadmap data:', e)
    }
  }

  const cycleNodeProgress = async (node) => {
    if (updatingProgress.value) return
    updatingProgress.value = true

    const nextStatusMap = { not_started: 'in_progress', in_progress: 'done', done: 'not_started' }
    const nextStatus = nextStatusMap[node.user_status] || 'in_progress'

    try {
      const res = await axios.patch(`/api/roadmaps/nodes/${node.id}/progress`, { status: nextStatus }, { withCredentials: true })
      node.user_status = nextStatus
      progressPercent.value = res.data.progress_percent
      doneCount.value = res.data.done_count
      totalCount.value = res.data.total_count

      const flowNode = nodes.value.find(n => n.id === String(node.id))
      if (flowNode) flowNode.data.user_status = nextStatus
    } catch (e) {
      if (e.response && e.response.status === 401) {
        alert('Please log in to save your roadmap progress.')
      } else {
        console.error('Failed to update node progress:', e)
      }
    } finally {
      updatingProgress.value = false
    }
  }

  const getStatusColorClass = (status) => {
    if (status === 'done') return 'text-[#9fef00]'
    if (status === 'in_progress') return 'text-amber-400'
    return 'text-slate-400'
  }

  const getCycleButtonClass = (status) => {
    if (status === 'done') return 'bg-[#9fef00] text-black border-[#9fef00] hover:bg-[#8ee000]'
    if (status === 'in_progress') return 'bg-amber-400 text-black border-amber-400 hover:bg-amber-300'
    return 'bg-[#21262d] text-slate-200 border-[#30363d] hover:bg-[#30363d]'
  }

  const getCycleButtonText = (status) => {
    if (status === 'done') return 'Mark Not Started'
    if (status === 'in_progress') return 'Mark Completed'
    return 'Start Practice'
  }

  return {
    roadmapTitle,
    rawNodes,
    nodes,
    edges,
    progressPercent,
    doneCount,
    totalCount,
    updatingProgress,
    fetchRoadmapData,
    cycleNodeProgress,
    getStatusColorClass,
    getCycleButtonClass,
    getCycleButtonText
  }
}
