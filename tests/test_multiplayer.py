import time
from engine.multiplayer import DedicatedServer, Client, SyncComponent
from engine.core.entity import Entity


def test_server_client_broadcast():
    server = DedicatedServer(port=0)
    server.start()
    port = server.sock.getsockname()[1]

    received = []
    client1 = Client('p1', '127.0.0.1', port)
    client2 = Client('p2', '127.0.0.1', port)
    client2.recv_callback = lambda msg: received.append(msg)

    client1.start()
    client2.start()

    # allow join messages to propagate
    for _ in range(20):
        time.sleep(0.01)
        if server.clients:
            break

    client1.send_update({'x': 5})

    for _ in range(50):
        time.sleep(0.01)
        if any(m.get('cmd') == 'update' for m in received):
            break

    client1.stop()
    client2.stop()
    server.stop()

    assert any(m.get('cmd') == 'update' and m.get('data', {}).get('x') == 5 for m in received)


def test_host_flag_in_join():
    server = DedicatedServer(port=0)
    server.start()
    port = server.sock.getsockname()[1]

    join_messages = []

    def on_recv(msg):
        if msg.get('cmd') == 'join':
            join_messages.append(msg)

    client_host = Client('host-player', '127.0.0.1', port, is_host=True)
    client_listener = Client('listener', '127.0.0.1', port)
    client_listener.recv_callback = on_recv

    client_listener.start()
    client_host.start()

    for _ in range(50):
        time.sleep(0.01)
        if join_messages:
            break

    client_host.stop()
    client_listener.stop()
    server.stop()

    assert any(m.get('player') == 'host-player' and m.get('host') is True for m in join_messages)


def test_sync_component_auto_attrs():
    server = DedicatedServer(port=0)
    server.start()
    port = server.sock.getsockname()[1]

    received = []
    listener = Client('listener', '127.0.0.1', port)
    listener.recv_callback = lambda m: received.append(m)
    listener.start()

    client = Client('p1', '127.0.0.1', port)
    entity = Entity()
    entity.add_component(SyncComponent(client))

    # allow join message to propagate
    for _ in range(50):
        time.sleep(0.01)
        if any(m.get('cmd') == 'join' and m.get('player') == 'p1' for m in received):
            break

    entity.position.x = 12
    entity.position.y = 34
    entity.tick()

    for _ in range(50):
        time.sleep(0.01)
        if any(m.get('cmd') == 'update' and m.get('data', {}).get('position.x') == 12 for m in received):
            break

    entity.remove_component(SyncComponent)
    listener.stop()
    server.stop()

    assert any(
        m.get('cmd') == 'update'
        and m.get('data', {}).get('position.x') == 12
        and m.get('data', {}).get('position.y') == 34
        for m in received
    )


def test_new_client_receives_existing_players():
    server = DedicatedServer(port=0)
    server.start()
    port = server.sock.getsockname()[1]

    client1 = Client('p1', '127.0.0.1', port)
    client1.start()

    # wait for server to register client1
    for _ in range(50):
        time.sleep(0.01)
        if server.clients:
            break

    received = []
    client2 = Client('p2', '127.0.0.1', port)
    client2.recv_callback = lambda m: received.append(m)
    client2.start()

    # wait for join messages about p1
    for _ in range(50):
        time.sleep(0.01)
        if any(m.get('cmd') == 'join' and m.get('player') == 'p1' for m in received):
            break

    client1.stop()
    client2.stop()
    server.stop()

    assert any(m.get('cmd') == 'join' and m.get('player') == 'p1' for m in received)
