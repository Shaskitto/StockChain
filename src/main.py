import threading
from server.server import Server  
from client.client import Client
import time

def start_server():
    """
    Starts the server in a separate thread.

    This function creates an instance of the `Server` class and calls its `start()` method to
    start the server in a separate thread. This allows the server to be running
    while communication with the client is taking place.
    """
    server = Server()
    server.start()

def start_client():
    """
    Starts the client after waiting a short period to ensure that the server is up.

    This function waits a few seconds to ensure that the server is fully started
    before starting the client instance. It then calls the client's interactive mode,
    allowing the user to interact with the system.

    This delay is necessary to avoid synchronization problems between server startup
    and client connection.
    """
    time.sleep(1)  
    client = Client()
    client.interactive_mode()

if __name__ == "__main__":
    """
    Start the server and client in separate threads.

    This block of code runs the server in a separate thread using `threading.Thread`
    and then starts the client in the main thread. The `start_server` function runs in a
    background thread to allow both the server and client to run simultaneously.

    The server is started in a separate thread (`daemon=True`), which means that the server
    will automatically stop when the main program terminates.
    """
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    start_client()