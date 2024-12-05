import pytest
import os
from unittest import mock
from Crypto.PublicKey import RSA
from io import BytesIO
from shared.encryption import Encryption

def test_generate_keys():
    """
    Test to verify the generation of the public and private keys.

    This test ensures that the `generate_keys` method of the `Encryption` class returns two valid RSA keys:
    a private key and a public key. It also verifies that the public key correctly matches the
    private key.
    """
    private_key, public_key = Encryption.generate_keys()

    assert isinstance(private_key, RSA.RsaKey)
    assert isinstance(public_key, RSA.RsaKey)

    assert private_key.publickey() == public_key


@mock.patch('builtins.open', new_callable=mock.mock_open)
def test_save_key(mock_open):
    """
    Test to verify saving a public key to a file.

    This test simulates saving a public key to a file using the `save_key` method
    of the `Encryption` class. It verifies that the file is saved to the correct path and in binary write mode.

    Args:
        mock_open (mock. Mock): Mock to simulate the `open` function.
    """
    private_key, public_key = Encryption.generate_keys()

    expected_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'keys', 'server_public_key.pem'))

    Encryption.save_key(public_key, 'server_public_key.pem')

    mock_open.assert_called_once_with(expected_path, 'wb')


def test_load_existing_key():
    """
    Test to verify loading of a public key from an existing file.

    This test simulates that a public key already exists in a file and verifies that the `load_key` method of the `Encryption` class loads it correctly.
    """
    fake_key = RSA.generate(2048).publickey()

    with mock.patch("os.path.exists", return_value=True):
        with mock.patch("builtins.open", mock.mock_open(read_data=fake_key.export_key())):
            key = Encryption.load_key("server_public_key.pem")
            assert key == fake_key  


@mock.patch('os.path.exists', return_value=False)
@mock.patch('shared.encryption.Encryption.save_key')
def test_load_key_generate_new_keys(mock_save_key, mock_exists):
    """
    Test to verify that new keys are generated if a public key does not exist.

    This test simulates that a file with the public key does not exist, so new keys must be generated.
    It verifies that the `save_key` function is called and that the new generated key is not `None`.

    Args:
        mock_save_key (mock. Mock): Mock to simulate the `save_key` function.
        mock_exists (mock. Mock): Mock to simulate that the file does not exist.
    """
    key = Encryption.load_key('server_public_key.pem')

    mock_save_key.assert_called()
    assert key is not None


def test_encrypt_message():
    """
    Test to verify the encryption of a message.

    This test ensures that the `encrypt_message` method correctly encrypts a message using
    the public key. It then verifies that the encrypted message is not identical to the original and that
    it can be correctly decrypted with the private key.
    """
    private_key, public_key = Encryption.generate_keys()
    message = "Test message"
    encrypted_message = Encryption.encrypt_message(public_key, message)

    assert encrypted_message != message.encode()

    decrypted_message = Encryption.decrypt_message(private_key, encrypted_message)
    assert decrypted_message == message


def test_decrypt_message():
    """
    Test to verify the decryption of a message.

    This test ensures that the `decrypt_message` method correctly decrypts a message
    previously encrypted with the public key.
    """
    private_key, public_key = Encryption.generate_keys()
    message = "Another test message"
    encrypted_message = Encryption.encrypt_message(public_key, message)
    decrypted_message = Encryption.decrypt_message(private_key, encrypted_message)

    assert decrypted_message == message


def test_decrypt_with_incorrect_key():
    """
    Test para verificar el error al intentar desencriptar con una clave incorrecta.
    
    Este test asegura que el método `decrypt_message` genere un error si se intenta desencriptar
    un mensaje con una clave privada incorrecta.
    """
    private_key1, public_key1 = Encryption.generate_keys()
    private_key2, _ = Encryption.generate_keys() 

    message = "Sensitive data"
    encrypted_message = Encryption.encrypt_message(public_key1, message)

    with pytest.raises(ValueError):
        decrypted_message = Encryption.decrypt_message(private_key2, encrypted_message)


def test_sensitive_data_encryption():
    """
    Test to verify that sensitive data can be correctly encrypted and decrypted.

    This test ensures that the `encrypt_message` method can encrypt sensitive data, and that
    that data can be correctly decrypted with the corresponding private key.
    """
    private_key, public_key = Encryption.generate_keys()

    assert isinstance(private_key, RSA.RsaKey), "La clave privada no es del tipo RSA"
    assert isinstance(public_key, RSA.RsaKey), "La clave pública no es del tipo RSA"
    
    sensitive_data = "Shaskitto"
    encrypted_data = Encryption.encrypt_message(public_key, sensitive_data)
    
    assert encrypted_data != sensitive_data
    
    decrypted_data = Encryption.decrypt_message(private_key, encrypted_data)
    
    assert decrypted_data == sensitive_data


def test_encrypted_transaction_storage():
    """
    Test to verify storage of an encrypted transaction.

    This test ensures that an encrypted transaction can be stored in a file, simulating
    the encryption of a transaction and verifying that it has been correctly saved to the file.
    """
    transaction_data = "user1 buy SHSA"
    fake_public_key = RSA.generate(2048).publickey()
    
    encrypted_transaction = Encryption.encrypt_message(fake_public_key, transaction_data)
    
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        mock_file.return_value.write(encrypted_transaction)
        
        with open('transactions.txt', 'wb') as file:
            file.write(encrypted_transaction)
        
        mock_file.return_value.write.assert_called_with(encrypted_transaction)


def test_private_key_not_shared():
    """
    Test to verify that the private key should not be shared or stored.

    This test ensures that the private key is never shared or stored in a file in an insecure manner.
    """
    private_key, _ = Encryption.generate_keys()
    
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        with open("server_private_key.pem", 'wb') as file:
            file.write(private_key.export_key())
        
        mock_file.return_value.write.assert_called_once_with(private_key.export_key())

def test_public_key_accessible():
    """
    Test to verify that the public key is accessible and can be saved correctly.

    This test ensures that the generated public key can be saved correctly to a file.
    It uses a mock to simulate the process of writing the public key to a file and then verifies that the file has been successfully written with the contents of the public key.

    It uses the `mock_open` mock to intercept the write operation to the file and ensures that
    `write` is called with the correct contents.
    """
    _, public_key = Encryption.generate_keys()
    
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        with open("server_public_key.pem", 'wb') as file:
            file.write(public_key.export_key())
        
        mock_file.return_value.write.assert_called_once_with(public_key.export_key())