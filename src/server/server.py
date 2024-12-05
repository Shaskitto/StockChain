import os
import json
import socket
import threading
from server.blockchain import Blockchain
from shared.encryption import Encryption

class Server:
    """
    Class representing a server that handles communication with clients,
    registers users, handles transactions, and creates blocks in a blockchain.
    The server listens on a specified port, processes commands from clients
    and manages the integrity of the blockchain.

    Attributes:
        host (str): Address of the host where the server will listen.
        port (int): The port on which the server will listen for connections.
        server_socket (socket.socket): The server socket to accept connections.
        blockchain (Blockchain): The instance of the Blockchain class that handles transactions and blocks.
        private_key (str): The private key used for message encryption.
        base_path (str): The server base path for data files.
        users_data_path (str): Directory where user data is stored.
        users_file (str): Path to the JSON file containing registered users.
        users (dict): Dictionary containing users and their ids.
    """
    
    def __init__(self, host='localhost', port=5000):
        """
        Initializes the server, configures the socket, loads the blockchain and user data.

        Args:
            host (str): Host address (default 'localhost').
            port (int): Port where the server will listen for connections (default 5000).
        """
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.blockchain = Blockchain()
        self.private_key = Encryption.load_key('server_private_key.pem')

        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server'))
        
        self.users_data_path = os.path.join(self.base_path, 'users_data')
        
        if not os.path.exists(self.users_data_path):
            os.makedirs(self.users_data_path)
        
        self.users_file = os.path.join(self.users_data_path, 'users.json')
        self.users = self.load_users()

    def load_users(self):
        """
        Loads user data from a JSON file. If the file does not exist, returns an empty dictionary.

        Returns:
            dict: User dictionary loaded from file, or empty if it does not exist.
        """
        if not os.path.exists(self.users_file):
            return {}  
        with open(self.users_file, 'r') as file:
            return json.load(file)

    def save_users(self):
        """
        Saves user data to a JSON file.

        """
        with open(self.users_file, 'w') as file:
            json.dump(self.users, file, indent=4)

    def handle_client(self, client_socket):
        """
        Handles communication with a client. Receives commands from the client, processes them, and sends responses.

        Args:
            client_socket (socket.socket): The client connection socket.
        """
        while True:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            message = Encryption.decrypt_message(self.private_key, encrypted_message)
            print(f'Received: {message}')
            command_parts = message.split(' ')

            if command_parts[0] == 'register':
                self.handle_register(command_parts[1], client_socket)
            
            elif command_parts[0] == 'add':
                self.handle_add_transaction(command_parts[1:], client_socket)
            
            elif command_parts[0] == 'copy':
                self.handle_copy_transactions(command_parts, client_socket)
            
            elif command_parts[0] == 'verify':
                self.handle_verify_integrity(client_socket)
            
            else:
                client_socket.send(Encryption.encrypt_message(self.private_key, 'Unknown command'))

    def handle_register(self, username, client_socket):
        """
        Handles the registration of a new user.

        Args:
            username (str): The username attempting to register.
            client_socket (socket.socket): The client connection socket.
        """
        if username in self.users:
            response = 'Username already taken'
        else:
            client_id = str(len(self.users) + 1)
            self.users[username] = client_id
            self.save_users()
            response = f'Registered with ID: {client_id}'
        
        client_socket.send(Encryption.encrypt_message(self.private_key, response))

    def handle_add_transaction(self, command_parts, client_socket):
        """
        Handles adding a new transaction to the blockchain.

        Args:
            command_parts (list): The list of command parts containing the username,
            operation type, and action name of the transaction.
            client_socket (socket.socket): The client connection socket.
        """
        username = command_parts[0]
        if username not in self.users:
            client_socket.send(Encryption.encrypt_message(self.private_key, 'Username not registered'))
        else:
            client_id = self.users[username]
            transaction = {
                'user_id': client_id,
                'operation_type': command_parts[1],
                'stock_name': command_parts[2]
            }

            if not self.blockchain.is_valid_transaction(transaction):
                response = 'Invalid transaction. Ensure operation type is "buy" or "sell".'
                client_socket.send(Encryption.encrypt_message(self.private_key, response))
                return
        
            self.blockchain.add_transaction(transaction)
            print(f"Transaction added: {transaction}")
            
            last_block = self.blockchain.last_block
            proof = self.blockchain.proof_of_work(last_block['proof'])
            previous_hash = self.blockchain.hash(last_block)
            
            self.blockchain.create_block(proof, previous_hash)
            print(f"Block created")
            client_socket.send(Encryption.encrypt_message(self.private_key, 'Transaction added'))

    def handle_copy_transactions(self, command_parts, client_socket):
        """
        Handles copying transactions for a specific user or for all users.

        Args:
            command_parts (list): The list of command parts, which may contain the user name.
            client_socket (socket.socket): The client connection socket.
        """
        if len(command_parts) == 2:
            self.copy_user_transactions(command_parts[1], client_socket)
        elif len(command_parts) == 1:
            self.copy_all_transactions(client_socket)
        else:
            response = 'Invalid copy command. Usage: copy [<username>]'
            client_socket.send(Encryption.encrypt_message(self.private_key, response))

    def copy_user_transactions(self, username, client_socket):
        """
        Copies the transactions of a specific user to a JSON file.

        Args:
            username (str): The username whose transactions will be copied.
            client_socket (socket.socket): The client connection socket.
        """
        if username not in self.users:
            client_socket.send(Encryption.encrypt_message(self.private_key, 'Username not registered'))
        else:
            client_id = self.users[username]
            user_transactions = []

            for block in self.blockchain.chain:
                if isinstance(block['data'], list):  
                    for transaction in block['data']:
                        if isinstance(transaction, dict) and transaction.get('user_id') == client_id:
                            transaction_info = {
                                'transaction': transaction,
                                'block_info': {
                                    'timestamp': block['timestamp'],
                                    'previous_hash': block['previous_hash'],
                                    'proof': block['proof'],
                                    'hash': block['hash']
                                }
                            }
                            user_transactions.append(transaction_info)

            if user_transactions:
                file_path = f"transactions_{username}.json"
                with open(file_path, 'w') as file:
                    json.dump(user_transactions, file, indent=4)

                response = f'Transactions copied for user {username} and saved to {file_path}'
            else:
                response = 'No transactions found for this user.'
        
            client_socket.send(Encryption.encrypt_message(self.private_key, response))

    def copy_all_transactions(self, client_socket):
        """
        Copies all transactions from the blockchain to a JSON file.

        Args:
            client_socket (socket.socket): The client connection socket.
        """
        all_transactions = []

        for block in self.blockchain.chain:
            if isinstance(block['data'], list):  
                for transaction in block['data']:
                    if isinstance(transaction, dict):
                        transaction_info = {
                            'transaction': transaction,
                            'block_info': {
                                'timestamp': block['timestamp'],
                                'previous_hash': block['previous_hash'],
                                'proof': block['proof'],
                                'hash': block['hash']
                            }
                        }
                        all_transactions.append(transaction_info)

        if all_transactions:
            file_path = "transactions_all_users.json"
            with open(file_path, 'w') as file:
                json.dump(all_transactions, file, indent=4)

            response = f'All transactions copied and saved to {file_path}'
        else:
            response = 'No transactions found.'
        
        client_socket.send(Encryption.encrypt_message(self.private_key, response))

    def handle_verify_integrity(self, client_socket):
        """
        Verifies the integrity of the blockchain and responds to the client.

        Args:
            client_socket (socket.socket): The client connection socket.
        """
        is_valid = self.blockchain.verify_integrity()
        if is_valid:
            response = 'The blockchain is valid and has not been altered.'
        client_socket.send(Encryption.encrypt_message(self.private_key, response))

    def start(self):
        """
        Starts the server, starting to listen for client connections and assigning
        threads to handle each connection.
        """
        print(f'Server listening on {self.host}:{self.port}')
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f'Connection from {client_address}')
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    server = Server()
    server_thread = threading.Thread(target=server.start)
    server_thread.start()