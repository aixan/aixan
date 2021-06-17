import sys
import json
import importlib
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
importlib.reload(sys)

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def getToken(Corpid, Secret):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    Data = {
        "corpid": Corpid,
        "corpsecret": Secret
    }
    r = requests.get(url=Url, params=Data, verify=False)
    if r.json()['errcode'] != 0:
        return False
    else:
        Token = r.json()['access_token']
        file = open('static/json/zabbix_wechat_config.json', 'w')
        file.write(r.text)
        file.close()
        return Token


def weiXin(User, Content):
    # Tagid = "1"  # 通讯录标签ID
    # Partyid = "1" # 部门ID
    Agentid = "1000002"  # 应用ID
    Corpid = "ww6c12b8255dd6d4b4"  # CorpID是企业号的标识
    Secret = "HhQCwzs_vv7eO_FhB4hba6JVnHNKwHJTUFChVBmcgbA"  # Secret是管理组凭证密钥
    try:
        file = open('static/json/zabbix_wechat_config.json', 'r')
        Token = json.load(file)['access_token']
        file.close()
    except:
        Token = getToken(Corpid, Secret)

    n = 0
    Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
    Data = {
        "touser": User,  # 企业号中的用户帐号，在zabbix用户Media中配置，如果配置不正常，将按部门发送。
        # "totag": 1,              # 企业号中的标签id，群发使用（推荐）
        # "toparty": 1,            # 企业号中的部门id，群发时使用。
        "msgtype": "markdown",  # 消息类型。
        "agentid": Agentid,  # 企业号中的应用id。
        "markdown": {
            "content": Content
        },
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    r = requests.post(url=Url, data=json.dumps(Data), verify=False)
    while r.json()['errcode'] != 0 and n < 4:
        n += 1
        Token = getToken(Corpid, Secret)
        if Token:
            Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
            r = requests.post(url=Url, data=json.dumps(Data), verify=False)
    return r.json()
