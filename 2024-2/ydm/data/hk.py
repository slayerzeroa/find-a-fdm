#### 한국투자증권 KIS DEVELOPER

#### 라이브러리 Import
import os
import json

import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from helpful_functions import json2df

#### 환경변수 세팅
load_dotenv(dotenv_path='C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/.env')
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")


#### 최초 실시간 (웹소켓) 접속키 발급

def get_websocket_token():
    headers = {"content-type":"application/json"}

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "secretkey": APP_SECRET
    }

    url = "https://openapivts.koreainvestment.com:29443/oauth2/Approval"

    response = requests.post(url, headers=headers, data=json.dumps(body))
    response_data = response.json()

    approval_key = response_data['approval_key']
    return approval_key


#### 접근토큰 발급

def get_access_token():
    headers = {"content-type":"application/json"}

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"

    response = requests.post(url, headers=headers, data=json.dumps(body))
    response_data = response.json()

    access_token = response_data['access_token']
    return access_token

try:
    TOKEN = get_access_token()
    txt_path = 'C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/token.txt'
    with open(txt_path, 'w') as f:
        f.write(TOKEN)
except:
    txt_path = 'C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/token.txt'
    with open(txt_path, 'r') as f:
        TOKEN = f.read()


#### 당일 1분봉 데이터 요청
headers = {
    "content-type": "application/json; charset=utf-8",
    "authorization": f"Bearer {TOKEN}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "FHKST03010200",
    "custtype": "P"
}

params = {
    "fid_cond_mrkt_div_code": "J",
    "fid_etc_cls_code": "",
    "fid_input_hour_1": "090000",
    "fid_input_iscd": "000660",
    "fid_pw_data_incu_yn": "Y"
}

url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"

res = requests.get(url, params=params, headers=headers)
rescode = res.status_code
if rescode == 200:
    print(res.headers)
    print(str(rescode) + " | " + res.text)
else:
    print("Error Code : " + str(rescode) + " | " + res.text)

# print(res.json()['output'])
print(res.json())

pd.set_option('display.max_columns', None)
print(json2df(res.json()['output2']))




# #### 일별 주가 데이터
# headers = {
#     "content-type": "application/json; charset=utf-8",
#     "authorization": f"Bearer {TOKEN}",
#     "appkey": APP_KEY,
#     "appsecret": APP_SECRET,
#     "tr_id": "FHKST01010400",
#     "custtype": "P"
# }

# params =  {
#     "fid_cond_mrkt_div_code": "J",
#     "fid_input_iscd": "000660",
#     "fid_org_adj_prc": "0000000001",
#     "fid_period_div_code": "D"
# }

# url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-daily-price"

# res = requests.get(url, params=params, headers=headers)
# rescode = res.status_code
# if rescode == 200:
#     # print(res.headers)
#     # print(str(rescode) + " | " + res.text)
#     print('Success')
# else:
#     print("Error Code : " + str(rescode) + " | " + res.text)


# # print(res.json()['output'])
# print(res.json())

# pd.set_option('display.max_columns', None)
# print(json2df(res.json()['output']))