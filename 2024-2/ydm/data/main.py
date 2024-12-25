from json import load
import api
import db

import pandas as pd

import time
import datetime
import schedule

import data

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


print("main.py is executed.")
schedule.every().day.at("20:00").do(main)
while True:
    schedule.run_pending()
    time.sleep(1)



# # main()
# if __name__ == '__main__':
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

