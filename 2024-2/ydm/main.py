from data.hankook_security_api import *
from data.db import *
from data.helpful_functions import *

import time
import datetime
import schedule

def main():
    start = time.time()
    kospi_df = get_every_stock_data()
    update_minutes_df(kospi_df)

    kosdaq_df = get_every_stock_data(market='KOSDAQ')
    update_minutes_df(kosdaq_df)
    print(time.time()-start)

schedule.every().day.at("10:00").do(main)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)