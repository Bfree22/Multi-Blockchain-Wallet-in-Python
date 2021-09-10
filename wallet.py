# Import dependencies
import subprocess
import json
from dotenv import load_dotenv

# Load and set environment variables
load_dotenv('c.env')
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import *
from bit.network import NetworkAPI
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit import *
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
 
 
# w3 connection
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1.8545"))
 
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = './derive -g --mnemonic="{mnemonic}" --coin="btc-test" --cols=path,address,privkey,pubkey --format=json'
    if coin == "eth":
        command = './derive -g --mnemonic="{mnemonic}" --coin="eth" --cols=path,address,privkey,pubkey --format=json'
    if coin == "btc":
        command = './derive -g --mnemonic="{mnemonic}" --coin="btc" --cols=path,address,privkey,pubkey --format=json'
        
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"ETH", "BTCTEST", "BTC"}
numderive = 3

keys = {}
for coin in coins:
keys[coin] = derive_wallets(os.getenv('mnemonic'), coin, numderive=3)

eth_Privatekey = keys["eth"][0]['privkey']
btc_Privatekey = keys["btc-test"][1]['privkey']

print(json.dumps(eth_Privatekey, indent=4, sort_keys=True))
print(json.dumps(btc_Privatekey, indent=4, sort_keys=True))

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
        
eth_account = priv_key_to_account(ETH,eth_Privatekey)
btc_account = priv_key_to_account(BTCTEST,btc_Privatekey)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin,account, recipient, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from":eth_account.address, "to":recipient, "value": amount}
        )
        return {
            "from": eth_account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(eth_account.address)
        }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, "btc")])
        
        
# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipient, amount):
    if coin == ETH:
        txn = create_tx(coin, account, recipient, amount)
        signed_tx = eth_account.signTransaction(txn)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()
    
    elif coin == BTCTEST:
        btc_tx = create_tx(coin, account, recipient, amount)
        signed_tx = account.sign_transaction(txn)
        print(signed_tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
