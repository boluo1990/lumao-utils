import time
from termcolor import colored
from web3 import Web3, HTTPProvider
from eth_abi import encode_abi
from eth_account.messages import encode_defunct
from . import config

class Luweb3(Web3):
    def __init__(self, http_provider=None, chain_id=None, chain_name=None) -> None:
        if http_provider is not None and chain_id is not None:
            self.chain_id = chain_id
            chain_name = f"链 {chain_id}"
        else:
            http_provider = config.chain_info[chain_name]["http_provider"]
            self.chain_id = config.chain_info[chain_name]["chain_id"]
        self.w3 = Web3(HTTPProvider(http_provider))
        while self.w3.isConnected() is not True:
            self.w3 = Web3(HTTPProvider(http_provider))
            print(colored(f"{chain_name} RPC连接失败, 重试...", "yellow"))
            time.sleep(1)
        print(colored(f"{chain_name} RPC已连接", "green"))

    @staticmethod
    def encode_abi_to_hex(types, args):
        return Web3.toHex(encode_abi(types, args))[2:]

    @staticmethod
    def encode_function(func_text):
        return Web3.keccak(text=func_text)[0:4].hex()

    def get_gas_price(self):
        return self.w3.eth.gas_price

    def get_nonce(self, address, estimate_nonce=0):
        return max(self.w3.eth.get_transaction_count(address), estimate_nonce)

    def sign_msg(self, private_key, msg_text):
        message = encode_defunct(text=msg_text)
        signed_message = self.w3.eth.account.sign_message(message, private_key=private_key)
        signature = signed_message["signature"].hex()
        return signature

    # 获取原生代币数量
    def get_eth_balance(self, address):
        return self.w3.eth.get_balance(address)

    # 构造 input_data 发送交易
    def send_raw_transaction(
        self, address, private_key, to_address, nonce, gas_option={}, input_data="0x",
        value=0, gas_limit=6000000, is_async=False, timeout=300, poll_latency=0.5):
        tx_data = {
            'from': address,
            'to': to_address,
            'value': value,
            'data': input_data,
            'gas': gas_limit,
            'chainId': self.chain_id
        }
        if not bool(gas_option):
            gas_option = self.w3.eth.gasPrice
        else:
            for k in gas_option:
                tx_data[k] = gas_option[k]
        tx_data['nonce'] = self.get_nonce(address, estimate_nonce=nonce)
        sign_txn = self.w3.eth.account.sign_transaction(tx_data, private_key=private_key)
        txn_hash = self.w3.eth.send_raw_transaction(sign_txn.rawTransaction)
        if is_async:
            print(colored(f'交易已提交, hash: {txn_hash.hex()}', "blue"))
            return 0, tx_data["nonce"], {}
        else:
            print(colored(f'交易确认中, hash: {txn_hash.hex()}', "blue"))
            txn_detail = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout, poll_latency=poll_latency)
            print(colored(f'交易已确认, hash: {txn_hash.hex()}, 状态: {txn_detail["status"]}', "green"))
            return txn_detail["status"], tx_data["nonce"], txn_detail["logs"]
        
    def send_erc20_token(self, address, private_key, receiver, token_address, amount, gas_option={}, nonce=0):
        input_data = f"0xa9059cbb%064x%064x" % (int(receiver, 16), amount)
        return self.send_raw_transaction(address, private_key, token_address, nonce, gas_option=gas_option, input_data=input_data)

    # 没有abi情况下读取合约数据
    def read_raw_contract_function(self, contract_addr, func_text, args_types=None, args=None):
        func_bytes = self.encode_function(func_text)
        if args_types is None or args is None:
            args_bytes = ''
        else:
            args_bytes = self.encode_abi_to_hex(args_types, args)
        data = f"{func_bytes}{args_bytes}"
        tx_data = {
            "to": contract_addr,
            "data": data
        }
        return self.w3.eth.call(tx_data).hex()

    def get_erc20_balance(self, address, token_address):
        func_text = 'balanceOf(address)'
        args_types = ['address']
        args = [address]
        return self.read_raw_contract_function(token_address, func_text, args_types, args)

    # def write_contract(self):
    #     pass