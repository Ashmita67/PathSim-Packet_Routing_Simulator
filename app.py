import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
import time

st.set_page_config(page_title="PathSim:Network Routing Simulator", layout="wide")

# === Load Dataset ===
@st.cache_data
def load_data(filename):
    df = pd.read_csv(filename)
    return df[df['Weight'] >= 0]

df = load_data("router_connections_dataset.csv")

st.title("📡PathSim: Network Routing Simulator")

# === Build graph ===
def build_graph(df):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['Source'], row['Destination'], weight=row['Weight'])
    return G

G = build_graph(df)

# === Visualization ===
def draw_graph(G, highlight_path=None):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 7))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=800, arrowsize=15)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    
    if highlight_path:
        edge_list = list(zip(highlight_path[:-1], highlight_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, edge_color='green', width=3)
    
    plt.title("Network Topology", fontsize=16)
    plt.axis('off')
    st.pyplot(plt.gcf())
    plt.clf()

st.subheader("Original Network Topology")
draw_graph(G)

# === Simulate Network Events ===
def simulate_network_events(G):
    G = G.copy()
    for edge in list(G.edges()):
        event_type = random.choice(['remove', 'update'])
        if event_type == 'remove':
            G.remove_edge(*edge)
        else:
            new_weight = random.randint(1, 20)
            G[edge[0]][edge[1]]['weight'] = new_weight
    return G

if st.button("Simulate Network Events (Random Changes)"):
    G = simulate_network_events(G)
    st.success("Network updated with random edge removals and weight changes.")
    draw_graph(G)

# === Routing Table for Node ===
st.subheader("Generate Routing Table")
node = st.selectbox("Select a Router:", sorted(G.nodes()))
if node:
    data = []
    for target in G.nodes():
        if target == node:
            continue
        try:
            path = nx.dijkstra_path(G, node, target, weight='weight')
            cost = nx.dijkstra_path_length(G, node, target, weight='weight')
            path_str = " ➝ ".join(path)
        except nx.NetworkXNoPath:
            cost = float('inf')
            path_str = "N/A"
        data.append({"Destination": target, "Cost": cost, "Path": path_str})
    df_table = pd.DataFrame(data)
    st.dataframe(df_table)

# === Shortest Path Algorithms ===
st.subheader("Find Shortest Path")

col1, col2 = st.columns(2)
with col1:
    source = st.selectbox("Select Source Router:", sorted(G.nodes()), key='source')
with col2:
    target = st.selectbox("Select Destination Router:", sorted(G.nodes()), key='target')

if source and target and source != target:
    st.write(f"### Shortest paths from {source} to {target}:")

    # Dijkstra
    try:
        start_d = time.time()
        path_d = nx.dijkstra_path(G, source, target, weight='weight')
        cost_d = nx.dijkstra_path_length(G, source, target, weight='weight')
        end_d = time.time()
        time_d = (end_d - start_d) * 1000  # convert to milliseconds
        st.markdown(f"**Dijkstra Path:** { ' ➝ '.join(path_d) }  \n**Cost:** {cost_d}  \n**Time taken:** {time_d:.2f} ms")
    except nx.NetworkXNoPath:
        st.warning("Dijkstra algorithm: No path found.")
        path_d = None
        time_d = None

    # Bellman-Ford
    try:
        start_bf = time.time()
        path_bf = nx.bellman_ford_path(G, source, target, weight='weight')
        cost_bf = nx.bellman_ford_path_length(G, source, target, weight='weight')
        end_bf = time.time()
        time_bf = (end_bf - start_bf) * 1000
        st.markdown(f"**Bellman-Ford Path:** { ' ➝ '.join(path_bf) }  \n**Cost:** {cost_bf}  \n**Time taken:** {time_bf:.2f} ms")
    except nx.NetworkXNoPath:
        st.warning("Bellman-Ford algorithm: No path found.")
        path_bf = None
        time_bf = None

    # Visualize paths
    if path_d:
        st.subheader("Dijkstra Shortest Path Visualization")
        draw_graph(G, highlight_path=path_d)

    if path_bf:
        st.subheader("Bellman-Ford Shortest Path Visualization")
        draw_graph(G, highlight_path=path_bf)

    # Recommendation
    if path_d and path_bf:
        if cost_d < cost_bf:
            st.success(f"Recommendation: Use Dijkstra (Cost {cost_d} < {cost_bf})")
        elif cost_bf < cost_d:
            st.success(f"Recommendation: Use Bellman-Ford (Cost {cost_bf} < {cost_d})")
        else:
            st.info(f"Both algorithms yield the same cost ({cost_d}). Either can be used.")
    elif path_d:
        st.success("Recommendation: Use Dijkstra (Bellman-Ford failed)")
    elif path_bf:
        st.success("Recommendation: Use Bellman-Ford (Dijkstra failed)")
    else:
        st.error("No path found by either algorithm.")

else:
    if source == target and source != "":
        st.warning("Source and destination cannot be the same.")

