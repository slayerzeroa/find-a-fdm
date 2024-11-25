import pandas as pd
import numpy as np

from scipy.stats import norm
import math

from datetime import datetime




def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    """
    Black-Scholes 모델을 사용하여 옵션 가격을 계산.
    S: 기초자산 가격
    K: 행사가격
    T: 옵션 만기까지의 시간 (연 단위)
    r: 무위험 이자율
    sigma: 변동성 (연 단위)
    option_type: 옵션 종류 ("call" 또는 "put")
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == "call":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")

def get_historical_volatility(data: pd.DataFrame, window=20):
    """
    주어진 주가 데이터로부터 과거 변동성을 계산.
    data: 주가 데이터프레임 (Date, Close 컬럼을 가져야 함)
    window: 이동 평균 창 크기
    """
    data["log_return"] = np.log(data["CLSPRC_IDX"] / data["CLSPRC_IDX"].shift(1))
    data["volatility"] = data["log_return"].rolling(window).std() * np.sqrt(252)
    data = data.dropna()
    return data[["BAS_DD", "volatility"]]

def get_delta(S, K, T, r, sigma, option_type="call"):
    """
    Delta 계산.
    S: 기초자산 가격
    K: 행사가격
    T: 옵션 만기까지의 시간 (연 단위)
    r: 무위험 이자율
    sigma: 변동성 (연 단위)
    option_type: 옵션 종류 ("call" 또는 "put")
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    if (option_type == "call") or (option_type == "CALL"):
        return norm.cdf(d1)
    elif (option_type == "put") or (option_type == "PUT"):
        return norm.cdf(d1) - 1
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    

def get_gamma(S, K, T, r, sigma):
    """
    Gamma 계산.
    S: 기초자산 가격
    K: 행사가격
    T: 옵션 만기까지의 시간 (연 단위)
    r: 무위험 이자율
    sigma: 변동성 (연 단위)
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    gamma = 1/(sigma * S  * math.sqrt(2*math.pi*T)) * np.exp(-d1**2/2)
    return gamma


