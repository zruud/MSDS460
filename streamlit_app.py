import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary

# Distance data
edges = {
    ("Origin", "A"): 40,
    ("Origin", "B"): 60,
    ("Origin", "C"): 50,
    ("A", "B"): 10,
    ("A", "D"): 70,
    ("B", "C"): 20,
    ("B", "D"): 55,
    ("B", "E"): 40,
    ("C", "E"): 50,
    ("D", "E"): 10,
    ("D", "Destination"): 60,
    ("E", "Destination"): 80
}

towns = sorted(set(t for edge in edges for t in edge))

st.title("🚗 Shortest Path Route Planner")

# Part (a): Draw the network
st.header("(a) Network Graph")
G = nx.Graph()
for (u, v), w in edges.items():
    G.add_edge(u, v, weight=w)

pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(10, 6))
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
st.pyplot(plt)

# Part (b): Dijkstra's algorithm
st.header("(b) Shortest Path using Dijkstra’s Algorithm")
shortest_path = nx.dijkstra_path(G, source="Origin", target="Destination")
shortest_distance = nx.dijkstra_path_length(G, source="Origin", target="Destination")
st.write(f"**Shortest Path**: {' → '.join(shortest_path)}")
st.write(f"**Total Distance**: {shortest_distance} miles")

# Part (c): Spreadsheet-style optimization using PuLP
st.header("(c) Optimization Model")
model = LpProblem("ShortestPath", LpMinimize)

# Binary decision variable for each edge
x = LpVariable.dicts("x", edges, cat=LpBinary)

# Objective: Minimize total distance
model += lpSum([edges[e] * x[e] for e in edges])

# Flow balance constraints
for t in towns:
    inflow = lpSum([x[e] for e in edges if e[1] == t])
    outflow = lpSum([x[e] for e in edges if e[0] == t])
    if t == "Origin":
        model += outflow - inflow == 1
    elif t == "Destination":
        model += inflow - outflow == 1
    else:
        model += inflow - outflow == 0

model.solve()
opt_path = [e for e in edges if x[e].value() == 1]
opt_path_str = " → ".join([opt_path[0][0]] + [e[1] for e in opt_path])
st.write(f"**Optimized Path (LP)**: {opt_path_str}")
st.write(f"**Total Distance (LP)**: {sum(edges[e] for e in opt_path)} miles")

# Part (d): Cost interpretation
st.header("(d) Interpreting Distances as Costs 💸")
st.write("If the distances represent **costs**, the answer in (b) and (c) still gives the **minimum-cost route** because both methods are minimizing the same numeric values.")

# Part (e): Time interpretation
st.header("(e) Interpreting Distances as Time ⏱️")
st.write("If the distances represent **time**, the answer in (b) and (c) still gives the **minimum-time route**, because again the same optimization is being performed over the same numbers.")

st.success("✅ All tasks completed.")
