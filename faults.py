import networkx as nx

def simulate_link_failure(G, failed_edge, demands):
    """
    Simulate a link failure by removing an edge from the topology graph.
    Re-run capacity checks to show impact on traffic.
    """
    u, v = failed_edge
    if not G.has_edge(u, v):
        print(f"\n[ERROR] Link {u}–{v} not found in topology.")
        return

    print(f"\n*** Simulating link failure: {u}–{v} ***")
    G.remove_edge(u, v)

    # Re-run traffic simulation
    from main import run_capacity_check  # reuse your load function if in main.py
    run_capacity_check(G, demands)

    # Check connectivity
    print("\n=== Connectivity Impact ===")
    for s, t, mbps in demands:
        if not nx.has_path(G, s, t):
            print(f"Traffic {s}->{t} ({mbps} Mbps) is DROPPED (no path).")
        else:
            path = nx.shortest_path(G, s, t)
            print(f"Traffic {s}->{t} rerouted via {path}")
