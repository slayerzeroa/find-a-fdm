from json import load
from data.api import *
from data.db import *
from data.helpful_functions import *

import time
import datetime
import schedule


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
    start = time.time()
    print("main start")
    kospi_call, kospi_put = get_index_option_dataframe()
    print("update index options...")

    update_index_options(kospi_call)
    update_index_options(kospi_put)
    
    print(time.time()-start)
    print("done!")

schedule.every().day.at("20:00").do(main)

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

