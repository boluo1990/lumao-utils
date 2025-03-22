import time
from termcolor import colored
from web3 import Web3, HTTPProvider, exceptions, WebsocketProvider
from web3.auto import w3 as _w3
from eth_abi import encode as encode_abi
from eth_account.messages import encode_defunct, encode_structured_data
from . import config

class Luweb3(Web3):
    def __init__(self, http_provider=None, ws_provider=None, chain_id=None,
                 chain_name=None, connect_timeout=10, request_kwargs={},
                 websocket_kwargs={}, check_connected=True) -> None:
        if (http_provider or ws_provider) and chain_id is not None:
            self.chain_id = chain_id
            chain_name = f"链 {chain_id}"
        else:
            http_provider = config.chain_info[chain_name]["http_provider"]
            self.chain_id = config.chain_info[chain_name]["chain_id"]

        connect_time = 0
        while True:
            if ws_provider:
                self.w3 = Web3(WebsocketProvider(ws_provider, websocket_kwargs=websocket_kwargs))
            else:
                self.w3 = Web3(HTTPProvider(http_provider, request_kwargs=request_kwargs))

            if not check_connected:
                break

            if self.w3.is_connected() is True:
                break

            print(colored(f"{chain_name} RPC连接失败, 重试...", "yellow"))
            time.sleep(1)
            connect_time += 1
            if connect_time >= connect_timeout:
                print(colored(f"{chain_name} RPC重试 {connect_timeout}s 连接失败", "red"))
                raise Exception("http_provider connect failed")
        print(colored(f"{chain_name} RPC已连接", "green"))

    @staticmethod
    def encode_abi_to_hex(types, args):
        return Web3.to_hex(encode_abi(types, args))[2:]

    @staticmethod
    def encode_function(func_text):
        return Web3.keccak(text=func_text)[0:4].hex()

    @staticmethod
    def encode_input_hex(_type, _value):
        if _type == "uint256":
            return "%064x" % _value
        elif _type == "address":
            return "%064x" % int(_value, 16)
        else:
            return _value

    @staticmethod
    def sign_msg(private_key, msg_text):
        message = encode_defunct(text=msg_text)
        signed_message = _w3.eth.account.sign_message(message, private_key=private_key)
        signature = signed_message["signature"].hex()
        return signature

    @staticmethod
    def sign_eip712_msg(private_key, typed_msg):
        signed_message = _w3.eth.account.sign_message(encode_structured_data(primitive=typed_msg), private_key=private_key)
        signature = signed_message["signature"].hex()
        return signature

    def get_gas_price(self):
        return self.w3.eth.gas_price

    def get_1559_base_fee(self):
        fee_dict = self.w3.eth.fee_history(1, 'latest')
        return fee_dict['baseFeePerGas'][0]

    def get_max_priority_fee(self):
        return self.w3.eth.max_priority_fee

    def get_logs(self, filter_params):
        return self.w3.eth.get_logs(filter_params)

    def get_nonce(self, address, estimate_nonce=0):
        return max(self.w3.eth.get_transaction_count(address), estimate_nonce)

    def get_transaction_receipt(self, tx_hash):
        return self.w3.eth.get_transaction_receipt(tx_hash)

    # 获取原生代币数量
    def get_eth_balance(self, address):
        return self.w3.eth.get_balance(address)

    # 检查交易确认情况
    # status: 0->回退 1->已确认 2->超时 3->其他异常
    def __check_transaction(self, txn_hash, poll_latency, timeout):
        status = 0
        txn_detail = {}
        count = 0
        while True:
            # 超时
            if count * poll_latency >= timeout:
                print(colored(f"{txn_hash.hex()} 交易超时", "red"))
                status = 2
                break

            try:
                txn_detail = self.w3.eth.get_transaction_receipt(txn_hash)
                status = txn_detail['status']
            except exceptions.TransactionNotFound:
                time.sleep(poll_latency)
                count += 1
            except Exception as e:
                print(colored(f"交易状态异常: {str(e)}", "yellow"))
                time.sleep(poll_latency)
                count += 1
                # status = 3
                # txn_detail = { "error": str(e) }
                # break
            else:
                if status == 1:
                    print(colored(f"交易 {txn_hash.hex()} 已成功确认", "green"))
                    break
                elif status == 0:
                    print(colored(f"交易 {txn_hash.hex()} 已失败回退", "red"))
                    break
                else:
                    print(colored(f"交易 {txn_hash.hex()} 状态异常", "red"))

        return status, txn_detail

    # 构造 input_data 发送交易
    def send_raw_transaction(
        self, address, private_key, to_address, nonce, gas_option={}, input_data="0x",
        tx_type=1, value=0, gas_limit=None, is_async=False, timeout=300, poll_latency=0.5):
        if gas_limit is None:
            gas_limit = self.get_estimate_gas(address, to_address, value, input_data)

        tx_data = {
            'from': address,
            'to': to_address,
            'value': value,
            'data': input_data,
            'gas': gas_limit,
            'chainId': self.chain_id
        }
        if not bool(gas_option):
            if tx_type == 1:
                tx_data["gasPrice"] = self.w3.eth.gas_price
            else:
                tx_data["maxFeePerGas"] = self.get_1559_base_fee() + self.get_max_priority_fee()
                tx_data["maxPriorityFeePerGas"] = self.get_max_priority_fee()
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
            # status, txn_detail = self.__check_transaction(txn_hash, poll_latency, timeout)
            try:
                while True:
                    txn_detail = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout, poll_latency=poll_latency)
                    if txn_detail["status"] != None:
                        break
                    time.sleep(5)
            except exceptions.BadResponseFormat:
                time.sleep(poll_latency)
            else:
                print(colored(f'交易已确认, hash: {txn_hash.hex()}, 状态: {txn_detail["status"]}', "green"))
                return txn_detail["status"], tx_data["nonce"], txn_detail

    def send_raw_transaction_with_gas(
        self, address, private_key, to_address, nonce, input_data="0x", value=0, tx_type=1,
        price_mul=1, limit_mul=1, is_async=False, timeout=300, poll_latency=0.5):
        gas_limit = self.get_estimate_gas(address, to_address, value=value, data=input_data)
        if price_mul == 1:
            return self.send_raw_transaction(
                address, private_key, to_address, nonce, input_data=input_data, value=value, tx_type=tx_type,
                gas_limit=int(gas_limit * limit_mul), is_async=is_async, timeout=timeout, poll_latency=poll_latency
                )
        else:
            if tx_type == 1:
                gas_option = {
                    "gasPrice": int(price_mul * self.get_gas_price())
                }
            else:
                base_fee = self.get_1559_base_fee()
                priority_fee = self.get_max_priority_fee()
                gas_option = {
                    "maxFeePerGas": int((base_fee + priority_fee) * price_mul),
                    "maxPriorityFeePerGas": int(priority_fee * price_mul),
                }
            return self.send_raw_transaction(
                address, private_key, to_address, nonce, gas_option=gas_option, input_data=input_data, tx_type=tx_type,
                value=value, gas_limit=int(gas_limit * limit_mul), is_async=is_async, timeout=timeout, poll_latency=poll_latency
            )

    def send_raw_transaction_with_gas_loop(
        self, address, private_key, to_address, nonce, input_data="0x", value=0, tx_type=1,
        price_mul_start=1, price_mul_step=0.1, limit_mul=1, timeout=300, poll_latency=0.5, retries=5):
        retry = 0
        while retry < retries:
            price_mul = price_mul_start + retry * price_mul_step 
            try:
                status, nonce, tx_detail = self.send_raw_transaction_with_gas(
                    address, private_key, to_address, nonce, input_data, value, tx_type, price_mul,
                    limit_mul, timeout=timeout, poll_latency=poll_latency
                    )
            except Exception as e:
                if "is not in the chain after" in str(e) or "transaction underpriced" in str(e) or "ALREADY_EXISTS" in str(e):
                    print(colored(f"{address} 交易未确认/GAS太低: {str(e)}", "yellow"))
                    retry += 1
                    continue
                print(colored(f"{address} 交易报错: {str(e)}", "red"))
                return 0, 0, {}
            else:
                return status, nonce, tx_detail

    # 授权ERC-20代币
    def approve_erc20_token(
        self, address, private_key, spender_addr, token_addr,
        limit=int("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16),
        gas_option={}, tx_type=1, gas_limit=None, nonce=0, is_async=False, check_allowance=False
        ):
        execute = True
        if check_allowance:
            allowance = self.get_erc20_allowance(address, spender_addr, token_addr)
            if allowance >= limit:
                execute = False
                return 1, nonce - 1, {}

        if execute:
            input_data = f"0x095ea7b3{Luweb3.encode_input_hex('address', spender_addr)}{Luweb3.encode_input_hex('uint256', limit)}"
            return self.send_raw_transaction(address, private_key, token_addr, nonce, gas_option=gas_option, gas_limit=gas_limit, input_data=input_data, tx_type=tx_type, is_async=is_async)

    # 发送ERC-20代币    
    def send_erc20_token(
        self, address, private_key, receiver, token_address, amount,
        gas_option={}, tx_type=1, gas_limit=None, nonce=0, is_async=False
        ):
        input_data = f"0xa9059cbb%064x%064x" % (int(receiver, 16), amount)
        return self.send_raw_transaction(address, private_key, token_address, nonce, gas_option=gas_option, gas_limit=gas_limit, input_data=input_data, tx_type=tx_type, is_async=is_async)

    # 获取已授权ERC20代币数量
    def get_erc20_allowance(self, address, spender, token_address):
        func_text = "allowance(address,address)"
        arg_types = ["address", "address"]
        args = [address, spender]
        return int(self.read_raw_contract_function(token_address, func_text, arg_types, args), 16)

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
        return int(self.read_raw_contract_function(token_address, func_text, args_types, args), 16)

    # 获取预期gas_limit
    def get_estimate_gas(self, address, to_address, value=0, data="0x"):
        return self.w3.eth.estimate_gas({
            "from": address,
            "to": to_address,
            "value": value,
            "data": data
        })

    def get_block_number(self):
        return self.w3.eth.get_block_number()

    def get_block(self, block_number="latest"):
        return self.w3.eth.get_block(block_number)

    def construct_contract(self, contract_addr, contract_abi):
        return self.w3.eth.contract(address=contract_addr, abi=contract_abi)

    def deploy_contract(self, contract_abi, bytecode, addr, pk, constructor_args=(), value=0, tx_type=1, gas_option={}):
        ctr = self.w3.eth.contract(abi=contract_abi, bytecode=bytecode)
        tx_data = {
            "from": addr,
            "nonce": self.get_nonce(addr),
            "value": value
        }
        if not bool(gas_option):
            if tx_type == 1:
                tx_data["gasPrice"] = self.w3.eth.gas_price
            else:
                tx_data["maxFeePerGas"] = self.get_1559_base_fee() + self.get_max_priority_fee()
                tx_data["maxPriorityFeePerGas"] = self.get_max_priority_fee()
        else:
            for k in gas_option:
                tx_data[k] = gas_option[k]
        construct_txn = ctr.constructor(*constructor_args).build_transaction(tx_data)
        return self.sign_send_transaction(pk, construct_txn)

    def sign_send_transaction(self, pk, txn_dict, is_async=False, timeout=300, poll_latency=0.5):
        signed_txn = self.w3.eth.account.sign_transaction(txn_dict, pk)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        if is_async:
            print(colored(f'交易已提交, hash: {txn_hash.hex()}', "blue"))
            return 0, txn_dict["nonce"], {}
        else:
            print(colored(f'交易确认中, hash: {txn_hash.hex()}', "blue"))
            # status, txn_detail = self.__check_transaction(txn_hash, poll_latency, timeout)
            try:
                txn_detail = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout, poll_latency=poll_latency)
            except exceptions.BadResponseFormat:
                time.sleep(poll_latency)
            else:
                print(colored(f'交易已确认, hash: {txn_hash.hex()}, 状态: {txn_detail["status"]}', "green"))
                return txn_detail["status"], txn_dict["nonce"], txn_detail

    # # 写方法
    # def write_contract(self, func_name, *args):
    #     nonce = self.w3.eth.get_transaction_count(self.base_addr)
    #     tx_dict = self.contract.functions[func_name](*args).buildTransaction({
    #         'from': self.base_addr,
    #         'chainId': 56,
    #         'gasPrice': self.w3.eth.gasPrice,
    #         'nonce': nonce,
    #     })
    #     signed_txn = self.w3.eth.account.signTransaction(tx_dict, self.base_pk)
    #     txn_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    #     print(colored(f'交易确认中, hash: {txn_hash.hex()}', "blue"))
    #     txn_detail = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=300, poll_latency=0.1)
    #     print(colored(f'交易已确认, hash: {txn_hash.hex()}, 状态: {txn_detail["status"]}', "green"))
    #     return txn_detail["status"], txn_detail["logs"]