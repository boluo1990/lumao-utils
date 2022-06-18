import time
from termcolor import colored
from web3 import Web3, HTTPProvider

class Lweb3:
    def __init__(self, http_provider, chain_id) -> None:
        self.provider = http_provider
        self.chain_id = chain_id
        self.w3 = {}
        self.contract = {}

        self._connect()

    # 创建Web3实例
    def _connect(self):
        self.w3 = Web3(HTTPProvider(self.provider))
        while self.w3.isConnected() is not True:
            self.w3 = Web3(HTTPProvider(self.provider))
            print(colored(f"连接web3失败, 重试...", "yellow"))
            time.sleep(1)
        print(colored(f"已连接web3", "green"))


    # 构造 input_data 发送交易
    # gas_option = {
    #   'maxFeePerGas': Web3.toWei(15, "gwei"),
    #   'maxPriorityFeePerGas': Web3.toWei(3, "gwei"),
    # }
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
        if not gas_option:
            gas_option = self.w3.eth.gasPrice

        for k in gas_option:
            tx_data[k] = gas_option[k]
        tx_data['nonce'] = max(self.w3.eth.getTransactionCount(address), nonce)
        sign_txn = self.w3.eth.account.sign_transaction(tx_data, private_key=private_key)
        txn_hash = self.w3.eth.sendRawTransaction(sign_txn.rawTransaction)
        if is_async:
            print(colored(f'交易已提交, hash: {txn_hash.hex()}', "blue"))
            return 0, tx_data["nonce"], {}
        else:
            print(colored(f'交易确认中, hash: {txn_hash.hex()}', "blue"))
            txn_detail = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout, poll_latency=poll_latency)
            print(colored(f'交易已确认, hash: {txn_hash.hex()}, 状态: {txn_detail["status"]}', "green"))
            return txn_detail["status"], tx_data["nonce"], txn_detail["logs"]