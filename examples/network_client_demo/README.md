# Network Client Demo

This example demonstrates a basic network client that connects to a server and synchronizes player movement.

## How to Run

First, ensure you have a network server running (e.g., `network_server.py`).
Install the engine with:

```bash
pip install -e .
# or
pip install pyengine
```

Then run:

```bash
python3 examples/network_client_demo/network_client.py <player_id> [--host <host>] [--port <port>]
```

Replace `<player_id>` with a unique identifier for your player (e.g., `player1`).

## Controls

- **W, A, S, D:** Move your player.

## Features

- Connects to a network server.
- Synchronizes player position with other connected clients.


