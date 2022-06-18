import time
import json
import requests


def list_captcha_types():
    print('''
- RecaptchaV2TaskProxyless
- RecaptchaV3TaskProxyless
- FunCaptchaTaskProxyless
- HCaptchaTaskProxyless
- HCaptchaClickTask
''')

def get_captcha_balance(anycaptcha_key):
    url = "https://api.anycaptcha.com/getBalance"
    payload = json.dumps({
        "clientKey": anycaptcha_key,
    })
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.json().get('balance'):
            return True, response.json()['balance']
        else:
            print(response.text())
            return False, ""
    except Exception as e:
        print(f"anycaptcha create task error: {str(e)}")
        return False, ""

def anycaptcha_create(task_type, website_key, website_url, anycaptcha_key):
    url = "https://api.anycaptcha.com/createTask"

    payload = json.dumps({
        "clientKey": anycaptcha_key,
        "task": {
            "type": task_type,
            "websiteURL": website_url,
            "websiteKey": website_key,
            # "isInvisible": False
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.json().get('taskId'):
            return True, response.json()['taskId']
        else:
            print(response.text())
            return False, ""
    except Exception as e:
        print(f"anycaptcha create task error: {str(e)}")
        return False, ""

def anycaptcha_solver(task_type, website_key, website_url, anycaptcha_key):
    url = "https://api.anycaptcha.com/getTaskResult"

    ok, task_id = anycaptcha_create(task_type, website_key, website_url, anycaptcha_key)
    delay = 0
    if ok:
        print(f"创建任务ID: {task_id}")
        while True:
            if delay >= 60:
                print(f"anycaptcha solver timeout!")
                break
            try:
                payload = json.dumps({
                    "clientKey": anycaptcha_key,
                    "taskId": task_id
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.json().get('solution'):
                    return True, response.json()['solution']['gRecaptchaResponse']
                elif response.json()['errorId'] == 1:
                    print(f"anycaptcha solver error: {response.json()}")
                    return False, ""
                else:
                    delay += 1
                    time.sleep(5)
            except Exception as e:
                print(f"anycaptcha solver error: {str(e)}")
                return False, ""
    else:
        print(f"anycaptcha solver error: no task id")
        return False, ""