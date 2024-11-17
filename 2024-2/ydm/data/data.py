import pandas as pd
import numpy as np

from scipy.stats import norm
import math

from datetime import datetime


## 옵션 만기가 세번째 금요일이니
## 해당 월의 세번째 금요일을 찾아주는 함수
def get_third_friday(year: int, month: int):
    # The 15th is the lowest third Friday can be
    third_friday = 15 + (4 - datetime(year, month, 15).weekday()) % 7
    return datetime(year, month, third_friday)

## 만기일까지 남은 일수를 계산해주는 함수
def get_remaining_days(year: int, month: int):
    third_friday = get_third_friday(year, month)
    today = datetime.today()
    remaining_days = (third_friday - today).days
    return remaining_days


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

def get_implied_volatility(S, K, T, r, market_price, option_type="call", tol=1e-5, max_iter=100):
    """
    암시적 변동성 (Implied Volatility)을 계산.
    S: 기초자산 가격
    K: 행사가격
    T: 옵션 만기까지의 시간 (연 단위)
    r: 무위험 이자율
    market_price: 옵션의 시장 가격
    option_type: 옵션 종류 ("call" 또는 "put")
    tol: 허용 오차
    max_iter: 최대 반복 횟수
    """
    sigma = 0.2  # 초기 추정값
    for i in range(max_iter):
        # 현재 변동성으로 계산한 이론적 가격
        price = black_scholes_price(S, K, T, r, sigma, option_type)
        # Vega 계산 (Black-Scholes 모델의 민감도)
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        vega = S * norm.pdf(d1) * math.sqrt(T)
        
        # Newton-Raphson 업데이트
        price_diff = price - market_price
        if abs(price_diff) < tol:  # 수렴 여부 확인
            return sigma
        sigma -= price_diff / vega
    
    # 반복 후 수렴 실패 시
    raise ValueError("Implied volatility did not converge.")


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
    if option_type == "call":
        return norm.cdf(d1)
    elif option_type == "put":
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
