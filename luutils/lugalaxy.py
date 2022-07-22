import uuid
import re
import json
import requests
from termcolor import colored
from datetime import datetime

def gee_callback():
    now = datetime.now()
    timestamp = int(datetime.timestamp(now) * 1000)
    return f"geetest_{timestamp}"

def get_gee_info(callback):
    uuid_string = str(uuid.uuid4())
    url = f"https://gcaptcha4.geetest.com/load?captcha_id=244bcb8b9846215df5af4c624a750db4&challenge={uuid_string}&client_type=web&lang=zh-cn&callback={callback}"
    payload = json.dumps({})
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
        result = response.text
        p1 = re.compile(r'[(](.*)[)]', re.S)  # 贪婪匹配
        result_i = re.findall(p1, result)
        result_dict = result_i[0]
        gee_data = json.loads(result_dict)['data']
    except Exception as e:
        print(colored(f"获取极验信息失败, 报错: {str(e)}", "red"))
        return False, {}
    else:
        return True, gee_data

def get_gee_captcha(callback):
    status, data = get_gee_info(callback)
    if not status:
        return False, {}

    lot_number = data.get('lot_number', '')
    payload = data.get('payload', '')
    process_token = data.get('process_token', '')
    url = f"https://gcaptcha4.geetest.com/verify?captcha_id=244bcb8b9846215df5af4c624a750db4&client_type=web&lot_number={lot_number}&payload={payload}&process_token={process_token}&payload_protocol=1&pt=1&w=62fa96ac7c66123f89d826efed6d5ea5fab9f9a8c0d6971650997018df188cb62e03ce90dbdf7b1b0f5b8c27c12d4ec3488ab37729b57c89b013d212a4b9933db4940009735be2f5bd8b441c9a904ee064e667cc83f6e1187ea9451bf2ca200358139c4bcbc8f984e6824f66b8fca5c49a9f0e9746cf9832c5ace6083cd04d8cdd77b1794c170035e8db997e8dff68392e27c36fd6afbfa9f7c4e3eda4e2d48f90fb2f66cbf38290c056917a4025aa7c9209b1dc8703b41d29bbd5013a3907642ce4311a1d7e0f79f0193dfb67e8535e2eee7b7fcee253b5299e9f3c5f86ea7ce5dc13410c795504515c370933f61e3677bdf3b188352aacf92d9eed2208fc132f0d7fb6d9d4e4389c5ff8b908cfeaa9de4ccdfc7ba627dcc505c3d5012331b089da5d1e09cbb636a31fac5398d5df3a739c0a3e161def19113a03ccdc9b59782602dda98f237e3bbbe49f1bba56cf3bb728339af764774ea97360d26018b093b4af86e27fd85fc8c44532bc6674e9cd99be2f60309363fb8d9a2e8485e8625113090696039dab1b8f0f5bd828c3d91687c9d92b8e72484b198cf090a2a86bffda065233a0ea6c4dc8fec4cec91d7dd08f7a514d637e0391c25d0a3050c5d60c&callback={callback}"
    payload = json.dumps({})
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        result = response.text
        p1 = re.compile(r'[(](.*)[)]', re.S)
        result_i = re.findall(p1, result)
        result_dict = result_i[0]
        gee_captcha = json.loads(result_dict)['data']
    except Exception as e:
        print(colored(f"获取极验验证码失败, 报错: {str(e)}", "red"))
        return False, {}
    else:
        return True, gee_captcha

