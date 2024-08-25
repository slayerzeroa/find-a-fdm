import json
import pandas as pd

def json2df(json_data):
    df = pd.DataFrame(json_data)
    return df