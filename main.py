import random
import time
import json
from web3 import Web3
from mnemonic import Mnemonic

# Define network configurations
NETWORKS = {
    "Arbitrum": "https://arb1.arbitrum.io/rpc",
    "Linea": "https://linea-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",
    "Base": "https://mainnet.base.org/",
    "zkSync": "https://mainnet.era.zksync.io",
    "OP": "https://mainnet.optimism.io/",
}

# Helper functions
def generate_wallet():
    mnemo = Mnemonic("english")
    phrase = mnemo.generate(strength=128)
    private_key = mnemo.to_seed(phrase).hex()[:64]
    account = Web3().eth.account.from_key(private_key)
    return {
        "mnemonic": phrase,
        "private_key": private_key,
        "address": account.address
    }

def get_balance(web3, address):
    return web3.eth.get_balance(address) / 10 ** 18

def send_transaction(web3, private_key, to_address, amount):
    account = web3.eth.account.from_key(private_key)
    nonce = web3.eth.get_transaction_count(account.address)
    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': web3.to_wei(amount, 'ether'),
        'gas': 21000,
        'gasPrice': web3.eth.gas_price
    }
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return web3.to_hex(tx_hash)

def save_to_file(filename, data):
    with open(filename, 'a') as f:
        f.write(data + "\n")

def random_pause():
    pause_duration = random.randint(30, 300)  # Random pause between 30 seconds and 5 minutes
    print(f"Pausing for {pause_duration} seconds...")
    time.sleep(pause_duration)

# User input
num_transactions = int(input("Enter the number of transactions: "))
print("Choose a network:")
print("1: Arbitrum\n2: Linea\n3: Base\n4: zkSync\n5: OP\n6: Random")
network_choice = int(input("Your choice: "))

# Select network
if network_choice == 6:
    selected_network = random.choice(list(NETWORKS.keys()))
else:
    selected_network = list(NETWORKS.keys())[network_choice - 1]

web3 = Web3(Web3.HTTPProvider(NETWORKS[selected_network]))

# Generate wallets
wallets = [generate_wallet() for _ in range(num_transactions)]
for wallet in wallets:
    save_to_file("new privates.txt", wallet["private_key"])
    save_to_file("new mnemonic.txt", wallet["mnemonic"])
    save_to_file("new address.txt", wallet["address"])
    random_pause()

# Load private keys from file
with open("privates.txt", 'r') as f:
    private_keys = [line.strip() for line in f.readlines()]

# Process transactions
transaction_count = 0
while transaction_count < num_transactions:
    for private_key in private_keys:
        account = web3.eth.account.from_key(private_key)
        balance = get_balance(web3, account.address)

        if balance > 0.002:
            print(f"Success: Wallet {account.address} has sufficient balance.")
            target_wallet = wallets[transaction_count % len(wallets)]
            amount_to_send = random.uniform(0.001, 0.002)

            # Send random amount
            tx_hash = send_transaction(web3, private_key, target_wallet["address"], amount_to_send)
            print(f"Transaction sent: {tx_hash}")
            random_pause()

            # Send back maximum from generated wallet
            target_web3 = Web3(Web3.HTTPProvider(NETWORKS[selected_network]))
            target_balance = get_balance(target_web3, target_wallet["address"])
            max_send = target_balance - 0.0005  # Reserve for gas fees

            if max_send > 0:
                return_tx_hash = send_transaction(target_web3, target_wallet["private_key"], account.address, max_send)
                print(f"Returned funds: {return_tx_hash}")
                random_pause()

            transaction_count += 1

        else:
            print(f"Failed: Wallet {account.address} has insufficient balance.")
            random_pause()

        if transaction_count >= num_transactions:
            break
