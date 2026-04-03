---
name: networkx
description: "Python library for creating, analyzing, and visualizing complex networks and graphs."
---

# NetworkX

Python package for building and analyzing graph/network structures -- social networks, biological networks, knowledge graphs, transportation systems, or any relational data. Supports undirected, directed, and multigraph types with arbitrary node/edge attributes.

## Key Patterns

- **Four graph types**: `Graph` (undirected), `DiGraph` (directed), `MultiGraph` (parallel edges), `MultiDiGraph` (directed + parallel)
- **Nodes can be any hashable**: strings, ints, tuples -- add attributes via `G.add_node("A", type="hub")`
- **Centrality measures**: `degree_centrality`, `betweenness_centrality`, `closeness_centrality`, `pagerank` -- pick based on what "importance" means
- **Community detection**: `community.greedy_modularity_communities(G)` for discovering clusters
- **Shortest paths**: `nx.shortest_path(G, source, target, weight='weight')` -- supports weighted and unweighted
- **Always set random seed**: `nx.spring_layout(G, seed=42)` and `nx.erdos_renyi_graph(n, p, seed=42)` for reproducibility
- **Pandas integration**: `nx.from_pandas_edgelist(df, 'src', 'tgt', edge_attr='weight')` and back with `nx.to_pandas_edgelist(G)`
- **Large graphs**: Use sparse matrices (`nx.to_scipy_sparse_array`), approximate algorithms, and load only needed subgraphs
- **Removing a node removes all its edges**: Be aware when modifying graphs
- **GraphML for interop**: Preserves attributes; use edge lists for simple cases

## Quick Reference

### Essential Operations

```python
import networkx as nx

# Create and populate
G = nx.Graph()                                    # or DiGraph, MultiGraph
G.add_edges_from([(1,2), (2,3), (3,4)], weight=1.0)
G.add_node(5, label="isolated")

# Inspect
G.number_of_nodes()             # node count
G.number_of_edges()             # edge count
nx.density(G)                   # edge density
nx.is_connected(G)              # connectivity check
list(G.neighbors(2))            # adjacent nodes
G.degree(2)                     # node degree
G[1][2]                         # edge attributes
```

### Analysis

```python
# Centrality
nx.degree_centrality(G)
nx.betweenness_centrality(G)
nx.closeness_centrality(G)
nx.pagerank(G)                  # for DiGraph

# Paths and components
nx.shortest_path(G, 1, 4)
nx.shortest_path_length(G, 1, 4, weight='weight')
list(nx.connected_components(G))

# Community detection
from networkx.algorithms import community
communities = community.greedy_modularity_communities(G)

# Clustering
nx.clustering(G)
nx.average_clustering(G)
```

### Graph Generators

```python
# Classic
G = nx.complete_graph(10)
G = nx.karate_club_graph()

# Random models
G = nx.erdos_renyi_graph(n=100, p=0.1, seed=42)       # random
G = nx.barabasi_albert_graph(n=100, m=3, seed=42)      # scale-free
G = nx.watts_strogatz_graph(n=100, k=6, p=0.1, seed=42) # small-world
```

### I/O and Visualization

```python
import matplotlib.pyplot as plt
import pandas as pd

# File I/O
nx.write_graphml(G, "graph.graphml")   # preserves attributes
G = nx.read_graphml("graph.graphml")
G = nx.read_edgelist("edges.txt")

# Pandas interop
G = nx.from_pandas_edgelist(df, 'source', 'target', edge_attr='weight')
df = nx.to_pandas_edgelist(G)

# Matrix
import numpy as np
A = nx.to_numpy_array(G)
G = nx.from_numpy_array(A)

# Visualize
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500)
plt.show()

# Color by centrality
colors = [nx.betweenness_centrality(G)[n] for n in G.nodes()]
nx.draw(G, pos, node_color=colors, cmap=plt.cm.viridis)
```

## When to Use

- Modeling relationships between entities (social, biological, citation networks)
- Computing graph metrics: centrality, clustering coefficient, shortest paths
- Detecting communities or connected components in relational data
- Generating synthetic networks for simulation (Erdos-Renyi, Barabasi-Albert, Watts-Strogatz)
- Converting between graph formats (edge list, GraphML, adjacency matrix, pandas DataFrame)

## Resources

- [NetworkX Documentation](https://networkx.org/documentation/latest/)
- [GitHub](https://github.com/networkx/networkx)
