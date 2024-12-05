import pytest
from unittest import mock
from client.client import Client
import socket

@pytest.fixture
def mock_socket():
    """
    A fixture that creates a socket mock to simulate the creation of a network connection.

    Uses `mock.patch` to intercept the creation of a socket and return a mock object
    to simulate interaction with the server without the need to establish an actual connection.

    Returns:
        mock.Mock: A mock object that replaces `socket.socket` in tests.
    """
    with mock.patch('socket.socket') as mock_socket:
        yield mock_socket

def test_client_connection(mock_socket):
    """
    Test that verifies the correct creation and connection of the socket on the client.

    This test verifies that the `Client` connects to the server using the mocked socket.
    It verifies that the socket has been created with the correct settings (AF_INET and SOCK_STREAM)
    and that the `connect` method has been called with the correct address ('localhost', 5000).

    Args:
        mock_socket (mock. Mock): The socket mock to simulate the connection.
    """
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.connect = mock.MagicMock()

    client = Client()

    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    mock_socket_instance.connect.assert_called_once_with(('localhost', 5000))

def test_send_message(mock_socket):
    """
    Test that verifies the sending of an encrypted message from the client.

    This test verifies that the message is correctly encrypted before being sent through the
    socket. It uses a mock for the `Encryption` class to simulate the encryption of the message.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()
        message = "Test message"

        client.send_message(message)

        mock_encrypt.assert_called_once_with(client.public_key, message)
        
        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

def test_register(mock_socket):
    """
    Test that verifies the registration of a new user on the client.

    This test simulates the registration process of a new user, where the client sends a
    registration message to the server. It verifies that the message has been encrypted and sent,
    and that the `client_id` and `username` are correctly updated on the client.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_encrypt.return_value = b'encrypted_message'
        mock_decrypt.return_value = '1234'  

        client = Client()

        client.register('testuser')

        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

        assert client.client_id == '1234'
        assert client.username == 'testuser'

def test_add_transaction(mock_socket):
    """
    Test that verifies the process of adding a transaction.

    This test simulates the addition of a transaction from the client. It verifies that the transaction
    is correctly encrypted, sent, and that the client receives the appropriate response from the server.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_decrypt.return_value = 'Transaction Added'
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()

        client.add_transaction('testuser', 'buy', 'AAPL')

        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

        assert mock_decrypt.call_count == 1

def test_verify(mock_socket):
    """
    Test that verifies the blockchain verification by the client.

    This test simulates the process of blockchain verification by the client, sending a
    message to the server and ensuring that the verification response is as expected.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_decrypt.return_value = 'Chain Verified'
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()

        client.verify()

        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

        assert mock_decrypt.call_count == 1

def test_receive_error(mock_socket):
    """
    Test that simulates an error in receiving a message and verifies proper handling.

    This test simulates an exception during message reception (for example, if decryption fails) and verifies that an exception is thrown on the client.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in testing.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt:
        mock_decrypt.side_effect = Exception("Decryption failed")

        client = Client()

        with pytest.raises(Exception):
            client.receive_message()

def test_interactive_mode(mock_socket):
    """
    Test that verifies the operation of the interactive mode of the client.

    This test simulates the interaction with the client in interactive mode, verifying that the
    client closes correctly when the 'exit' command is entered.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('builtins.input', return_value='exit'), \
         mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt:
        
        mock_decrypt.return_value = 'Exit command received'

        client = Client()

        client.interactive_mode()

        mock_socket.return_value.close.assert_called_once()

def test_copy_all_transactions(mock_socket):
    """
    Test that verifies the copying of all transactions from the server.

    This test simulates the copying of all transactions and verifies that the client receives
    the expected response from the server and that the message is sent correctly.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_decrypt.return_value = 'All transactions copied'
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()

        client.copy()

        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

        assert mock_decrypt.call_count == 1


def test_copy_user_transaction(mock_socket):
    """
    Test that verifies the copying of a specific user's transactions from the server.

    This test simulates the copying of a specific user's transactions. It verifies that the copy request message for a user (in this case, 'testuser') 
    is sent correctly and that the server's response is as expected.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_decrypt.return_value = 'User transactions copied'
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()

        client.copy('testuser')

        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

        assert mock_decrypt.call_count == 1


def test_recieve_id(mock_socket):
    """
    Test that verifies that the client receives a user ID after registration.

    This test simulates a user registration and verifies that the client receives an ID (in this case,
    '1234') from the server. The test also verifies that the received ID is stored correctly
    on the client.

    Args:
    mock_socket (mock. Mock): The mock of the socket used in testing.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_decrypt.return_value = '1234'
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()

        client.register('testuser')

        assert client.client_id == '1234'


def test_send_encrypted_transaction(mock_socket):
    """
    Test that verifies the sending of an encrypted transaction from the client.

    This test simulates the process of sending a transaction from the client. It verifies that the transaction
    is encrypted correctly before being sent to the server, and that the server responds appropriately.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_decrypt.return_value = 'Transaction added'
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()

        client.add_transaction('testuser', 'buy', 'AAPL')

        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

        assert mock_decrypt.call_count == 1


def test_send_transaction_with_missing_fields(mock_socket):
    """
    Test that verifies the handling of a transaction with missing fields.

    This test simulates the sending of a transaction with a missing field (for example, empty stock),
    and verifies that the client receives an appropriate error response from the server.

    Args:
        mock_socket (mock. Mock): The mock of the socket used in the tests.
    """
    with mock.patch('shared.encryption.Encryption.decrypt_message') as mock_decrypt, \
         mock.patch('shared.encryption.Encryption.encrypt_message') as mock_encrypt:

        mock_decrypt.return_value = 'Error: Missing fields'
        mock_encrypt.return_value = b'encrypted_message'

        client = Client()

        client.add_transaction('testuser', 'buy', '')  

        mock_socket.return_value.send.assert_called_once_with(b'encrypted_message')

        assert mock_decrypt.call_count == 1
        assert 'Error: Missing fields' in mock_decrypt.return_value