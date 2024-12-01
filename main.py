import os
from web3 import Web3
from dotenv import load_dotenv
import csv
from mnemonic import Mnemonic
from eth_account import Account

# Enable unaudited HD wallet features
Account.enable_unaudited_hdwallet_features()

# Load environment variables
load_dotenv()

# Load blockchain settings from .env
RPC_URL = os.getenv('RPC_URL')
if not RPC_URL:
    raise ValueError("RPC_URL is missing in the .env file")

# Wallet generation details
SEED_PHRASE = os.getenv('SEED_PHRASE')
if not SEED_PHRASE:
    raise ValueError("SEED_PHRASE is missing in the .env file")

NUMBER_OF_WALLETS = int(os.getenv('NUMBER_OF_WALLETS', 100))  # Default to 100 if not provided

# Load token details from .env (Format: NAME,CONTRACT,DECIMALS;...)
TOKEN_CONFIGS = os.getenv('TOKENS').split(';') if os.getenv('TOKENS') else []
if not TOKEN_CONFIGS:
    raise ValueError("TOKENS configuration is missing or improperly set in the .env file")

# ERC-20 ABI for balanceOf function
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# Initialize Web3 provider
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Check if Web3 is connected
if not web3.is_connected():
    raise ValueError("Failed to connect to the Web3 provider")

def generate_wallets(mnemonic, count):
    wallets = []
    for i in range(count):
        acct = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{i}")
        wallets.append({
            "address": acct.address,
            "private_key": acct.key.hex(),
        })
    return wallets

def to_eth(amount, decimals):
    """Convert token amount to ETH based on decimals"""
    return Web3.from_wei(amount, 'ether') if decimals == 18 else amount / (10 ** decimals)

def get_token_balance(contract, address, decimals):
    """Fetch token balance from the contract"""
    try:
        balance = contract.functions.balanceOf(address).call()
        return to_eth(balance, decimals)
    except Exception as e:
        print(f"Error fetching balance for {address}: {e}")
        return None

def write_csv_file(wallets, token_names):
    """Write filtered wallet data to a CSV file"""
    with open('filtered_wallets.csv', mode='w', newline='') as file:
        fieldnames = ["Address", "Private Key"] + [f"{name} Balance" for name in token_names]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(wallets)
    print("CSV file 'filtered_wallets.csv' has been created successfully!")

def main():
    wallets = generate_wallets(SEED_PHRASE, NUMBER_OF_WALLETS)
    filtered_wallets = []
    token_contracts = []

    # Initialize contracts for each token
    for config in TOKEN_CONFIGS:
        name, contract_address, decimals = config.split(',')
        contract_address_checksum = Web3.to_checksum_address(contract_address)  # Ensure address is in checksum format
        token_contracts.append({
            "name": name,
            "contract": web3.eth.contract(address=contract_address_checksum, abi=ERC20_ABI),
            "decimals": int(decimals)
        })

    for i, wallet in enumerate(wallets):
        wallet_info = {"Address": wallet['address'], "Private Key": wallet['private_key']}
        non_zero_balance = False

        for token in token_contracts:
            balance = get_token_balance(token["contract"], wallet['address'], token["decimals"])
            wallet_info[f"{token['name']} Balance"] = balance
            if balance > 0:
                non_zero_balance = True

        if non_zero_balance:
            filtered_wallets.append(wallet_info)
            print(f"Wallet {i + 1}: {wallet_info}")
        else:
            print(f"Wallet {i + 1}: No balance in specified tokens")

    if filtered_wallets:
        write_csv_file(filtered_wallets, [token['name'] for token in token_contracts])
    else:
        print("No wallets with non-zero balances found.")

if __name__ == "__main__":
    main()
