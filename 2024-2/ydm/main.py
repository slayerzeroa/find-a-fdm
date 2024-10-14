from data.hankook_security_api import *
from data.db import *
from data.helpful_functions import *

import time
import datetime
import schedule

def main():
    try:
        start = time.time()
        print("main start at ", datetime.datetime.now())
        kospi_df = get_every_stock_data()
        update_minutes_df(kospi_df)

        kosdaq_df = get_every_stock_data(market='KOSDAQ')
        update_minutes_df(kosdaq_df)
        print(time.time()-start)
        print("main end at ", datetime.datetime.now())
    except:
        print("error")

# main()
schedule.every().day.at("16:00").do(main)

if __name__ == '__main__':
    while True:
        schedule.run_pending()