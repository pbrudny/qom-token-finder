
# Ethereum Wallet Balance Checker

This project generates Ethereum wallets from a seed phrase, checks their ERC-20 token balances, and exports the results to a CSV file. It is designed to be flexible, allowing multiple tokens to be specified dynamically.

## Features
- Generate Ethereum wallets from a BIP-44 compatible seed phrase
- Check balances for multiple ERC-20 tokens specified in the `.env` file
- Export wallets with non-zero balances to `filtered_wallets.csv`

## Requirements
- Python 3.8 or higher
- Qom RPC URL and ERC-20 contract details

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# On Windows
# .\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file in the root directory and add the following:

```ini
# Blockchain RPC URL
RPC_URL=https://rpc.qom.one

# Seed phrase and wallet count
SEED_PHRASE="your seed phrase here"
NUMBER_OF_WALLETS=100

# Token details (Format: NAME,CONTRACT_ADDRESS,DECIMALS)
TOKENS=HAWK,0xbc85f14059d60458b614052b4a84734e463878cc,18;
```

### 5. Run the Script
```bash
python main.py
```


## Output
The script generates a `filtered_wallets.csv` containing wallets with non-zero balances in the specified tokens.

## License
This project is open source under the MIT License.
