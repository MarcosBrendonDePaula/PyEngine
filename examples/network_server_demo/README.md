# Network Server Demo

This example demonstrates a basic network server that manages connections from multiple clients and synchronizes their states.

## How to Run

Install the engine with:

```bash
pip install pyengine
```

Then run:

```bash
python3 examples/network_server_demo/network_server.py [--host <host>] [--port <port>]
```

## Features

- Accepts multiple client connections.
- Broadcasts player position updates to all connected clients.


