import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class Encryption:
    """
    Class that provides static methods for generating RSA keys, saving and loading keys,
    and encrypting/decrypting messages using RSA with the OAEP padding scheme.
    """

    @staticmethod
    def generate_keys(key_size=2048):
        """
        Generates an RSA key pair (public and private).

        Args:
            key_size (int): The size of the keys in bits. Default is 2048 bits.

        Returns:
            tuple: A tuple containing the generated private key and public key.
        """
        private_key = RSA.generate(key_size)  
        public_key = private_key.publickey()  
        return private_key, public_key

    @staticmethod
    def save_key(key, filename):
        """
        Saves an RSA key (public or private) to a file.

        Args:
            key (RSA.RsaKey): The key to save (can be public or private).
            filename (str): The name of the file where the key will be saved.
        """
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server'))
        keys_dir = os.path.join(base_path, 'keys')
        
        if not os.path.exists(keys_dir):
            os.makedirs(keys_dir)
        
        file_path = os.path.join(keys_dir, filename)
        
        with open(file_path, 'wb') as file:
            file.write(key.export_key())

    @staticmethod
    def load_key(filename):
        """
        Loads an RSA key from a file. If the file does not exist, generates new keys.

        Args:
            filename (str): The name of the file containing the key to be loaded.

        Returns:
            RSA.RsaKey: The key loaded from the file.
        """
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server'))
        keys_dir = os.path.join(base_path, 'keys')
        file_path = os.path.join(keys_dir, filename)
        
        if not os.path.exists(file_path):
            private_key, public_key = Encryption.generate_keys()
            Encryption.save_key(private_key, 'server_private_key.pem')
            Encryption.save_key(public_key, 'server_public_key.pem')
        
        with open(file_path, 'rb') as file:
            key = RSA.import_key(file.read())
        return key

    @staticmethod
    def encrypt_message(public_key, message):
        """
        Encrypts a message using an RSA public key and the OAEP padding scheme.

        Args:
            public_key (RSA.RsaKey): The RSA public key used to encrypt the message.
            message (str): The cleartext message to be encrypted.

        Returns:
            bytes: The encrypted message.
        """
        cipher = PKCS1_OAEP.new(public_key)  
        encrypted_message = cipher.encrypt(message.encode())  
        return encrypted_message

    @staticmethod
    def decrypt_message(private_key, encrypted_message):
        """
        Decrypts a message using an RSA private key and the OAEP padding scheme.

        Args:
            private_key (RSA.RsaKey): The RSA private key used to decrypt the message.
            encrypted_message (bytes): The encrypted message to be decrypted.

        Returns:
            str: The decrypted message in clear text.
        """
        cipher = PKCS1_OAEP.new(private_key)  
        decrypted_message = cipher.decrypt(encrypted_message).decode() 
        return decrypted_message