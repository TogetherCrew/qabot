import json
from math import e
import os
from dotenv import load_dotenv
from eth_typing import HexStr

from web3 import AsyncWeb3

load_dotenv()

ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS", "")
assert ADMIN_ADDRESS, "ADMIN_ADDRESS environment variable is missing from .env, look at .env.example"
# ADMIN_PK = os.getenv("ADMIN_PK", "")
# assert ADMIN_PK, "ADMIN_PK environment variable is missing from .env, look at .env.example"
TOKEN_CONTRACT_ADDRESS = os.getenv("TOKEN_CONTRACT_ADDRESS", "")
assert TOKEN_CONTRACT_ADDRESS, "TOKEN_CONTRACT_ADDRESS environment variable is missing from .env, look at .env.example"
STAKE_CONTRACT_ADDRESS = os.getenv("STAKE_CONTRACT_ADDRESS", "")
assert STAKE_CONTRACT_ADDRESS, "STAKE_CONTRACT_ADDRESS environment variable is missing from .env, look at .env.example"

RPC_URL = os.getenv("RPC_URL", "")
assert RPC_URL, "RPC_URL environment variable is missing from .env, look at .env.example"

abiToken = json.load(open(os.path.join(os.path.dirname(__file__), "../../../hardhat/artifacts-foundry/QABot.sol/QABot.json")))["abi"]
abiStake = json.load(open(os.path.join(os.path.dirname(__file__), "../../../hardhat/artifacts-foundry/QAStake.sol/QAStake.json")))["abi"]



async def call_contract_stake():
    web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
    address = web3.to_checksum_address(ADMIN_ADDRESS)
    
    token_contract = web3.eth.contract(address=web3.to_checksum_address(TOKEN_CONTRACT_ADDRESS), abi=abiToken)
    stake_contract = web3.eth.contract(address=web3.to_checksum_address(STAKE_CONTRACT_ADDRESS), abi=abiStake)

    balance = await token_contract.functions.balanceOf(address).call()
    print(balance)

    staked_balance = await stake_contract.functions.balances(address).call()
    print(staked_balance)
    
    isAdmin = await token_contract.functions.hasRole(web3.to_bytes(hexstr=HexStr("0x"+("0"*64))),address).call()
    print(isAdmin)

    try:
        charge_tx = await stake_contract.functions.charge(address,web3.to_wei(125, 'ether')).transact()
        print('tx hash',charge_tx.hex())
        receipt = await web3.eth.wait_for_transaction_receipt(charge_tx)
        print(receipt)
    except Exception as e:
        print(e.__dict__)
        # print type of e var
        print(type(e))
        if 'message' in e.__dict__:
            if (e.__dict__['message'] == '0xe4ab3929'):
                print('Insufficient funds')


    staked_balance = await stake_contract.functions.balances(address).call()
    print(staked_balance)
    

    # tx_hash = await contract.functions.balanceOf(address).transact()
    # receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)
    # print(receipt)