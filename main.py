import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
import os
import random

# === STEP 1: Load the dataset ===
file_name = "router_connections_dataset.csv"

if not os.path.exists(file_name):
    print(f"❌ File '{file_name}' not found. Make sure it is in the same folder as this script.")
    exit()

df = pd.read_csv(file_name)
print("Raw Dataset:")
print(df.head())

# === STEP 2: Filter out negative weights ===
df = df[df['Weight'] >= 0]
print("\nFiltered Dataset (no negative weights):")
print(df.head())

# === STEP 3: Create the graph ===
G = nx.DiGraph()
for _, row in df.iterrows():
    G.add_edge(row['Source'], row['Destination'], weight=row['Weight'])

# === STEP 4: Visualization Function ===
def visualize_graph(G, highlight_path=None, title="Network Topology", filename=None):
    pos = nx.spring_layout(G, seed=42)
    edge_labels = nx.get_edge_attributes(G, 'weight')

    plt.figure(figsize=(10, 7))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1000, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    if highlight_path:
        edge_list = list(zip(highlight_path[:-1], highlight_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, edge_color='green', width=2, label='Shortest Path')

    plt.title(title, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=300)
        print(f"Saved visualization as: {filename}")
    plt.show()

# === STEP 5: Initial Network Visualization ===
visualize_graph(G, title="Original Network Topology", filename="1_original_network.png")

# === STEP 6: Network Event Simulation ===
def simulate_network_events(G):
    print("\nSimulating network events (random edge removals or weight changes)...")
    for edge in list(G.edges()):
        event_type = random.choice(['remove', 'update'])
        if event_type == 'remove':
            G.remove_edge(*edge)
            # Removed verbose print here
        elif event_type == 'update':
            new_weight = random.randint(1, 20)
            G[edge[0]][edge[1]]['weight'] = new_weight
            # Removed verbose print here
    print("Simulation complete.\n")
    return G

G = simulate_network_events(G)

# === STEP 7: Post-Update Visualization ===
visualize_graph(G, title="Updated Network After Simulation", filename="2_updated_network.png")


# === STEP 8: Routing Table Generation for User-Selected Node ===
def generate_routing_table_for_node(G, node):
    if node not in G.nodes():
        print(f"❌ Node '{node}' not found in the graph.")
        return None

    print(f"\n📌 Routing Table for Node '{node}':")
    data = []
    for target in G.nodes():
        if target == node:
            continue
        try:
            path = nx.dijkstra_path(G, node, target, weight='weight')
            cost = nx.dijkstra_path_length(G, node, target, weight='weight')
        except nx.NetworkXNoPath:
            path = None
            cost = float('inf')
        data.append({
            "Destination": target,
            "Cost": cost,
            "Path": " ➝ ".join(path) if path else "N/A"
        })

    df_table = pd.DataFrame(data)
    print(df_table.to_string(index=False))
    return data

# === STEP 9: Algorithm Function ===
def run_algorithms(G, source, target):
    print(f"\nShortest Paths from {source} to {target}:\n")

    # Dijkstra
    try:
        start = time.time()
        path_d = nx.dijkstra_path(G, source, target, weight='weight')
        time_d = time.time() - start
        print("Dijkstra Path:", path_d)
        print("  ➤ Total Cost:", nx.dijkstra_path_length(G, source, target, weight='weight'))
        print("  ⏱️ Time Taken:", round(time_d, 6), "sec")
    except Exception as e:
        print("Dijkstra failed:", e)
        path_d = []

    # Bellman-Ford
    try:
        start = time.time()
        path_bf = nx.bellman_ford_path(G, source, target, weight='weight')
        time_bf = time.time() - start
        print("\nBellman-Ford Path:", path_bf)
        print("  ➤ Total Cost:", nx.bellman_ford_path_length(G, source, target, weight='weight'))
        print("  ⏱️ Time Taken:", round(time_bf, 6), "sec")
    except Exception as e:
        print("Bellman-Ford failed:", e)
        path_bf = []

    return path_d, path_bf

# === STEP 10: Take User Input ===
print("\nRouters in the network:", list(G.nodes))
selected_node = input("Enter the Router to generate routing table for: ").strip()
generate_routing_table_for_node(G, selected_node)
print("\nENTER NODES TO SIMULATE PATH FOR")
source = input("Enter Source Router: ").strip()
destination = input("Enter Destination Router: ").strip()

# === STEP 11: Run Algorithms and Visualize ===
path_d, path_bf = run_algorithms(G, source, destination)

visualize_graph(G, highlight_path=path_d, title="Dijkstra Shortest Path After Simulation", filename="3_dijkstra_path.png")
visualize_graph(G, highlight_path=path_bf, title="Bellman-Ford Shortest Path After Simulation", filename="4_bellman_ford_path.png")

# === STEP 12: Compare Paths and Recommend ===
print("\n📌 Final Recommendation:")

if path_d and path_bf:
    cost_d = nx.dijkstra_path_length(G, source, destination, weight='weight')
    cost_bf = nx.bellman_ford_path_length(G, source, destination, weight='weight')

    if cost_d < cost_bf:
        print(f"✅ Use Dijkstra: Lower cost ({cost_d} < {cost_bf})")
    elif cost_bf < cost_d:
        print(f"✅ Use Bellman-Ford: Lower cost ({cost_bf} < {cost_d})")
    else:
        print(f"✅ Both algorithms yield same cost ({cost_d}). Use either.")
elif path_d:
    print("✅ Use Dijkstra: Bellman-Ford failed to find a path.")
elif path_bf:
    print("✅ Use Bellman-Ford: Dijkstra failed to find a path.")
else:
    print("❌ No valid path found by either algorithm.")
