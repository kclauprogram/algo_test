import numpy as np
import pandas as pd
import os

def str_to_float(string):
    try:
        num = float(string)
    except ValueError:
        num = string[1:]
    return float(num)

def summary(output=False):
    path = "D:/data/sp500_ibapi/"
    df = {}
    for filename in os.listdir(path):
        if filename.split('.')[0] == 'summary':
            continue
        
        if filename.split('.')[1] == 'csv':
            ticket = filename.split('.')[0]
             
            file_path = os.path.join(path, filename)
            tmp = pd.read_csv(file_path)
            x = tmp.columns[1]
            
            df[ticket] = tmp[x]
            df = pd.DataFrame(df)
            df[ticket] = df[ticket].apply(func=str_to_float)
    
    if output:
        df.to_csv(path + 'summary.csv', index=False)
    
    return df