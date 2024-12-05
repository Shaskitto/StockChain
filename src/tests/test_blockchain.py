import pytest
import json
import os
import shutil
from tempfile import mkdtemp
from server.blockchain import Blockchain

@pytest.fixture
def temp_blockchain():
    """
    Fixture that creates a temporary blockchain in a folder called 'temp_blockchain'.

    This fixture configures an instance of the Blockchain class using a temporary
    directory to store the blocks. At the end of each test, the temporary directory is
    automatically deleted.

    Returns:
        Blockchain: Instance of the Blockchain class configured for testing.
    """
    temp_dir = mkdtemp(prefix="temp_blockchain_") 

    blockchain = Blockchain()
    blockchain.blockchain_dir = temp_dir  
    blockchain.load_chain_from_json()
    yield blockchain
    shutil.rmtree(temp_dir)
    
def test_create_genesis_block(temp_blockchain):
    """
    Test to verify the creation of a genesis block.

    This test ensures that the genesis block is created correctly and is not recreated if it already exists on the chain. It also validates the properties of the genesis block.

    Args:
    temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    
    blockchain.create_genesis_block()
    existing_genesis = blockchain.chain[0]
    
    blockchain.create_genesis_block()

    assert blockchain.chain[0] == existing_genesis

    genesis_block = blockchain.chain[0]
    assert genesis_block['index'] == 0
    assert isinstance(genesis_block['timestamp'], str)
    assert genesis_block['data'] == 'Genesis Block'
    assert genesis_block['previous_hash'] == '0'
    assert genesis_block['proof'] == 100
    assert 'hash' in genesis_block

def test_proof_of_work(temp_blockchain):
    """
    Test to verify the 'proof of work' calculation.

    Ensures that the 'proof_of_work' method returns a valid proof value
    and of type integer.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    assert proof is not None
    assert isinstance(proof, int)

def test_create_block(temp_blockchain):
    """
    Test to verify the creation of a new block in the blockchain.

    Validates that the creation of a block correctly updates the chain,
    incrementing the block index.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(proof, previous_hash)
    assert block['index'] == last_block['index'] + 1

def test_verify_integrity(temp_blockchain):
    """
    Test to verify the integrity of the blockchain.

    This test adds a transaction to the blockchain and then verifies that the integrity of the chain is valid.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    blockchain.add_transaction({'user_id': '1', 'operation_type': 'buy', 'stock_name': 'AAPL'})
    assert blockchain.verify_integrity() == True

def test_is_valid_chain(temp_blockchain):
    """
    Test to verify if the blockchain is valid.

    This test validates that the blockchain is not empty and is considered valid.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain

    assert len(blockchain.chain) > 0
    assert blockchain.is_valid_chain() == True

def test_add_transaction(temp_blockchain):
    """
    Test to add a transaction to the blockchain.

    Validates that an added transaction is correctly recorded in the list of pending transactions.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    
    transaction = {'user_id': '1', 'operation_type': 'buy', 'stock_name': 'AAPL'}
    blockchain.add_transaction(transaction)
    
    assert len(blockchain.current_transactions) == 1
    assert blockchain.current_transactions[0] == transaction

def test_add_block_increases_chain_length(temp_blockchain):
    """
    Test to verify that adding a block increases the chain length.

    This test ensures that every time a block is added to the chain,
    its length increases by one.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    initial_length = len(blockchain.chain)
    
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    previous_hash = blockchain.hash(last_block)
    
    blockchain.create_block(proof, previous_hash)
    
    assert len(blockchain.chain) == initial_length + 1, (
        f"Expected chain length {initial_length + 1}, got {len(blockchain.chain)}"
    )

def test_calculate_block_hash(temp_blockchain):
    """
    Test to verify the calculation of a block hash.

    Ensures that the 'hash' method calculates a valid hash and that the result
    is a non-empty string.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    block = blockchain.chain[0]
    calculated_hash = blockchain.hash(block)
    
    assert isinstance(calculated_hash, str)
    assert len(calculated_hash) > 0

def test_proof_of_work_calculation(temp_blockchain):
    """
    Test to verify the 'proof of work' calculation.

    This test ensures that the calculated 'proof of work' value is
    an integer and greater than 0.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    
    assert isinstance(proof, int)
    assert proof > 0

def test_add_block(temp_blockchain):
    """
    Test to verify that a new block is successfully added to the blockchain.

    This test ensures that the newly created block is added to the end of the chain.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    previous_hash = blockchain.hash(last_block)
    new_block = blockchain.create_block(proof, previous_hash)
    
    assert new_block in blockchain.chain

def test_empty_chain_before_genesis(temp_blockchain):
    """
    Test to verify that the chain is empty before the creation of the genesis block.

    This test ensures that the blockchain is empty before the creation of the first block.

    Args:
        temp_blockchain (Blockchain): Blockchain instance provided by the fixture.
    """
    blockchain = temp_blockchain
    
    blockchain.chain = [] 
    blockchain.create_genesis_block() 
    assert len(blockchain.chain) == 1
