import db
import data
import api

import pandas as pd
from datetime import datetime


start = '20241104'


while start <= '20241127':
    try:
        option_data = db.load_index_options(start)
        print(option_data)
        print('====================')
        net_gex, pc_gex = data.cal_gamma_exposure(option_data)
        print(net_gex, pc_gex)
        print('====================')

        df = pd.DataFrame()
        df['DATE'] = [start]
        df['NET_GEX'] = [net_gex]
        df['PC_GEX'] = [pc_gex]

        db.update_gamma_exposure(df)
        start = str(int(start) + 1)
    except:
        start = str(int(start) + 1)
        continue