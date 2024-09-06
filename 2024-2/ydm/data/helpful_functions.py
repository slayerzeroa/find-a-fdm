import json
import pandas as pd
from datetime import datetime, timedelta


def json2df(json_data):
    df = pd.DataFrame(json_data)
    return df


def get_minutes_list(reversed=False):
    '''
    9:00 ~ 15:30 사이의 시간 리스트를 반환합니다. (30분 간격)
    '''

    # 시작 시간과 종료 시간 설정
    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("15:30", "%H:%M")

    # 시간 간격 설정 (30분)
    time_interval = timedelta(minutes=30)

    # 시간 리스트 생성
    minutes_list = []
    current_time = start_time
    while current_time <= end_time:
        minutes_list.append(current_time.strftime("%H%M%S"))
        current_time += time_interval

    if reversed:
        minutes_list.reverse()

    return minutes_list