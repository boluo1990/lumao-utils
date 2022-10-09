import requests
import threading
from termcolor import colored

class MyThread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.res = self.func(*self.args)

    def get_result(self):
        return self.res

def get_real_ip(proxies):
    url = 'https://ifconfig.me/ip'
    try:
        response = requests.request('GET', url, proxies=proxies, timeout=5)
        proxy_ip = response.text
    except Exception as e:
        print(colored(f"请求真实IP失败, 报错: {str(e)}", "red"))
        return ""
    else:
        return proxy_ip

class Luproxy(object):
    def __init__(self, token) -> None:
        self.token = token

    def get_proxy_ips(self, country="", qty=10, is_idc=True):
        """获取代理IP, 不做验证和真实IP校验

        Args:
            country (str, optional): 获取代理的国家代号(例如 jp / sg / hk). Defaults to "".
            qty (int, optional): 一次获取代理的数量. Defaults to 10.
            is_idc (bool, optional): 是否idc地址. Defaults to True.

        Returns:
            _type_: 是否正常返回(bool), 返回的IP列表(list)
        """
        url = f'http://list.rola.info:8088/user_get_ip_list?token={self.token}&qty={qty}&country={country}&state=&city=&time=5&format=json&protocol=http&filter=1'
        if is_idc:
            url = f"{url}&type=datacenter"

        try:
            response = requests.request('GET', url, timeout=5)
            resp_json = response.json()
            resp_code = resp_json["code"]
            resp_data = resp_json["data"]
        except Exception as e:
            return False, e
        else:
            if resp_code != 0:
                return False, resp_json
            else:
                return True, resp_data

    def add_whitelist(self, local_ip, remark=""):
        """添加IP白名单

        Args:
            local_ip (_type_): 需要添加的IP地址
            remark (str, optional): 备注. Defaults to "".
        """
        url = f"http://api.rola-ip.co/user_add_whitelist?token={self.token}&remark={remark}&ip={local_ip}"
        try:
            response = requests.request('GET', url, timeout=5)
            resp_json = response.json()
            resp_msg = resp_json["msg"]
        except Exception as e:
            print(colored(f"添加白名单失败, 报错: {str(e)}", "red"))
        else:
            if resp_json["code"] != 0:
                print(colored(f"添加白名单失败, 报错: {resp_msg}", "red"))
            else:
                print(colored(f"添加白名单成功, 消息: {resp_msg}", "green"))

    def fetch_ok_proxy(self, country="", qty=10):
        """获取可用代理IP列表

        Args:
            country (str, optional): 获取代理的国家代号(例如 jp / sg / hk). Defaults to "".
            qty (int, optional): 一次获取代理的数量. Defaults to 10.

        Returns:
            _type_: 是否正常返回(bool), 返回的IP列表(list), 返回IP对应真实出口IP列表(list)
        """
        ok, proxy_data = self.get_proxy_ips(country=country, qty=qty)
        if not ok:
            return False, [], []

        threads = []
        results = []
        for i in range(0, len(proxy_data)):
            proxies = {
                'http': f'http://{proxy_data[i]}',
                'https': f'http://{proxy_data[i]}'
            }
            t = MyThread(get_real_ip, (proxies,))
            threads.append(t)

        for i in range(0, len(proxy_data)):
            threads[i].start()

        for i in range(0, len(proxy_data)):
            threads[i].join()
            results.append(threads[i].get_result())

        return True, proxy_data, results