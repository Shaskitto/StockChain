import socket
import os
from shared.encryption import Encryption

class Client:
    """
    A client class that interacts with a server for sending and receiving encrypted messages.
    Provides methods for registering a user, adding transactions, copying data, and verifying.
    
    Attributes:
        host (str): The server host address.
        port (int): The server port number.
        socket (socket.socket): The client socket for communication.
        public_key (str): The public key used for encrypting messages.
        client_id (str or None): The ID assigned to the client upon registration.
        username (str or None): The username of the client.
    """
    
    def __init__(self, host='localhost', port=5000):
        """
        Initializes the client with the given server host and port, and sets up the socket connection.
        Loads the public key for encryption.
        
        Args:
            host (str): The server's host address (default is 'localhost').
            port (int): The server's port number (default is 5000).
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.public_key = Encryption.load_key('server_public_key.pem')
        self.client_id = None
        self.username = None

    def send_message(self, message):
        """
        Encrypts and sends a message to the server.
        
        Args:
            message (str): The message to send to the server.
        """
        encrypted_message = Encryption.encrypt_message(self.public_key, message)
        self.socket.send(encrypted_message)

    def receive_message(self):
        """
        Receives and decrypts a message from the server.
        
        Returns:
            str: The decrypted message from the server.
        """
        encrypted_message = self.socket.recv(1024)
        return Encryption.decrypt_message(Encryption.load_key('server_private_key.pem'), encrypted_message)

    def register(self, username):
        """
        Registers the client with the given username and receives a client ID.
        
        Args:
            username (str): The username to register with.
        """
        self.send_message(f'register {username}')
        response = self.receive_message()
        self.client_id = response
        self.username = username
        print(f'Server Response: {self.client_id}\n')

    def add_transaction(self, username, action, stock_name):
        """
        Adds a transaction for a specific user with a given action and stock name.
        
        Args:
            username (str): The username associated with the transaction.
            action (str): The action to perform (e.g., 'buy' or 'sell').
            stock_name (str): The name of the stock involved in the transaction.
        """
        transaction = f'add {username} {action} {stock_name}'
        self.send_message(transaction)
        response = self.receive_message()
        print(f'Server Response: {response}\n')

    def copy(self, username=None):
        """
        Requests a copy of transactions for a specific username or all transactions if no username is provided.
        
        Args:
            username (str, optional): The username to get transactions for. Defaults to None for all transactions.
        """
        if username:
            self.send_message(f'copy {username}')
            response = self.receive_message()
            print(f'Server Response: Copy Response for {username}: {response}\n')
        else:
            self.send_message('copy')
            response = self.receive_message()
            print(f'Server Response: Copy Response (All Transactions): {response}\n')

    def verify(self):
        """
        Verifies the client's current status with the server.
        """
        self.send_message('verify')
        response = self.receive_message()
        print(f'Server Response: Verify Response: {response}\n')

    def interactive_mode(self):
        """
        Starts an interactive command-line interface for the client to interact with the server.
        Allows users to register, add transactions, copy data, verify, and exit.
        """
        while True:
            print("Client Commands: 'register <username>', 'add <username> <action> <stock>', 'copy [<username>]', 'verify', 'exit'")
            command = input("Enter command: ")
            
            if command == 'exit':
                print("Exiting client...")
                self.socket.close()
                break
            elif command.startswith('register'):
                parts = command.split(' ')
                if len(parts) == 2:
                    self.register(parts[1])
                else:
                    print("Invalid 'register' command. Usage: register <username>\n")
            elif command.startswith('add'):
                parts = command.split(' ')
                if len(parts) == 4:
                    self.add_transaction(parts[1], parts[2], parts[3])
                else:
                    print("Invalid 'add' command. Usage: add <username> <action> <stock>\n")
            elif command.startswith('copy'):
                parts = command.split(' ')
                if len(parts) == 2:
                    self.copy(parts[1])
                elif len(parts) == 1:
                    self.copy()
                else:
                    print("Invalid 'copy' command. Usage: copy [<username>]\n")
            elif command.startswith('verify'):
                self.verify()
            else:
                print("Unknown command. Try again.\n")

if __name__ == "__main__":
    client = Client()
    client.interactive_mode()