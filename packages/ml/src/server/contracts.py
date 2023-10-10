# import json
# import os
# from dotenv import load_dotenv
# # from eth_account import Account
# # from eth_typing import HexStr
# #
# # from web3 import AsyncWeb3
# # from web3.exceptions import ContractCustomError
#
# from utils.util import atimeit
#
# load_dotenv()
#
# ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS", "")
# assert ADMIN_ADDRESS, "ADMIN_ADDRESS environment variable is missing from .env, look at .env.example"
# ADMIN_PK = os.getenv("ADMIN_PK", "")
# assert ADMIN_PK, "ADMIN_PK environment variable is missing from .env, look at .env.example"
#
# RPC_URL = os.getenv("RPC_URL", "")
# assert RPC_URL, "RPC_URL environment variable is missing from .env, look at .env.example"
#
# ADDRESSES = None
#
# try:
#     abiToken = \
#         json.load(
#             open(os.path.join(os.path.dirname(__file__), "../../../hardhat/artifacts-foundry/QABot.sol/QABot.json")))[
#             "abi"]
#     abiStake = json.load(
#         open(os.path.join(os.path.dirname(__file__), "../../../hardhat/artifacts-foundry/QAStake.sol/QAStake.json")))[
#         "abi"]
#     ADDRESSES = json.load(open(os.path.join(os.path.dirname(__file__), "../../../hardhat/addresses.json")))
# except:
#     raise Exception("Please run `forge compile` and `yarn hardhat deploy:anvil` in hardhat folder first")
#
# # if ADDRESSES is not None:
# #     print(f"ADDRESSES:{ADDRESSES}")
# #
# #     TOKEN_CONTRACT_ADDRESS = ADDRESSES["QABotProxy"]
# #     STAKE_CONTRACT_ADDRESS = ADDRESSES["QAStakeProxy"]
# #
# #     print(f"TOKEN_CONTRACT_ADDRESS:{TOKEN_CONTRACT_ADDRESS}")
# #     print(f"STAKE_CONTRACT_ADDRESS:{STAKE_CONTRACT_ADDRESS}")
# #
# #     print(f"ADMIN_ADDRESS:{ADMIN_ADDRESS}")
# #
# #     account = Account.from_key(ADMIN_PK)
# #     wallet_address = account.address
# #     web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
# #
# #     token_contract = web3.eth.contract(address=web3.to_checksum_address(TOKEN_CONTRACT_ADDRESS), abi=abiToken)
# #     stake_contract = web3.eth.contract(address=web3.to_checksum_address(STAKE_CONTRACT_ADDRESS), abi=abiStake)
#
#
# # async def call_contract_stake():
# #     try:
# #         address = web3.to_checksum_address(ADMIN_ADDRESS)
# #
# #         balance = await token_contract.functions.balanceOf(address).call()
# #         print(f"balance:{balance}")
# #
# #         await staked_balance_for(address)
# #
# #         isAdmin = await token_contract.functions.hasRole(web3.to_bytes(hexstr=HexStr("0x" + ("0" * 64))),
# #                                                          address).call()
# #         print(f"isAdmin:{isAdmin}")
# #     except (Exception, ContractCustomError) as e:
# #         print(type(e))
# #         print(e.__dict__)
# #         if 'message' in e.__dict__:
# #             sig = web3.keccak(text='QAStake__AmountGreaterThanBalance()').hex()[0:10]
# #             if e.__dict__['message'] == sig:
# #                 print('Insufficient funds')
# #
# # @atimeit
# # async def charge_stake(address, amount_in_ethers) -> bool:
# #     is_success=False
# #     try:
# #         address = web3.to_checksum_address(address)
# #
# #         nonce = await web3.eth.get_transaction_count(wallet_address)
# #
# #         signed_txn = await stake_contract.functions.charge(address, web3.to_wei(amount_in_ethers, 'ether')).build_transaction({
# #             'gas': 1_000_000,
# #             'gasPrice': web3.to_wei('50', 'gwei'),
# #             'nonce': nonce,
# #             'from': wallet_address,
# #         })
# #
# #         signed_txn = account.sign_transaction(signed_txn)
# #
# #         await staked_balance_for(address)
# #         charge_tx = await web3.eth.send_raw_transaction(signed_txn.rawTransaction)
# #
# #         # print('tx hash', charge_tx.hex())
# #         receipt = await web3.eth.wait_for_transaction_receipt(charge_tx)
# #         if receipt.status == 0:
# #             tx = await web3.eth.get_transaction(charge_tx)
# #             await web3.eth.call({
# #                 'to': tx['to'],
# #                 'from': tx['from'],
# #                 'value': tx['value'],
# #                 'data': tx['input'],
# #             }, tx.blockNumber - 1)
# #         else:
# #             # print('receipt', receipt)
# #             is_success = True
# #     except (Exception, ContractCustomError) as e:
# #         print(type(e))
# #         print(e.__dict__)
# #         if 'message' in e.__dict__:
# #             sig = web3.keccak(text='QAStake__AmountGreaterThanBalance()').hex()[0:10]
# #             if e.__dict__['message'] == sig:
# #                 print('Insufficient funds')
# #
# #     return is_success
# #
# #
# # async def staked_balance_for(address):
# #     address = web3.to_checksum_address(address)
# #     staked_balance = await stake_contract.functions.balances(address).call()
# #     print(f"staked_balance:{staked_balance}")
# #     return staked_balance