def query_galaxy(payload, timeout=30, authorization='null'):
    url = "https://graphigo.prd.galaxy.eco/query"
    headers = {
        'Host': 'graphigo.prd.galaxy.eco',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'authorization': authorization,
        'content-type': 'application/json',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'origin': 'https://galaxy.eco',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://galaxy.eco/',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=timeout)
        resp_json = response.json()
        data = resp_json.get('data', {})
    except Exception as e:
        return False, str(e)
    else:
        return True, data

class Lugalaxy(object):
    @staticmethod
    def basic_user_info(addr, timeout=30, authorization='null'):
        payload = json.dumps({
            "operationName": "BasicUserInfo",
            "variables": {
                "address": addr,
                "listSpaceInput": {
                    "first": 30
                }
            },
            "query": "query BasicUserInfo($address: String!, $listSpaceInput: ListSpaceInput!) {\n  addressInfo(address: $address) {\n    id\n    username\n    address\n    hasEmail\n    avatar\n    solanaAddress\n    hasTwitter\n    hasGithub\n    hasDiscord\n    email\n    twitterUserID\n    twitterUserName\n    githubUserID\n    githubUserName\n    isVerifiedTwitterOauth2\n    discordUserID\n    discordUserName\n    isWhitelisted\n    spaces(input: $listSpaceInput) {\n      list {\n        ...SpaceBasicFrag\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SpaceBasicFrag on Space {\n  id\n  name\n  info\n  thumbnail\n  alias\n  links\n  isVerified\n  __typename\n}\n"
        })
        status, data = query_galaxy(payload, timeout=timeout, authorization=authorization)
        if not status:
            print(colored(f"获取活动信息失败, 报错: {data}", "red"))
            return False, {}
        else:
            address_info = data.get('addressInfo', {})
            print(colored("获取用户信息成功", "green"))
            return True, address_info

    @staticmethod
    def claimable_campaigns(addr, timeout=30, authorization='null'):
        status, address_info = Lugalaxy.basic_user_info(addr, timeout, authorization)
        if status:
            user_id = address_info.get("id", "")
            payload = json.dumps({
                "operationName": "Campaigns",
                "variables": {
                    "input": {
                        "listType": "Trending",
                        "statuses": None,
                        "chains": None,
                        "types": None,
                        "isVerified": None,
                        "first": 15,
                        "after": "",
                        "searchString": None,
                        "claimableByUser": user_id
                    },
                    "address": addr
                },
                "query": "query Campaigns($input: ListCampaignInput!, $address: String!) {\n  campaigns(input: $input) {\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    list {\n      ...CampaignSnap\n      isBookmarked(address: $address)\n      id\n      numberID\n      name\n      info\n      useCred\n      formula\n      thumbnail\n      gasType\n      createdAt\n      requirementInfo\n      description\n      enableWhitelist\n      chain\n      startTime\n      requireEmail\n      requireUsername\n      endTime\n      dao {\n        id\n        name\n        logo\n        alias\n        isVerified\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CampaignSnap on Campaign {\n  id\n  name\n  ...CampaignMedia\n  dao {\n    ...DaoSnap\n    __typename\n  }\n  __typename\n}\n\nfragment DaoSnap on DAO {\n  id\n  name\n  logo\n  alias\n  isVerified\n  __typename\n}\n\nfragment CampaignMedia on Campaign {\n  thumbnail\n  gamification {\n    id\n    type\n    __typename\n  }\n  __typename\n}\n"
            })
            _status, data = query_galaxy(payload, timeout=timeout, authorization=authorization)
            if not _status:
                print(colored(f"获取可领取信息失败, 报错: {data}", "red"))
                return False, {}
            else:
                campaigns_info = data.get('campaigns', {})
                print(colored("获取可领取信息成功", "green"))
                return True, campaigns_info

    @staticmethod
    def campaign_info(addr, ampaign_id, timeout=30, authorization='null'):
        payload = json.dumps({
            "operationName": "CampaignInfo",
            "variables": {
                "address": addr,
                "id": ampaign_id
            },
            "query": "query CampaignInfo($id: ID!, $address: String!) {\n  campaign(id: $id) {\n    ...CampaignDetailFrag\n    childrenCampaigns {\n      ...CampaignDetailFrag\n      parentCampaign {\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CampaignDetailFrag on Campaign {\n  id\n  ...CampaignMedia\n  name\n  numberID\n  cap\n  info\n  useCred\n  formula\n  status\n  creator\n  numNFTMinted\n  thumbnail\n  gasType\n  createdAt\n  requirementInfo\n  description\n  enableWhitelist\n  chain\n  startTime\n  endTime\n  requireEmail\n  requireUsername\n  blacklistCountryCodes\n  spaceStation {\n    id\n    address\n    chain\n    __typename\n  }\n  ...WhitelistInfoFrag\n  ...WhitelistSubgraphFrag\n  gamification {\n    ...GamificationDetailFrag\n    __typename\n  }\n  creds {\n    ...CredForAddress\n    __typename\n  }\n  dao {\n    ...DaoSnap\n    nftCores {\n      list {\n        capable\n        marketLink\n        contractAddress\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment DaoSnap on DAO {\n  id\n  name\n  logo\n  alias\n  isVerified\n  __typename\n}\n\nfragment CampaignMedia on Campaign {\n  thumbnail\n  gamification {\n    id\n    type\n    __typename\n  }\n  __typename\n}\n\nfragment CredForAddress on Cred {\n  id\n  name\n  type\n  credType\n  credSource\n  referenceLink\n  chain\n  eligible(address: $address)\n  subgraph {\n    endpoint\n    query\n    expression\n    __typename\n  }\n  __typename\n}\n\nfragment WhitelistInfoFrag on Campaign {\n  id\n  whitelistInfo(address: $address) {\n    address\n    maxCount\n    usedCount\n    __typename\n  }\n  __typename\n}\n\nfragment WhitelistSubgraphFrag on Campaign {\n  id\n  whitelistSubgraph {\n    query\n    endpoint\n    expression\n    variable\n    __typename\n  }\n  __typename\n}\n\nfragment GamificationDetailFrag on Gamification {\n  id\n  type\n  nfts {\n    nft {\n      id\n      animationURL\n      category\n      powah\n      image\n      name\n      treasureBack\n      nftCore {\n        ...NftCoreInfoFrag\n        __typename\n      }\n      traits {\n        name\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  airdrop {\n    name\n    contractAddress\n    token {\n      address\n      icon\n      symbol\n      __typename\n    }\n    merkleTreeUrl\n    addressInfo(address: $address) {\n      index\n      amount {\n        amount\n        ether\n        __typename\n      }\n      proofs\n      __typename\n    }\n    __typename\n  }\n  forgeConfig {\n    minNFTCount\n    maxNFTCount\n    requiredNFTs {\n      nft {\n        category\n        powah\n        image\n        name\n        nftCore {\n          capable\n          contractAddress\n          __typename\n        }\n        __typename\n      }\n      count\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NftCoreInfoFrag on NFTCore {\n  id\n  capable\n  chain\n  contractAddress\n  name\n  symbol\n  dao {\n    id\n    name\n    logo\n    alias\n    __typename\n  }\n  __typename\n}\n"
        })
        status, data = query_galaxy(payload, timeout=timeout, authorization=authorization)
        if not status:
            print(colored(f"获取活动信息失败, 报错: {data}", "red"))
            return False, {}
        else:
            campaign_info = data.get('campaign', {})
            print(colored("获取活动信息成功", "green"))
            return True, campaign_info 

    @staticmethod
    def recent_participation(addr, first=49, only_vasless=False, only_verified=False, timeout=30, authorization='null'):
        payload = json.dumps({
            "operationName": "RecentParticipation",
            "variables": {
                "address": addr,
                "participationInput": {
                    "first": first,
                    "onlyGasless": only_vasless,
                    "onlyVerified": only_verified
                }
            },
            "query": "query RecentParticipation($address: String!, $participationInput: ListParticipationInput!) {\n  addressInfo(address: $address) {\n    id\n    recentParticipation(input: $participationInput) {\n      list {\n        id\n        chain\n        tx\n        campaign {\n          id\n          name\n          dao {\n            id\n            alias\n            __typename\n          }\n          __typename\n        }\n        status\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
        })
        status, data = query_galaxy(payload, timeout=timeout, authorization=authorization)
        if not status:
            print(colored(f"获取近期活动列表失败, 报错: {data}", "red"))
            return False, {}
        else:
            campaign_list = data.get('addressInfo', {}).get('recentParticipation', {}).get('list', [])
            print(colored("获取近期活动列表成功", "green"))
            return True, campaign_list

    # chain = BSC / MATIC
    @staticmethod
    def prepare_participate(addr, campaign_id, chain, mint_count=1, timeout=30, authorization='null'):
        callback = gee_callback()
        status, data = get_gee_captcha(callback)
        if not status:
            return False, {}

        lotNumber = data.get('lot_number', '')
        if 'seccode' not in data:
            return False, {}

        seccode = data['seccode']

        captchaOutput = seccode.get('captcha_output', '')
        passToken = seccode.get('pass_token', '')
        gen_time = seccode.get('gen_time', '')

        payload = json.dumps({
            "operationName": "PrepareParticipate",
            "variables": {
                "input": {
                    "signature": "",
                    "campaignID": campaign_id,
                    "address": addr,
                    "mintCount": mint_count,
                    "chain": chain,
                    "captcha": {
                        "lotNumber": lotNumber,
                        "captchaOutput": captchaOutput,
                        "passToken": passToken,
                        "genTime": gen_time,
                    }
                }
            },
            "query": "mutation PrepareParticipate($input: PrepareParticipateInput!) {\n  prepareParticipate(input: $input) {\n    allow\n    disallowReason\n    signature\n    mintFuncInfo {\n      funcName\n      nftCoreAddress\n      verifyIDs\n      powahs\n      cap\n      __typename\n    }\n    extLinkResp {\n      success\n      data\n      error\n      __typename\n    }\n    metaTxResp {\n      metaSig2\n      autoTaskUrl\n      metaSpaceAddr\n      forwarderAddr\n      metaTxHash\n      reqQueueing\n      __typename\n    }\n    solanaTxResp {\n      mint\n      updateAuthority\n      explorerUrl\n      signedTx\n      verifyID\n      __typename\n    }\n    __typename\n  }\n}\n"
        })

        status, data = query_galaxy(payload, timeout=timeout, authorization=authorization)
        if not status:
            print(colored(f"领取NFT/获取签名信息失败, 报错: {data}", "red"))
            return False, {}
        else:
            info = data.get('prepareParticipate', {})
            print(colored("领取NFT/获取签名信息成功", "green"))
            return True, info