import threading
import queue
import time
import networkx as nx

class RouterThread(threading.Thread):
    def __init__(self, name, neighbors, routers_dict):
        super().__init__()
        self.name = name
        self.neighbors = neighbors  # neighbor names from graph
        self.inbox = queue.Queue()
        self.running = True
        self.discovered = set()
        self.routers_dict = routers_dict

    def run(self):
        print(f"[{self.name}] Starting up...")
        # Send discovery messages to neighbors
        for n in self.neighbors:
            self.send(n, f"HELLO from {self.name}")
        # Process incoming messages
        while self.running:
            try:
                msg = self.inbox.get(timeout=1)
                print(f"[{self.name}] received: {msg}")
                src = msg.split()[-1]
                if src not in self.discovered:
                    self.discovered.add(src)
            except queue.Empty:
                pass

    def send(self, neighbor_name, message):
        if neighbor_name in self.routers_dict:
            self.routers_dict[neighbor_name].inbox.put(message)

    def stop(self):
        self.running = False


def simulate_discovery(G):
    """Run neighbor discovery using NetworkX graph G."""
    # Build neighbor map from graph adjacency
    neighbor_map = {node: list(G.neighbors(node)) for node in G.nodes}

    # Create router threads
    routers = {name: RouterThread(name, nbrs, None) for name, nbrs in neighbor_map.items()}

    # Pass reference so they can send messages
    for r in routers.values():
        r.routers_dict = routers

    # Start all routers
    for r in routers.values():
        r.start()

    # Run for a while
    time.sleep(5)

    # Stop all routers
    for r in routers.values():
        r.stop()
    for r in routers.values():
        r.join()

    # Print discovery results
    print("\n=== Neighbor Discovery Results ===")
    for name, r in routers.items():
        print(f"{name} discovered: {list(r.discovered)}")


# Example standalone run
if __name__ == "__main__":
    # Example graph (R1-R2-R3 chain)
    G = nx.Graph()
    G.add_edges_from([("R1", "R2"), ("R2", "R3")])
    simulate_discovery(G)
