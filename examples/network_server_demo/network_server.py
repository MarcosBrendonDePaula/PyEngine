from engine.multiplayer import DedicatedServer
import time


def main():
    server = DedicatedServer()
    server.start()
    print(f"Server listening on {server.host}:{server.port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server...")
    server.stop()


if __name__ == "__main__":
    main()
