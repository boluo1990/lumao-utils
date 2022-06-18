#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''
@Time    :   2022/06/02 10:31:57
@Author  :   Boluo
@Version :   1.0
@Contact :   poorityw5@gmail.com
@License :   (C)Copyright 2021-2022
@Desc    :   None
'''

chain_info = {
    # 主网
    "ethereum": {
        "http_provider": "https://mainnet.infura.io/v3/",
        "chain_id": 1,
        "desc": "以太坊主网",
        "expoler": "https://etherscan.io"
    },
    "bsc": {
        "http_provider": "https://bsc-dataseed.binance.org/",
        "chain_id": 56,
        "desc": "币安智能链",
        "expoler": "https://bscscan.com"
    },
    "polygon": {
        "http_provider": "https://polygon-rpc.com",
        "chain_id": 137,
        "desc": "Polygon主网",
        "expoler": "https://polygonscan.com"
    },
    "moonriver": {
        "http_provider": "https://rpc.api.moonriver.moonbeam.network",
        "chain_id": 1285,
        "desc": "Moonriver主网",
        "expoler": "https://moonriver.moonscan.io"
    },
    "moonbeam": {
        "http_provider": "https://rpc.api.moonbeam.network",
        "chain_id": 1284,
        "desc": "Moonbeam主网",
        "expoler": "https://moonbeam.moonscan.io"
    },
    "fantom": {
        "http_provider": "https://rpc.ftm.tools",
        "chain_id": 250,
        "desc": "Fantom主网",
        "expoler": "https://ftmscan.com"
    },
    "evmos": {
        "http_provider": "https://eth.bd.evmos.org:8545",
        "chain_id": 9001,
        "desc": "Evmos主网",
        "expoler": "https://evm.evmos.org"
    },
    "avalanche-c-chain": {
        "http_provider": "https://api.avax.network/ext/bc/C/rpc",
        "chain_id": 43114,
        "desc": "雪崩C链",
        "expoler": "https://snowtrace.io"
    },
    "arbitrum": {
        "http_provider": "https://arb1.arbitrum.io/rpc",
        "chain_id": 42161,
        "desc": "Arbitrum主网",
        "expoler": "https://arbiscan.io"
    },
    "optimism": {
        "http_provider": "https://mainnet.optimism.io",
        "chain_id": 10,
        "desc": "Optimism主网",
        "expoler": "https://optimistic.etherscan.io"
    },
    "cube": {
        "http_provider": "https://http.cube.network",
        "chain_id": 1818,
        "desc": "Cube主网",
        "expoler": "https://cubescan.network"
    },
    # 测试网
    "ropsten": {
        "http_provider": "https://ropsten.infura.io/v3/",
        "chain_id": 3,
        "desc": "以太坊Ropsten测试网",
        "expoler": "https://ropsten.etherscan.io"
    },
    "rinkeby": {
        "http_provider": "https://rinkeby.infura.io/v3/",
        "chain_id": 4,
        "desc": "以太坊Rinkeby测试网",
        "expoler": "https://rinkeby.etherscan.io"
    },
    "goerli": {
        "http_provider": "https://goerli.infura.io/v3/",
        "chain_id": 5,
        "desc": "以太坊Goerli测试网",
        "expoler": "https://goerli.etherscan.io"
    },
    "bsc-test": {
        "http_provider": "https://data-seed-prebsc-1-s1.binance.org:8545",
        "chain_id": 97,
        "desc": "币安智能链测试网",
        "expoler": "https://testnet.bscscan.com"
    },
    "cube-test": {
        "http_provider": "https://http-testnet.cube.network",
        "chain_id": 1819,
        "desc": "Cube链测试网",
        "expoler": "https://testnet.cubescan.network"
    },
}