import socket
import threading
import json
import time
import sys
import os

def load_config():
    node_name = sys.argv[1]
    with open(f"config/{node_name}.json", "r") as f:
        config = json.load(f)
    return config

config = load_config()
NODE_NAME = config['node_name']
NEIGHBORS = config['neighbors']
ALL_NODES = config['all_nodes']
LISTEN_PORT = config['listen_port']

LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"{NODE_NAME}.log")

infinity = float('inf')
distances = {node: infinity for node in ALL_NODES}
distances[NODE_NAME] = 0

for neighbor, info in NEIGHBORS.items():
    distances[neighbor] = info['weight']

distance_lock = threading.Lock()

def log(message):
    """Log a message to the node's log file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def send_update():
    """Send distance updates to all neighbors."""
    with distance_lock:
        data = {
            'source': NODE_NAME,
            'distances': distances.copy()
        }
    for neighbor, info in NEIGHBORS.items():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((info['host'], info['port']))
                s.sendall(json.dumps(data).encode('utf-8'))
                log(f"Sent update to {neighbor}: {distances}")
        except ConnectionError:
            log(f"Failed to connect to {neighbor}")

def listen_for_updates():
    """Listen for updates from neighbors."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', LISTEN_PORT))
        server_socket.listen(5)
        log(f"{NODE_NAME} listening on port {LISTEN_PORT}...")
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_update, args=(conn,)).start()

def handle_update(conn):
    """Handle incoming update from a neighbor."""
    with conn:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            return
        message = json.loads(data)
        source = message['source']
        neighbor_distances = message['distances']

        updated = False
        log(f"Received update from {source}: {neighbor_distances}")
        
        with distance_lock:
            for node in ALL_NODES:
                if distances[node] != infinity:
                    new_distance = distances[node] + neighbor_distances[node]
                else:
                    new_distance = distances[source] + neighbor_distances[node]
                
                if new_distance < distances[node]:
                    log(f"Updating distance for {node}: old={distances[node]}, new={new_distance} (via {source})")
                    distances[node] = new_distance
                    updated = True

                if updated:
                    log(f"Updated distances: {distances}")
                    send_update()

def main():
    """Start the node."""
    threading.Thread(target=listen_for_updates, daemon=True).start()
    time.sleep(1)
    send_update()
    log(f"Final distances: {distances}")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
