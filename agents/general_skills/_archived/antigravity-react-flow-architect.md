---
name: react-flow-architect
description: Use when building ReactFlow applications -- hierarchical navigation, performance optimization, auto-layout with Dagre, state management with undo/redo.
---

# ReactFlow Architect

Production-ready ReactFlow with hierarchical navigation, performance, and state management.

## Quick Start

```tsx
import ReactFlow, { Node, Edge } from "reactflow";

const nodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Node 1" } },
  { id: "2", position: { x: 100, y: 100 }, data: { label: "Node 2" } },
];
const edges: Edge[] = [{ id: "e1-2", source: "1", target: "2" }];

export default function Graph() {
  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

## Hierarchical Tree Navigation

### Node Schema

```typescript
interface TreeNode extends Node {
  data: {
    label: string;
    level: number;
    hasChildren: boolean;
    isExpanded: boolean;
    childCount: number;
    category: "root" | "category" | "process" | "detail";
  };
}
```

### Incremental Visible Node Building

```typescript
const buildVisibleNodes = useCallback(
  (allNodes: TreeNode[], expandedIds: Set<string>) => {
    const visibleNodes = new Map<string, TreeNode>();
    const rootNodes = allNodes.filter((n) => n.data.level === 0);

    const addVisibleChildren = (node: TreeNode) => {
      visibleNodes.set(node.id, node);
      if (expandedIds.has(node.id)) {
        allNodes.filter((n) => n.parentNode === node.id)
          .forEach((child) => addVisibleChildren(child));
      }
    };
    rootNodes.forEach((root) => addVisibleChildren(root));
    return { nodes: Array.from(visibleNodes.values()) };
  }, []
);
```

## Performance Optimization

### Memoization Patterns

```typescript
// Memoize node components
const ProcessNode = memo(({ data, selected }: NodeProps) => (
  <div className={`process-node ${selected ? 'selected' : ''}`}>{data.label}</div>
), (prev, next) =>
  prev.data.label === next.data.label &&
  prev.selected === next.selected &&
  prev.data.isExpanded === next.data.isExpanded
);

// Memoize edge styles
const styledEdges = useMemo(() =>
  edges.map(edge => ({
    ...edge,
    style: { strokeWidth: selectedEdgeId === edge.id ? 3 : 2, stroke: selectedEdgeId === edge.id ? '#3b82f6' : '#94a3b8' },
    animated: selectedEdgeId === edge.id,
  })), [edges, selectedEdgeId]
);

// Use Map for O(1) lookups
const nodesById = useMemo(() => new Map(allNodes.map((n) => [n.id, n])), [allNodes]);
```

### Memory Management

```typescript
// Use useRef for non-render data
const layoutCacheRef = useRef<Map<string, Node[]>>(new Map());

useEffect(() => {
  return () => { nodesMapRef.current.clear(); edgesMapRef.current.clear(); };
}, []);
```

## State Management: Reducer Pattern

```typescript
type GraphAction =
  | { type: "SELECT_NODE"; payload: string }
  | { type: "TOGGLE_EXPAND"; payload: string }
  | { type: "UPDATE_NODES"; payload: Node[] }
  | { type: "UNDO" } | { type: "REDO" };

const graphReducer = (state: GraphState, action: GraphAction): GraphState => {
  switch (action.type) {
    case "SELECT_NODE":
      return { ...state, selectedNodeId: action.payload, selectedEdgeId: null };
    case "TOGGLE_EXPAND":
      const newExpanded = new Set(state.expandedNodeIds);
      newExpanded.has(action.payload) ? newExpanded.delete(action.payload) : newExpanded.add(action.payload);
      return { ...state, expandedNodeIds: newExpanded, isDirty: true };
    default: return state;
  }
};
```

## Auto-Layout with Dagre

```typescript
import dagre from "dagre";

const applyLayout = (nodes: Node[], edges: Edge[]) => {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "TB", nodesep: 100, ranksep: 150 });
  g.setDefaultEdgeLabel(() => ({}));

  nodes.forEach((node) => g.setNode(node.id, { width: 200, height: 100 }));
  edges.forEach((edge) => g.setEdge(edge.source, edge.target));
  dagre.layout(g);

  return nodes.map((node) => ({
    ...node,
    position: { x: g.node(node.id).x - 100, y: g.node(node.id).y - 50 },
  }));
};

const debouncedLayout = useMemo(() => debounce(applyLayout, 150), []);
```

## Focus Mode

```typescript
const useFocusMode = (selectedNodeId: string, allNodes: Node[], allEdges: Edge[]) =>
  useMemo(() => {
    if (!selectedNodeId) return { nodes: allNodes, edges: allEdges };
    const connectedNodeIds = new Set([selectedNodeId]);
    const focusedEdges = allEdges.filter((edge) => {
      if (edge.source === selectedNodeId || edge.target === selectedNodeId) {
        connectedNodeIds.add(edge.source); connectedNodeIds.add(edge.target);
        return true;
      }
      return false;
    });
    return { nodes: allNodes.filter((n) => connectedNodeIds.has(n.id)), edges: focusedEdges };
  }, [selectedNodeId, allNodes, allEdges]);
```

## Search Integration

```typescript
const navigateToSearchResult = (nodeId: string) => {
  const nodePath = calculateBreadcrumbPath(nodeId, allNodes);
  setExpandedIds((prev) => new Set([...prev, ...nodePath.slice(0, -1).map((n) => n.id)]));
  setSelectedNodeId(nodeId);
  fitView({ nodes: [{ id: nodeId }], duration: 800 });
};
```

## Common Problems

| Problem | Solution |
|---------|----------|
| Lag during expansion | Incremental rendering with change detection |
| Memory growth | Cleanup in useEffect, WeakMap for temp data |
| Positioning conflicts | Controlled positioning state, separate layout modes |
| Excessive re-renders | `memo`, `useMemo`, `useCallback` with stable deps |
| Slow layout | Debounce calculations, cache results |

## Best Practices

1. `React.memo` for all node components with custom comparators
2. Virtualization for 1000+ nodes
3. Debounce layout during rapid interactions
4. `useCallback` for edge creation/manipulation
5. `Map` for O(1) lookups instead of `array.find`
6. `useRef` for objects that shouldn't trigger re-renders
