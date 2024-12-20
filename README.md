# DistributedBellmanFord

This repository implements a distributed distance vector protocol using Python and Docker. Each node in the network calculates the shortest path to all other nodes using its neighbors' information. The protocol leverages periodic updates and multi-threaded communication between nodes.

## Repository Structure

```
.
├── node.py               # Main Python script for the node functionality
├── Dockerfile            # Dockerfile to build the node's image
├── docker-compose.yml    # Docker Compose configuration for multi-node setup
├── config/               # Configuration files for each node
│   ├── Node1.json        # Configuration for Node1
│   ├── Node2.json        # Configuration for Node2
│   ├── Node3.json        # Configuration for Node3
│   ├── Node4.json        # Configuration for Node4
│   └── Node5.json        # Configuration for Node5
└── logs/                 # Log directory for each node (populated at runtime)
```

## Getting Started

### 1. Build and Run the Nodes

1. Clone the repository
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2. Build the Docker images and start the containers using Docker Compose
    ```bash
    docker-compose up --build
    ```
3. Logs for each node are available in the logs/ directory.

### 2. Node Configuration

Each node's configuration is defined in the config directory as a JSON file.

- node_name: Unique name of the node.

- listen_port: Port on which the node listens for updates.

- all_nodes: List of all nodes in the network.

- neighbors: Dictionary of neighbor nodes with their host, port, and weight (link cost).

Example (Node1.json):
```json
{
  "node_name": "Node1",
  "listen_port": 5001,
  "all_nodes": ["Node1", "Node2", "Node3", "Node4", "Node5"],
  "neighbors": {
    "Node2": {"host": "node2", "port": 5002, "weight": 2},
    "Node3": {"host": "node3", "port": 5003, "weight": 4}
  }
}
```

### 3. Protocol Behavior

- Each node starts a server to listen for updates from its neighbors.

- Nodes exchange distance vectors periodically and update their routing tables based on received information.

- Logs are written to each node's log file in /app/logs/ within the container or logs/ on the host.

## Logs

Logs for each node capture updates and routing table changes. Example log entry:

```
[2024-12-20 11:54:24] Sent update to Node2: {'Node1': 0, 'Node2': 2, 'Node3': 4, 'Node4': inf, 'Node5': inf}
[2024-12-20 11:54:24] Received update from Node3: {'Node1': 4, 'Node2': inf, 'Node3': 0, 'Node4': inf, 'Node5': 4}
[2024-12-20 11:54:24] Received update from Node2: {'Node1': 2, 'Node2': 0, 'Node3': inf, 'Node4': 3, 'Node5': inf}
[2024-12-20 11:54:24] Updating distance for Node4: old=inf, new=5 (via Node2)
```

## Scaling

To add more nodes:

1. Create a new configuration JSON file in the config directory.

2. Update docker-compose.yml with a new service definition for the node.

3. Rebuild and restart the network.

## Limitations

- Communication relies on TCP sockets, which may not scale efficiently for large networks.

- Assumes all nodes are reachable and their configurations are correct.