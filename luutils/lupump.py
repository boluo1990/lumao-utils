import struct
from typing import Optional, Union
from solders.pubkey import Pubkey  # type: ignore
from solders.instruction import Instruction  # type: ignore
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price  # type: ignore
from spl.token.instructions import get_associated_token_address
from construct import Padding, Struct, Int64ul, Flag
from solana.transaction import AccountMeta, Transaction
from solana.rpc.types import TokenAccountOpts, TxOpts
from spl.token.instructions import (
    create_associated_token_account, 
    get_associated_token_address, 
    close_account, 
    CloseAccountParams
)
from .lusolana import Lusolana

GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOC_TOKEN_ACC_PROG = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
SOL_DECIMAL = 10**9

class Lupump(Lusolana):
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

    # 获取pump代币价格
    def get_token_price(self, mint_str: str) -> float:
        try:
            coin_data = self.get_coin_data(mint_str)
            
            if not coin_data:
                print("Failed to retrieve coin data...")
                return None
            
            virtual_sol_reserves = coin_data['virtual_sol_reserves'] / 10**9
            virtual_token_reserves = coin_data['virtual_token_reserves'] / 10**6

            token_price = virtual_sol_reserves / virtual_token_reserves
            print(f"Token Price: {token_price:.20f} SOL")
            
            return token_price

        except Exception as e:
            print(f"Error calculating token price: {e}")
            return None

    def get_virtual_reserves(self, bonding_curve: Pubkey):
        bonding_curve_struct = Struct(
            Padding(8),
            "virtualTokenReserves" / Int64ul,
            "virtualSolReserves" / Int64ul,
            "realTokenReserves" / Int64ul,
            "realSolReserves" / Int64ul,
            "tokenTotalSupply" / Int64ul,
            "complete" / Flag
        )
        
        try:
            account_info = self.sol_client.get_account_info(bonding_curve)
            data = account_info.value.data
            parsed_data = bonding_curve_struct.parse(data)
            return parsed_data
        except Exception:
            return None

    @staticmethod
    def derive_bonding_curve_accounts(mint_str: str):
        try:
            mint = Pubkey.from_string(mint_str)
            bonding_curve, _ = Pubkey.find_program_address(
                ["bonding-curve".encode(), bytes(mint)],
                PUMP_FUN_PROGRAM
            )
            associated_bonding_curve = get_associated_token_address(bonding_curve, mint)
            return bonding_curve, associated_bonding_curve
        except Exception:
            return None, None

    def get_coin_data(self, mint_str: str):
        bonding_curve, associated_bonding_curve = Lupump.derive_bonding_curve_accounts(mint_str)
        if bonding_curve is None or associated_bonding_curve is None:
            return None

        virtual_reserves = self.get_virtual_reserves(bonding_curve)
        if virtual_reserves is None:
            return None

        try:
            virtual_token_reserves = int(virtual_reserves.virtualTokenReserves)
            virtual_sol_reserves = int(virtual_reserves.virtualSolReserves)
            token_total_supply = int(virtual_reserves.tokenTotalSupply)
            complete = bool(virtual_reserves.complete)
            
            return {
                "mint": mint_str,
                "bonding_curve": str(bonding_curve),
                "associated_bonding_curve": str(associated_bonding_curve),
                "virtual_token_reserves": virtual_token_reserves,
                "virtual_sol_reserves": virtual_sol_reserves,
                "token_total_supply": token_total_supply,
                "complete": complete
            }
        except Exception:
            return None

    def buy(self, mint_str: str, sol_in: float = 0.01, slippage: int = 25) -> bool:
        try:
            print(f"Starting buy transaction for mint: {mint_str}")
            
            coin_data = self.get_coin_data(mint_str)
            print("Coin data retrieved:", coin_data)

            if not coin_data:
                print("Failed to retrieve coin data...")
                return
                
            if not self.keypair:
                print("current keypair not set...")
                return
            owner = self.pub_key
            mint = Pubkey.from_string(mint_str)
            token_account, token_account_instructions = None, None

            try:
                account_data = self.sol_client.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
                token_account = account_data.value[0].pubkey
                token_account_instructions = None
                print("Token account retrieved:", token_account)
            except:
                token_account = get_associated_token_address(owner, mint)
                token_account_instructions = create_associated_token_account(owner, owner, mint)
                print("Token account created:", token_account)

            print("Calculating transaction amounts...")
            virtual_sol_reserves = coin_data['virtual_sol_reserves']
            virtual_token_reserves = coin_data['virtual_token_reserves']
            sol_in_lamports = sol_in * SOL_DECIMAL
            amount = int(sol_in_lamports * virtual_token_reserves / virtual_sol_reserves)
            slippage_adjustment = 1 + (slippage / 100)
            sol_in_with_slippage = sol_in * slippage_adjustment
            max_sol_cost = int(sol_in_with_slippage * SOL_DECIMAL)  
            print(f"Amount: {amount} | Max Sol Cost: {max_sol_cost}")
            
            MINT = Pubkey.from_string(coin_data['mint'])
            BONDING_CURVE = Pubkey.from_string(coin_data['bonding_curve'])
            ASSOCIATED_BONDING_CURVE = Pubkey.from_string(coin_data['associated_bonding_curve'])
            ASSOCIATED_USER = token_account
            USER = owner

            print("Creating swap instructions...")
            keys = [
                AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
                AccountMeta(pubkey=FEE_RECIPIENT, is_signer=False, is_writable=True),
                AccountMeta(pubkey=MINT, is_signer=False, is_writable=False),
                AccountMeta(pubkey=BONDING_CURVE, is_signer=False, is_writable=True),
                AccountMeta(pubkey=ASSOCIATED_BONDING_CURVE, is_signer=False, is_writable=True),
                AccountMeta(pubkey=ASSOCIATED_USER, is_signer=False, is_writable=True),
                AccountMeta(pubkey=USER, is_signer=True, is_writable=True),
                AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False), 
                AccountMeta(pubkey=TOKEN_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
                AccountMeta(pubkey=EVENT_AUTHORITY, is_signer=False, is_writable=False),
                AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False)
            ]

            data = bytearray()
            data.extend(bytes.fromhex("66063d1201daebea"))
            data.extend(struct.pack('<Q', amount))
            data.extend(struct.pack('<Q', max_sol_cost))
            data = bytes(data)
            swap_instruction = Instruction(PUMP_FUN_PROGRAM, data, keys)

            print("Building transaction...")
            recent_blockhash = self.sol_client.get_latest_blockhash().value.blockhash
            txn = Transaction(recent_blockhash=recent_blockhash, fee_payer=owner)
            txn.add(set_compute_unit_price(self.unit_price))
            txn.add(set_compute_unit_limit(self.unit_budget))
            if token_account_instructions:
                txn.add(token_account_instructions)
            txn.add(swap_instruction)
            
            print("Signing and sending transaction...")
            txn.sign(self.keypair)
            txn_sig = self.sol_client.send_transaction(txn, self.keypair, opts=TxOpts(skip_preflight=True)).value
            #txn_sig = client.send_legacy_transaction(txn, payer_keypair, opts=TxOpts(skip_preflight=True)).value
            print("Transaction Signature:", txn_sig)

            print("Confirming transaction...")
            confirmed = self.confirm_txn(txn_sig)
            print("Transaction confirmed:", confirmed)
            
            return confirmed

        except Exception as e:
            print("Error:", e)
            return None

    def sell(self, mint_str: str, percentage: int = 100, slippage: int = 25) -> bool:
        try:
            print(f"Starting sell transaction for mint: {mint_str}")
            
            if not (1 <= percentage <= 100):
                print("Percentage must be between 1 and 100.")
                return False
            
            coin_data = self.get_coin_data(mint_str)
            print("Coin data retrieved:", coin_data)
            if not coin_data:
                print("Failed to retrieve coin data...")
                return
            
            if not self.keypair:
                print("current keypair not set...")
                return
            owner = self.pub_key
            mint = Pubkey.from_string(mint_str)
            token_account = get_associated_token_address(owner, mint)

            print("Calculating token price...")
            token_decimal = 10**6
            virtual_sol_reserves = coin_data['virtual_sol_reserves'] / SOL_DECIMAL
            virtual_token_reserves = coin_data['virtual_token_reserves'] / token_decimal
            token_price = virtual_sol_reserves / virtual_token_reserves
            print(f"Token Price: {token_price:.20f} SOL")

            print("Retrieving token balance...")
            token_balance = self.get_token_balance(mint_str, str(owner))
            print("Token Balance:", token_balance)    
            if token_balance == 0:
                print("Token Balance is zero, nothing to sell")
                return
            
            print("Calculating transaction amounts...")
            token_balance = token_balance * (percentage / 100)
            amount = int(token_balance * token_decimal)     
            sol_out = float(token_balance) * float(token_price)
            slippage_adjustment = 1 - (slippage / 100)
            sol_out_with_slippage = sol_out * slippage_adjustment
            min_sol_output = int(sol_out_with_slippage * SOL_DECIMAL)
            print(f"Amount: {amount} | Minimum Sol Out: {min_sol_output}")
            
            MINT = Pubkey.from_string(coin_data['mint'])
            BONDING_CURVE = Pubkey.from_string(coin_data['bonding_curve'])
            ASSOCIATED_BONDING_CURVE = Pubkey.from_string(coin_data['associated_bonding_curve'])
            ASSOCIATED_USER = token_account
            USER = owner

            print("Creating swap instructions...")
            keys = [
                AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
                AccountMeta(pubkey=FEE_RECIPIENT, is_signer=False, is_writable=True),
                AccountMeta(pubkey=MINT, is_signer=False, is_writable=False),
                AccountMeta(pubkey=BONDING_CURVE, is_signer=False, is_writable=True),
                AccountMeta(pubkey=ASSOCIATED_BONDING_CURVE, is_signer=False, is_writable=True),
                AccountMeta(pubkey=ASSOCIATED_USER, is_signer=False, is_writable=True),
                AccountMeta(pubkey=USER, is_signer=True, is_writable=True),
                AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False), 
                AccountMeta(pubkey=ASSOC_TOKEN_ACC_PROG, is_signer=False, is_writable=False),
                AccountMeta(pubkey=TOKEN_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(pubkey=EVENT_AUTHORITY, is_signer=False, is_writable=False),
                AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False)
            ]

            data = bytearray()
            data.extend(bytes.fromhex("33e685a4017f83ad"))
            data.extend(struct.pack('<Q', amount))
            data.extend(struct.pack('<Q', min_sol_output))
            data = bytes(data)
            swap_instruction = Instruction(PUMP_FUN_PROGRAM, data, keys)

            print("Building transaction...")
            recent_blockhash = self.sol_client.get_latest_blockhash().value.blockhash
            txn = Transaction(recent_blockhash=recent_blockhash, fee_payer=owner)
            txn.add(set_compute_unit_price(self.unit_price))
            txn.add(set_compute_unit_limit(self.unit_budget))
            txn.add(swap_instruction)
            
            if percentage == 100:
                print("Preparing to close token account after swap...")
                close_account_instructions = close_account(CloseAccountParams(TOKEN_PROGRAM, token_account, owner, owner))
                txn.add(close_account_instructions)        

            print("Signing and sending transaction...")
            txn.sign(self.keypair)
            txn_sig = self.sol_client.send_transaction(txn, self.keypair, opts=TxOpts(skip_preflight=True)).value
            # txn_sig = self.sol_client.send_legacy_transaction(txn, self.keypair, opts=TxOpts(skip_preflight=True)).value
            print("Transaction Signature:", txn_sig)

            print("Confirming transaction...")
            confirmed = self.confirm_txn(txn_sig)
            print("Transaction confirmed:", confirmed)
            
            return confirmed

        except Exception as e:
            print("Error:", e)
            return None