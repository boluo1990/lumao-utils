import time
import json
import requests
from termcolor import colored

class Lucaptcha(object):
    def __init__(self, anycaptcha_key, task_type, website_key, website_url) -> None:
       self.anycaptcha_key = anycaptcha_key
       self.task_type = task_type
       self.website_key = website_key
       self.website_url = website_url

    def __anycaptcha_create(self):
        url = "https://api.anycaptcha.com/createTask"

        payload = json.dumps({
            "clientKey": self.anycaptcha_key,
            "task": {
                "type": self.task_type,
                "websiteURL": self.website_url,
                "websiteKey": self.website_key,
                # "isInvisible": False
            }
        })
        headers = { 'Content-Type': 'application/json' }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.json().get('taskId'):
                return True, response.json()['taskId']
            else:
                print(colored(f"创建任务失败, 返回: {response.text()}", "red"))
                return False, ""
        except Exception as e:
            print(colored(f"创建任务失败, 报错: {str(e)}", "red"))
            return False, ""

    @staticmethod
    def list_captcha_types():
        print('''
    - RecaptchaV2TaskProxyless
    - RecaptchaV3TaskProxyless
    - FunCaptchaTaskProxyless
    - HCaptchaTaskProxyless
    - HCaptchaClickTask
    ''')

    def get_captcha_balance(self):
        url = "https://api.anycaptcha.com/getBalance"
        payload = json.dumps({
            "clientKey": self.anycaptcha_key,
        })
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.json().get('balance'):
                return True, response.json()['balance']
            else:
                print(colored(f"获取账户余额失败, 返回: {response.text()}", "red"))
                return False, ""
        except Exception as e:
            print(colored(f"获取账户余额失败, 报错: {response.text()}", "red"))
            return False, ""

    def anycaptcha_solver(self):
        url = "https://api.anycaptcha.com/getTaskResult"

        ok, task_id = self.__anycaptcha_create()
        delay = 0
        if ok:
            print(colored(f"开始创建任务ID: {task_id}", "cyan"))
            while True:
                if delay >= 60:
                    print(colored(f"解析任务超时", "red"))
                    break
                try:
                    payload = json.dumps({
                        "clientKey": self.anycaptcha_key,
                        "taskId": task_id
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload)
                    if response.json().get('solution'):
                        return True, response.json()['solution']['gRecaptchaResponse']
                    elif response.json()['errorId'] == 1:
                        print(colored(f"解析任务失败, 返回: {response.text()}", "red"))
                        return False, ""
                    else:
                        delay += 1
                        time.sleep(5)
                except Exception as e:
                    print(colored(f"解析任务失败, 报错: {response.text()}", "red"))
                    return False, ""
            return False, ""
        else:
            return False, ""