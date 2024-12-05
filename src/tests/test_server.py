import socket
import pytest
import random
import string
from shared.encryption import Encryption

SERVER_HOST = 'localhost'
SERVER_PORT = 5000
PUBLIC_KEY_PATH = 'server_public_key.pem'
PRIVATE_KEY_PATH = 'server_private_key.pem'

def connect_to_server():
    """
    Establishes a connection to the server and loads the public and private keys needed for encryption.

    This function creates a client socket that connects to the server at the addresses defined by
    SERVER_HOST and SERVER_PORT. It then loads the public and private keys needed for
    encryption and decryption operations.

    Returns:
        tuple: A connected socket client, loaded public key, and loaded private key.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    public_key = Encryption.load_key(PUBLIC_KEY_PATH)
    private_key = Encryption.load_key(PRIVATE_KEY_PATH)
    return client_socket, public_key, private_key

def send_and_receive(socket, public_key, private_key, message):
    """
    Sends an encrypted message to the server and receives the decrypted response.

    This function encrypts the message using the public key, sends it to the server over the socket,
    and then receives the response, which is decrypted using the private key.

    Args:
        socket (socket.socket): The client socket connected to the server.
        public_key (RSA.RsaKey): The public key to encrypt the message.
        private_key (RSA.RsaKey): The private key to decrypt the response.
        message (str): The message to be sent to the server.

    Returns:
        str: The decrypted response from the server.
    """
    encrypted_message = Encryption.encrypt_message(public_key, message)
    socket.send(encrypted_message)
    encrypted_response = socket.recv(1024)
    return Encryption.decrypt_message(private_key, encrypted_response)

def test_register_existing_user():
    """
    Verifies that the server responds correctly when attempting to register an existing username.

    This test simulates an attempt to register a user whose username is already taken
    and ensures that the server responds with the appropriate message.

    Asserts:
        'Username already taken' - Expected response from the server when the user already exists.
    """
    client_socket, public_key, private_key = connect_to_server()
    try:
        response = send_and_receive(client_socket, public_key, private_key, "register Shaskitto")
        assert response == "Username already taken", f"Expected 'Username already taken', got '{response}'"
    finally:
        client_socket.close()

def generate_random_username():
    """
    Generates a random 8-character alphanumeric username.

    Uses alphabetic and numeric characters to generate a random string
    of length 8, which is useful for tests that require unique usernames.

    Returns:
        str: A random 8-character username.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def test_register_new_user():
    """
    Verifies that the server successfully registers a new user.

    This test generates a random username, attempts to register that name
    on the server, and validates that the server has responded with a message confirming
    the creation of the user.

    Asserts:
        'Registered with ID' - Expected response indicating that the registration was successful.
    """
    client_socket, public_key, private_key = connect_to_server()
    try:
        username = generate_random_username() 
        response = send_and_receive(client_socket, public_key, private_key, f"register {username}")
        assert "Registered with ID" in response, f"Expected registration response, got '{response}'"
    finally:
        client_socket.close()


def test_add_transaction_existing_user():
    """
    Verifies that the server accepts and processes a transaction from an already registered user.

    This test simulates sending a transaction for an existing user, in this case 'Shaskitto',
    and validates that the server responds confirming the addition of the transaction.

    Asserts:
    'Transaction added' - Expected response from the server when processing the transaction.
    """
    client_socket, public_key, private_key = connect_to_server()
    try:
        response = send_and_receive(client_socket, public_key, private_key, "add Shaskitto buy AAPL")
        assert response == "Transaction added", f"Expected 'Transaction added', got '{response}'"
    finally:
        client_socket.close()

def test_copy_transactions_user():
    """
    Verifies that the server correctly copies the transactions of a registered user.

    This test simulates the request to copy the transactions of an existing user, in this case 'Shaskitto',
    and validates that the server responds confirming the action.

    Asserts:
        'Transactions copied' - Expected response from the server when copying the transactions.
    """
    client_socket, public_key, private_key = connect_to_server()
    try:
        response = send_and_receive(client_socket, public_key, private_key, "copy Shaskitto")
        assert "Transactions copied" in response, f"Expected success response, got '{response}'"
    finally:
        client_socket.close()

def test_verify_blockchain():
    """
    Verifies that the server can validate the integrity of the blockchain.

    This test requests validation of the blockchain on the server and verifies that the response
    indicates that the blockchain is valid and has not been altered.

    Asserts:
        'The blockchain is valid and has not been altered.' - Expected response when verifying the blockchain.
    """
    client_socket, public_key, private_key = connect_to_server()
    try:
        response = send_and_receive(client_socket, public_key, private_key, "verify")
        assert response == "The blockchain is valid and has not been altered.", \
            f"Expected blockchain validation response, got '{response}'"
    finally:
        client_socket.close()

def test_unknown_command():
    """
    Verifies that the server responds correctly to an unknown command.

    This test simulates the sending of a command not recognized by the server and validates that the server
    responds with the appropriate message indicating that the command is not known.

    Asserts:
        'Unknown command' - Expected response from the server when receiving an unrecognized command.
    """
    client_socket, public_key, private_key = connect_to_server()
    try:
        response = send_and_receive(client_socket, public_key, private_key, "unknown_command")
        assert response == "Unknown command", f"Expected 'Unknown command', got '{response}'"
    finally:
        client_socket.close()