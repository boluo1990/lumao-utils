import json
import time
import requests
from typing import Optional, Union
from solana.rpc.api import Client
from solders.keypair import Keypair #type: ignore
from solana.transaction import Signature

class Lusolana():
    def __init__(self, http_rpc, ws_rpc=None) -> None:
        self.http_rpc = http_rpc
        self.ws_rpc = ws_rpc
        self.sol_client = Client(http_rpc)
        self.unit_price = 1_000_000
        self.unit_budget = 100_000

    # 设置当前交易的钱包
    def set_key_pair(self, priv_key: str) -> None:
        self.priv_key = priv_key
        self.keypair = Keypair.from_json(self.priv_key)
        self.pub_key = self.keypair.pubkey()
        print(f"设置钱包: {str(self.pub_key)}")

    # 设置优先费用 = unit_price / 10**6 * unit_budget / 10**9 
    def set_gas(self, unit_price: int, unit_budget: int) -> None:
        self.unit_price = unit_price
        self.unit_budget = unit_budget
        print(f"设置优先费: {self.unit_budget * self.unit_price / 10**15} SOL")

    @staticmethod
    def find_data(data: Union[dict, list], field: str) -> Optional[str]:
        if isinstance(data, dict):
            if field in data:
                return data[field]
            else:
                for value in data.values():
                    result = Lusolana.find_data(value, field)
                    if result is not None:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = Lusolana.find_data(item, field)
                if result is not None:
                    return result
        return None

    # 获取代币余额
    def get_token_balance(self, mint_str: str, pubkey_str: str):
        try:
            headers = {"accept": "application/json", "content-type": "application/json"}

            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "getTokenAccountsByOwner",
                "params": [
                    pubkey_str,
                    {"mint": mint_str},
                    {"encoding": "jsonParsed"},
                ],
            }
            
            response = requests.post(self.http_rpc, json=payload, headers=headers)
            ui_amount = Lusolana.find_data(response.json(), "uiAmount")
            return float(ui_amount)
        except Exception as e:
            print(f"get token balance error: {str(e)}")
            return None

    # 确认交易
    def confirm_txn(self, txn_sig: Signature, max_retries: int = 20, retry_interval: int = 3) -> bool:
        retries = 1
        
        while retries < max_retries:
            try:
                txn_res = self.sol_client.get_transaction(txn_sig, encoding="json", commitment="confirmed", max_supported_transaction_version=0)
                txn_json = json.loads(txn_res.value.transaction.meta.to_json())
                
                if txn_json['err'] is None:
                    print("Transaction confirmed... try count:", retries)
                    return True
                
                print("Error: Transaction not confirmed. Retrying...")
                if txn_json['err']:
                    print("Transaction failed.")
                    return False
            except Exception as e:
                print("Awaiting confirmation... try count:", retries)
                retries += 1
                time.sleep(retry_interval)
        
        print("Max retries reached. Transaction confirmation failed.")
        return None