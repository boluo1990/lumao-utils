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

    def __get_proxy_ips(self, country="", qty=10, is_idc=True):
        url = f'http://list.rola.info:8088/user_get_ip_list?token={self.token}&qty={qty}&country={country}&state=&city=&time=5&format=json&protocol=http&filter=1'
        if is_idc:
            url = f"{url}&&type=datacenter"

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
        ok, proxy_data = self.__get_proxy_ips(country=country, qty=qty)
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