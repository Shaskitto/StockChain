import hashlib
import time
import json
import os
from datetime import datetime, timezone

class Blockchain:
    """
    Class to represent a blockchain. This class manages the creation of blocks,
    the addition of transactions, the hashing of blocks, the verification of the chain integrity
    and the storage of blocks as JSON files.

    Attributes:
    chain (list): List of blocks that make up the blockchain.
    current_transactions (list): List of transactions that are waiting to be added to a block.
    blockchain_dir (str): Directory where the JSON files of the blocks are saved.
    """
    
    def __init__(self):
        """
        Initializes the blockchain and loads blocks from existing JSON files.
        If the chain is empty, creates the genesis block.
        """
        self.chain = []
        self.current_transactions = []
        self.blockchain_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blockchain_data')
        
        if not os.path.exists(self.blockchain_dir):
            os.makedirs(self.blockchain_dir)
        
        self.load_chain_from_json()

        if len(self.chain) == 0:
            self.create_genesis_block()

    def create_genesis_block(self):
        """
        Creates the genesis block if it does not exist and saves it as a JSON file.
        """
        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        genesis_block = {
            'index': 0,
            'timestamp': formatted_timestamp, 
            'data': 'Genesis Block',
            'previous_hash': '0',  
            'proof': 100  
        }
        genesis_block['hash'] = self.hash(genesis_block)
        self.chain.append(genesis_block)
        self.save_block_to_json(genesis_block)

    def create_block(self, proof, previous_hash=None):
        """
        Creates a new block and adds it to the chain.

        Args:
            proof (int): The proof of work for this block.
            previous_hash (str, optional): The hash of the previous block (defaults to the calculated one).

        Returns:
            dict: The newly created block.
        """
        if not self.is_valid_chain():
            raise ValueError("Cannot create a block on an invalid blockchain.")
        
        last_block = self.last_block
        calculated_previous_hash = self.hash(last_block) if last_block else '0'
        previous_hash = previous_hash or calculated_previous_hash

        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        block = {
            'index': len(self.chain),
            'timestamp': formatted_timestamp,  
            'data': self.current_transactions,
            'previous_hash': previous_hash,
            'proof': proof
        }
        block['hash'] = self.hash(block)

        self.save_block_to_json(block)
        self.current_transactions = []
        self.chain.append(block)
        return block

    def save_block_to_json(self, block):
        """
        Saves a block as a JSON file in the 'blockchain_data' folder.

        Args:
            block (dict): The block to save.
        """
        block_filename = f"block_{block['index']}.json"
        file_path = os.path.join(self.blockchain_dir, block_filename)

        try:
            with open(file_path, 'w') as f:
                json.dump(block, f, indent=4)
            
        except Exception as e:
            print(f"Error saving block {block['index']}: {e}")


    def add_transaction(self, transaction):
        """
        Adds a new transaction to the transaction list.

        Args:
            transaction (dict): The transaction to add.

        Returns:
            int: The index of the block that will contain this transaction.
        """
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1

    def is_valid_transaction(self, transaction):
        """
        Validates if the transaction is valid.

        Args:
            transaction (dict): The transaction to validate.

        Returns:
            bool: True if the transaction is valid, False otherwise.
        """
        if 'operation_type' not in transaction:
            return False
        
        if transaction['operation_type'] not in ['buy', 'sell']:
            return False
        
        if 'stock_name' not in transaction or not transaction['stock_name']:
            return False
        
        return True
    
    def hash(self, block):
        """
        Returns the hash of a block.

        Args:
            block (dict): The block to hash.

        Returns:
            str: The hash of the block.
        """
        block_copy = block.copy()
        block_copy.pop('hash', None)  
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Performs the proof-of-work process to find a valid proof.

        Args:
            last_proof (int): The proof of the previous block.

        Returns:
            int: The proof that solves the problem.
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        """
        Checks if a proof is valid.

        Args:
            last_proof (int): The proof of the previous block.
            proof (int): The new proof to verify.

        Returns:
            bool: True if the proof is valid, False otherwise.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def is_valid_chain(self):
        """
        Checks the integrity of the blockchain.

        Returns:
            bool: True if the chain is valid, False if it has integrity issues.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block['previous_hash'] != previous_block['hash']:
                return False
            
            for transaction in current_block['data']:
                if not self.is_valid_transaction(transaction):
                    return False
        return True

    def verify_integrity(self):
        """
        Checks the integrity of all blocks in the chain.
        If any block has an incorrect hash, it recalculates it and saves it again.

        Returns:
            bool: True if the integrity is valid, False otherwise.
        """
        current_block = self.chain[0]  
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            recalculated_previous_hash = self.hash(current_block)

            if block['previous_hash'] != recalculated_previous_hash:
                print(f"Error: Recalculating block {block['index']}.")
                block['previous_hash'] = recalculated_previous_hash  

                block['hash'] = self.hash(block)
                
                self.chain[block_index] = block  

                self.save_block_to_json(block)

            current_block = block
            block_index += 1

        return True

    def load_chain_from_json(self):
        """
        Loads blocks from JSON files and verifies their integrity.
        If the hashes do not match, updates the block with the recalculated hash.
        """
        if os.path.exists(self.blockchain_dir):
            for filename in sorted(os.listdir(self.blockchain_dir)):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.blockchain_dir, filename)
                    with open(file_path, 'r') as f:
                        block = json.load(f)
                        
                        self.chain.append(block)
    
    @property
    def last_block(self):
        """
        Returns the last block of the chain.

        Returns:
            dict: The last block of the chain, or None if the chain is empty.
        """
        return self.chain[-1] if self.chain else None