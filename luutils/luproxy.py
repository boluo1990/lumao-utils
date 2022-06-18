import requests
import threading

class MyThread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.res = self.func(*self.args)

    def get_result(self):
        return self.res

def get_proxy_ips(token, country="", qty=10):
    url = f'http://list.rola.info:8088/user_get_ip_list?token={token}&qty={qty}&country={country}&state=&city=&time=5&format=json&protocol=http&filter=1'
    try:
        response = requests.request('GET', url, timeout=5)
        resp_json = response.json()
    except Exception as e:
        return False, e
    else:
        if resp_json["code"] != 0:
            return False, resp_json
        else:
            return True, resp_json["data"]

def get_real_ip(proxies):
    url = 'https://ifconfig.me/ip'
    try:
        response = requests.request('GET', url, proxies=proxies, timeout=5)
        proxy_ip = response.text
    except Exception as e:
        print(str(e))
        return ""
    else:
        return proxy_ip

def add_whitelist(token, local_ip, remark=""):
    url = f"http://api.rola-ip.co/user_add_whitelist?token={token}&remark={remark}&ip={local_ip}"
    try:
        response = requests.request('GET', url, timeout=5)
        resp_json = response.json()
    except Exception as e:
        print(f"添加白名单失败, 报错: {str(e)}")
    else:
        if resp_json["code"] != 0:
            print(f"添加白名单失败, 报错: {resp_json['msg']}")
        else:
            print(f"添加白名单成功, 消息: {resp_json['msg']}")

def fetch_ok_proxy(token, country="", qty=10):
    ok, proxy_data = get_proxy_ips(token, country=country, qty=qty)
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