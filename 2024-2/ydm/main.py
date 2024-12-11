from json import load
from data import api
from data import db
from data import data
from data import helpful_functions

import pandas as pd

import time
import datetime
import schedule

import QuantLib as ql


# target_date = '20241110'
# df = load_index_options(target_date)

# kospi_call = df[df['MARKET_CODE']=='C']
# kospi_put = df[df['MARKET_CODE']=='P']

# print(df)

# # net_gex, pc_gex = cal_gamma_exposure(kospi_call, kospi_put)

# # input_df = pd.DataFrame()
# # input_df['DATE'] = [target_date]
# # input_df['NET_GEX'] = [net_gex]
# # input_df['PC_GEX'] = [pc_gex]

# # update_gamma_exposure(input_df)

def main():
    TOKEN = api.get_access_token()

    # 오늘이 working day인지 확인
    business_day_flag = api.check_business_day(TOKEN)
    if business_day_flag == 'Y':
        start = time.time()
        print("main start")
        kospi_call, kospi_put = api.get_index_option_dataframe(TOKEN)
        print("update index options...")

        db.update_index_options(kospi_call)
        db.update_index_options(kospi_put)
        
        print(time.time()-start)
        print("done!")

        print("update gamma exposure...")
        option_data = db.load_index_options(datetime.datetime.now().strftime("%Y%m%d"))
        net_gex, pc_gex = data.cal_gamma_exposure(option_data)

        df = pd.DataFrame()
        df['DATE'] = [datetime.datetime.now().strftime("%Y%m%d")]
        df['NET_GEX'] = [net_gex]
        df['PC_GEX'] = [pc_gex]

        db.update_gamma_exposure(df)
        print("done!")

    else:
        print("Today is not a business day.")

schedule.every().day.at("20:00").do(main)
# main()
if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)



# def main():
#     start = time.time()
#     print("main start")
#     kospi_df = get_every_stock_data()
#     update_minutes_df(kospi_df)

#     kosdaq_df = get_every_stock_data(market='KOSDAQ')
#     update_minutes_df(kosdaq_df)
#     print(time.time()-start)

# main()
# schedule.every().day.at("16:00").do(main)

# if __name__ == '__main__':
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

