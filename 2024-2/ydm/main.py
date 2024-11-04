from data.api import *
from data.db import *
from data.helpful_functions import *

import time
import datetime
import schedule

kospi_call, kospi_put = get_index_option_dataframe()

print("update index options...")
update_index_options(kospi_call)
update_index_options(kospi_put)
print("done!")


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

