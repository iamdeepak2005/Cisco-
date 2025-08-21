import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from main import (
    parse_config, build_topology, rename_capacity,
    simulate_traffic, utilization_dataframe,
    visualize_topology_with_icons
)

st.set_page_config(page_title="NetSim", layout="wide")

@st.cache_data
def load_topology(conf_dir="Conf"):
    router_data = []
    for file in Path(conf_dir).glob("*/config.dump"):
        router_data.append(parse_config(file))
    G = build_topology(router_data)
    rename_capacity(G)
    return G

def figure_topology(G, edge_loads=None):
    fig = plt.figure(figsize=(10,6))
    # reuse your visualize method, but direct it to current axes
    visualize_topology_with_icons(G, utilization=edge_loads or {})
    return plt.gcf()

st.title("Network Simulator")
G = load_topology()

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Traffic Demands (Mbps)")
    default_demands = [
        ("PC1", "PC2", 20),
        ("R1", "R3", 50),
        ("PC1", "R1", 10),
        ("R2", "FW1", 15),
        ("R3", "PC2", 25),
    ]
    # Simple text edit box for demands
    txt = st.text_area(
        "Format: src,dst,mbps per line",
        "\n".join([f"{s},{t},{mbps}" for s,t,mbps in default_demands]),
        height=150
    )
    demands = []
    for line in txt.splitlines():
        if not line.strip():
            continue
        s, t, m = [x.strip() for x in line.split(",")]
        demands.append((s, t, float(m)))

    st.subheader("Failure Injection")
    all_edges = ["<none>"] + [f"{u},{v}" for u, v in G.edges()]
    sel = st.selectbox("Fail a link", options=all_edges, index=0)

    run_btn = st.button("Run Simulation")

with col1:
    st.subheader("Topology")
    if run_btn:
        G_run = G.copy()
        if sel != "<none>":
            u, v = sel.split(",")
            if G_run.has_edge(u, v):
                G_run.remove_edge(u, v)
                st.warning(f"Failed link: {u} — {v}")
        edge_loads = simulate_traffic(G_run, demands)
        fig = figure_topology(G_run, edge_loads=edge_loads)
        st.pyplot(fig, clear_figure=True)

        # Metrics table
        df = utilization_dataframe(G_run, edge_loads)
        st.dataframe(df, use_container_width=True)
    else:
        fig = figure_topology(G, edge_loads=None)
        st.pyplot(fig, clear_figure=True)
        st.info("Set demands and click Run Simulation.")
