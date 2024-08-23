#### 한국투자증권 KIS DEVELOPER

#### 라이브러리 Import
import os
import json

import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

#### 환경변수 세팅
load_dotenv()
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



#### 당일 1분봉 데이터 요청
headers = {
    "content-type": "application/json; charset=utf-8",
    "authorization": get_websocket_token(),
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "FHKST03010200",
    "custtype": "P"
}

body =  {
    "fid_cond_mrkt_div_code": "J",
    "fid_etc_cls_code": "",
    "fid_input_hour_1": "100000",
    "fid_input_iscd": "000660",
    "fid_pw_data_incu_yn": "Y"
 }

url = "https://openapivts.koreainvestment.com:29443/oauth2/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"

response = requests.get(url, headers=headers, data=json.dumps(body))
print(response.text)
# response_data = response.json()
# print(response_data)