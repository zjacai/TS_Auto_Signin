#encoding:utf-8
import json
import requests
import bs4
import re
import os

requests.packages.urllib3.disable_warnings()

import time

t = time.localtime()
time_start = time.strftime("%Y-%m-%d %H:%M:%S", t)
#print(f"开始时间：{time_start}",t)
print(f"开始时间：{time_start}")
#sys.exit(0)


username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]
question_num = os.environ["QUESTION_NUM"]
question_answer = os.environ["QUESTION_ANSWER"]
pushplus_token = os.environ["PUSHPLUS_TOKEN"]

proxies = {
    'https': "http://127.0.0.1:8080",
    'http': "http://127.0.0.1:8080"
}

#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
             "Accept":"*/*",
             "Accept-Encoding":"gzip,deflate",
             "Connection":"close",
             "Content-Type":"application/x-www-form-urlencoded"
             }


def pushplus(text, msg):
    url = 'http://www.pushplus.plus/send'
    data = {
        "token":pushplus_token,
        "title":text,
        "content":msg,
        "template": "markdown"
        }
    body=json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type':'application/json'}
    requests.post(url,data=body,headers=headers)



def t00ls_login(u_name, u_pass, q_num, q_ans):
    login_data = {
        'username': u_name,
        'password': u_pass,
        'questionid': q_num,    # 安全提问 参考下面
        'answer': q_ans,
        'cookietime': 2592000,
        'loginsubmit':'登录',
        'redirect':'https://www.t00ls.com'
    }
    '''
    questionid
    # 0 = 没有安全提问
    # 1 = 母亲的名字
    # 2 = 爷爷的名字
    # 3 = 父亲出生的城市
    # 4 = 您其中一位老师的名字
    # 5 = 您个人计算机的型号
    # 6 = 您最喜欢的餐馆名称
    # 7 = 驾驶执照的最后四位数字
    '''
    response_login = requests.get('https://www.t00ls.com/login.html', verify=False, headers=headers)
    #soup = bs4.BeautifulSoup(response_login.text, 'lxml')
    soup = bs4.BeautifulSoup(response_login.text, 'html.parser')

    if response_login.status_code != 302:
        #formhash = soup.find_all("input")[5].attrs["value"]
        formhash=soup.find('input', attrs={"name":"formhash"})["value"]
        formhash1 = {"formhash": formhash}
        login_data.update(formhash1)
        response_login1 = requests.post(url='https://www.t00ls.com/login.html', data=login_data, headers=headers,
                                        verify=False,)
        if response_login1.history[0].status_code == 302:
            cookie_value = requests.utils.dict_from_cookiejar(response_login1.history[0].cookies)

            return formhash, cookie_value
        else:
            return None

def t00ls_sign(t00ls_hash, t00ls_cookies):
    sign_data = {
        'formhash': t00ls_hash,
        'signsubmit': "apply"
    }

    response_sign = requests.post('https://www.t00ls.com/ajax-sign.json', cookies=t00ls_cookies, data=sign_data,
                                  verify=False, headers=headers)
    soup = bs4.BeautifulSoup(response_sign.text, 'lxml')
    s=soup.find_all(href=re.compile("formhash"))
    pattern=re.compile('[0-9a-zA-Z]{8}')
    formhash = {"formhash": pattern.findall(str(s[0]))[1]}
    sign_data.update(formhash)
    response_sign = requests.post('https://www.t00ls.com/ajax-sign.json', cookies=t00ls_cookies, data=sign_data, verify=False, headers=headers)
    return json.loads(response_sign.text)


def main():
    response_login = t00ls_login(username, password, question_num, question_answer)
    if response_login:
        print('登录成功')
        response_sign = t00ls_sign(response_login[0], response_login[1])
        if response_sign['status'] == 'success':
            print('签到成功')
            pushplus(text='签到程序提醒!',msg=f"签到成功 {response_sign}")
        elif response_sign['message'] == 'alreadysign':
            print('今日已签到')
            pushplus(text='签到程序提醒!',msg=f"今日已签到 {response_sign}")
        else:
            print('出现玄学问题了 签到失败')
            pushplus(text='签到失败!',msg=response_sign)
    else:
        print('登入失败 请检查输入资料是否正确')
        pushplus(text='登入失败!',msg="登入失败 请检查输入资料是否正确")


if __name__ == '__main__':
    main()
