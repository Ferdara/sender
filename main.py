import random
import time
import json
from datetime import datetime
from web3 import Web3
from mnemonic import Mnemonic
from eth_account import Account

Account.enable_unaudited_hdwallet_features()

# Define network configurations
NETWORKS = {
    "Arbitrum": "https://arb1.arbitrum.io/rpc",
    "Base": "https://mainnet.base.org/",
    "zkSync": "https://mainnet.era.zksync.io",
    "OP": "https://mainnet.optimism.io/",
}

# Helper functions
def generate_wallet():
    mnemo = Mnemonic("english")
    phrase = mnemo.generate(strength=128)
    acct = Account.from_mnemonic(phrase)
    return {
        "mnemonic": phrase,
        "private_key": acct._private_key.hex(),
        "address": acct.address
    }

def get_balance(web3, address):
    return web3.eth.get_balance(address) / 10 ** 18

def send_transaction(web3, private_key, to_address, amount):
    try:
        account = web3.eth.account.from_key(private_key)
        nonce = web3.eth.get_transaction_count(account.address)
        gas_price = web3.eth.gas_price
        gas_limit = 21000

        # Estimate gas fee in wei
        gas_fee_estimate = gas_limit * gas_price

        # Convert amount to wei
        amount_in_wei = web3.to_wei(amount, 'ether')

        # Check if the balance is sufficient for the transaction
        balance = web3.eth.get_balance(account.address)  # Balance in wei
        total_cost = gas_fee_estimate + amount_in_wei
        if balance < total_cost:
            raise ValueError(f"Insufficient funds for transaction. Balance: {balance / 10**18} ETH, Required: {total_cost / 10**18} ETH")

        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_in_wei,
            'gas': gas_limit,
            'gasPrice': gas_price
        }
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return web3.to_hex(tx_hash)
    except ValueError as e:
        log_message(f"Transaction failed: {e}")
        raise

def save_to_file(filename, data):
    with open(filename, 'a') as f:
        f.write(data + "\n")

def log_message(message):
    with open("Log.txt", 'a') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def initialize_log_file():
    try:
        with open("Log.txt", 'r') as log_file:
            if log_file.read().strip():
                with open("Log.txt", 'a') as log_file:
                    log_file.write("\n------------------\n")
    except FileNotFoundError:
        with open("Log.txt", 'w') as log_file:
            log_file.write("")

def random_pause():
    pause_duration = random.randint(5, 7)  # Random pause between 5 and 7 seconds
    log_message(f"Pausing for {pause_duration} seconds...")
    time.sleep(pause_duration)

# Initialize log file
initialize_log_file()

# User input
num_transactions = int(input("Enter the number of transactions: "))
log_message(f"User requested {num_transactions} transactions.")

print("Choose a network:")
print("1: Arbitrum\n2: Base\n3: zkSync\n4: OP\n5: Random")
network_choice = int(input("Your choice: "))

# Select network
if network_choice == 5:
    selected_network = random.choice(list(NETWORKS.keys()))
else:
    selected_network = list(NETWORKS.keys())[network_choice - 1]

log_message(f"Selected network: {selected_network}")
web3 = Web3(Web3.HTTPProvider(NETWORKS[selected_network]))

# Generate wallets
wallets = [generate_wallet() for _ in range(num_transactions)]
for wallet in wallets:
    save_to_file("new_privates.txt", wallet["private_key"])
    save_to_file("new_mnemonic.txt", wallet["mnemonic"])
    save_to_file("new_address.txt", wallet["address"])
    log_message(f"Generated wallet: {wallet['address']}")
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
            log_message(f"Wallet {account.address} is valid and has balance: {balance} ETH.")
            target_wallet = wallets[transaction_count % len(wallets)]
            amount_to_send = random.uniform(0.001, 0.002)

            # Send random amount
            tx_hash = send_transaction(web3, private_key, target_wallet["address"], amount_to_send)
            log_message(f"Transaction sent: {tx_hash}")
            random_pause()

            # Send back maximum from generated wallet
            target_web3 = Web3(Web3.HTTPProvider(NETWORKS[selected_network]))
            target_balance = get_balance(target_web3, target_wallet["address"])
            max_send = target_balance - 0.0005  # Reserve for gas fees

            if max_send > 0:
                return_tx_hash = send_transaction(target_web3, target_wallet["private_key"], account.address, max_send)
                log_message(f"Returned funds: {return_tx_hash}")
                random_pause()

            transaction_count += 1

        else:
            log_message(f"Wallet {account.address} has insufficient balance or is invalid.")
            random_pause()

        if transaction_count >= num_transactions:
            break
