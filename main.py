import os
from web3 import Web3
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet as ETH
from dotenv import load_dotenv
import csv

# Load environment variables
load_dotenv()

# Load blockchain settings from .env
RPC_URL = os.getenv('RPC_URL')

# Wallet generation details
SEED_PHRASE = os.getenv('SEED_PHRASE')
NUMBER_OF_WALLETS = int(os.getenv('NUMBER_OF_WALLETS'))

# Load token details from .env (Format: NAME,CONTRACT,DECIMALS;...)
TOKEN_CONFIGS = os.getenv('TOKENS').split(';')

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

def generate_wallets(mnemonic, count):
    hd_wallet = BIP44HDWallet(cryptocurrency=ETH)
    hd_wallet.from_mnemonic(mnemonic=mnemonic)
    wallets = []
    for i in range(count):
        wallet = hd_wallet.derive_path(f"m/44'/60'/0'/0/{i}")
        wallets.append({
            "address": wallet.address(),
            "private_key": wallet.private_key()
        })
    return wallets

def to_eth(amount, decimals):
    return Web3.fromWei(amount, 'ether') if decimals == 18 else amount / (10 ** decimals)

def get_token_balance(contract, address, decimals):
    try:
        balance = contract.functions.balanceOf(address).call()
        return to_eth(balance, decimals)
    except Exception as e:
        print(f"Error fetching balance for {address}: {e}")
        return None

def write_csv_file(wallets, token_names):
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
        token_contracts.append({
            "name": name,
            "contract": web3.eth.contract(address=contract_address, abi=ERC20_ABI),
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
