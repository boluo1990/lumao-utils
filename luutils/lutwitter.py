#!/usr/bin/env python3
# encoding=utf-8
import re
import requests

from twitter.api import Twitter
from twitter.oauth import OAuth
from twitter.cmdline import *

CONSUMER_KEY = 'uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET = 'MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

def guest_token() -> str:
    """Generate a guest token to authorize twitter api requests"""
    headers = {
        "authorization": (
            "Bearer "
            "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
            "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        )
    }
    response = requests.post(
        "https://api.twitter.com/1.1/guest/activate.json", headers=headers
    ).json()
    token = response["guest_token"]
    if not token:
        raise RuntimeError("No guest token found after five retry")
    return token


def user_id(user_url: str) -> str:
    """Get the id of a twitter using the url linking to their account"""
    screen_name = re.findall(r"(?<=twitter.com/)\w*", user_url)[0]
    params = {"screen_names": screen_name}
    response = requests.get(
        "https://cdn.syndication.twimg.com/widgets/followbutton/info.json",
        params=params,
    )
    user_data = response.json()
    usr_id = user_data[0]["id"]
    return usr_id


def fetch_pin_autoken(url, cookies):
    url = url

    payload = {}
    headers = {
        'authority': 'api.twitter.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': cookies,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        #### oath2 附加
        # 'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs % 3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        # 'x-csrf-token': '016ba8b68b17b4b4ad89680eba2ea40aa58f0442d41db32ee4a1807b6277291867c21b65c42ed3b1be3eaeedc2c3dff0b249b3696b08f2bfd03207bae85c36ea84b628b36eaf50d2d45778f3c13cf81d',
        # 'x-twitter-active-user': 'yes',
        # 'x-twitter-auth-type': 'OAuth2Session',
        # 'x-twitter-client-language': 'en',
        # 'x-twitter-polling': 'true',
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    aa = response.text

    authenticity_tokenimport = re.findall(r'<input name="authenticity_token" type="hidden" value="(.+)">', aa)
    if authenticity_tokenimport:
        print(f"获取到: {authenticity_tokenimport}")
        return authenticity_tokenimport[0]


def fetch_pin(authenticity_token, pin_url, pin_token, cookies):
    url = "https://api.twitter.com/oauth/authorize"

    payload = f"authenticity_token={authenticity_token}&redirect_after_login={pin_url}&oauth_token={pin_token}"
    headers = {
        'authority': 'api.twitter.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookies,
        'origin': 'https://api.twitter.com',
        'referer': pin_url,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        pin_txt = response.text
        pin_code = re.findall(r'<kbd aria-labelledby="code-desc"><code>(.+)</code></kbd>', pin_txt)
        if pin_code:
            print(f"获取到pin_code: {pin_code}")
            return pin_code[0]
        else:
            print(f"没有pin_code")
            return False
    except Exception as e:
        print(f"fetch pin {str(e)}")

def parse_oauth_tokens(result):
    for r in result.split('&'):
        k, v = r.split('=')
        if k == 'oauth_token':
            oauth_token = v
        elif k == 'oauth_token_secret':
            oauth_token_secret = v
    return oauth_token, oauth_token_secret


def authorize(account_cookies):
    oauth_dance("the Command-Line Tool", CONSUMER_KEY, CONSUMER_SECRET, account_cookies)

class Lutwitter(object):
    def __init__(self, token, token_secret, consumer_key, consumer_secret):
        self.token = token
        self.token_secret = token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.t = Twitter(auth=OAuth(self.token, self.token_secret, self.consumer_key, self.consumer_secret))

    '''
    获取oauth_token和oauth_token_secret
    '''
    @staticmethod
    def oauth_dance(consumer_key, consumer_secret, account_cookies):
        twitter = Twitter(
            auth=OAuth('', '', consumer_key, consumer_secret),
            format='', api_version=None)
        oauth_token, oauth_token_secret = parse_oauth_tokens(
            twitter.oauth.request_token(oauth_callback="oob"))
        oauth_url = ('https://api.twitter.com/oauth/authorize?oauth_token=' +
                    oauth_token)
        twitter_auth_token = fetch_pin_autoken(oauth_url, account_cookies)
        oauth_verifier = fetch_pin(twitter_auth_token, oauth_url, oauth_token, account_cookies)

        if not oauth_verifier:
            return False, "", ""

        twitter = Twitter(
            auth=OAuth(
                oauth_token, oauth_token_secret, consumer_key, consumer_secret),
            format='', api_version=None)
        oauth_token, oauth_token_secret = parse_oauth_tokens(
            twitter.oauth.access_token(oauth_verifier=oauth_verifier))

        return True, oauth_token, oauth_token_secret

    def like(self, tw_id):
        # 点赞
        self.t.favorites.create(_id=tw_id)

    def tw_id_info(self, tw_id):
        #获取指定ID的推特信息
        return self.t.statuses.show(_id=tw_id)

    def retweet(self, tw_id):
        # 转推
        return self.t.statuses.retweet(_id=tw_id)

    # 评论转推
    def quote_retweet(self, content, quote_tw_url):
        return self.t.statuses.update(status=f"{content}.{quote_tw_url}")

    #限流
    def rate_limit_status(self):
        return self.t.application.rate_limit_status()
    # 回复
    def comment(self, content, comment_tw_id):
        return self.t.statuses.update(status=content, in_reply_to_status_id=comment_tw_id, auto_populate_reply_metadata=True)

    #关注者
    def followers(self):
        return self.t.followers.list()

    #朋友
    def friends(self):
        return self.t.friends.list()

    # 发推
    def tweet(self, content):
        return self.t.statuses.update(status=content)

    # 关注
    def follow(self, user_screen_name):
        return self.t.friendships.create(screen_name=f"@{user_screen_name}", follow=True)

    # @ 被人提及
    # aaa = t.statuses.mentions_timeline()

    def my_name(self):
        account_settings = self.t.account.settings()
        return account_settings['screen_name']

    def my_settings(self):
        return self.t.account.settings()


    def search(self, query_string, search_length):
        options = {'action': 'search', 'refresh': False, 'refresh_rate': 600, 'format': 'default', 'length': search_length, 'timestamp': False, 'datestamp': False, 'secure': True, 'invert_split': False, 'force-ansi': False}
        results = self.t.search.tweets(
            q=query_string, count=search_length)['statuses']
        f = get_formatter('search', options)
        for result in results:
            resultStr = f(result, options)
            if resultStr.strip():
                printNicely(resultStr)

    def user_lookup(self, ids):
        ids = [str(_id) for _id in ids]

        lookup_ids = []
        def do_lookup():
            ids_str = ",".join(lookup_ids)
            return self.t.users.lookup(user_id=ids_str, include_entities=False, tweet_mode=False)

        for _ids in ids:
            lookup_ids.append(_ids.strip())
            if len(lookup_ids) == 20:
                for u in do_lookup():
                    yield u
                lookup_ids = []

        if len(lookup_ids) > 0:
            for u in do_lookup():
                yield u

    def fetch_followers(self, user):
        all_followers = []
        cursor = -1
        while cursor != 0:
            all_ids = self.t.followers.ids(screen_name=user, cursor=cursor)
            cursor = all_ids['next_cursor']
            all_followers.append(all_ids['ids'])

        all_fans_list = []
        all_fans_info = self.user_lookup(all_followers)
        for _fans in all_fans_info:
            all_fans_list.append(_fans['screen_name'])

        return all_fans_list