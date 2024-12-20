import numpy as np
import pandas as pd
import fastdtw
import os

def data_import(path='D:/project/results/stock_data_summary/summary.csv', train_num=506, test_num=755):
    data = pd.read_csv(path)  
    train_data = data[0:train_num]
    test_data = data[506:test_num]
    
    columns_with_nulls = train_data.columns[train_data.isnull().any()].tolist()
    
    # Drop the identified columns from both train and test data
    train_data = train_data.drop(columns=columns_with_nulls)
    test_data = test_data.drop(columns=columns_with_nulls)
    
    drop_count = len(columns_with_nulls)
    print(f'Dropped {drop_count} columns with null values in training data.')
    
    return train_data, test_data

def scaler_fit(data):
    col_name = data.columns
    scaling = {}
    for ticket in col_name:
        scaling[ticket] = np.mean(data[ticket])
    return scaling

def scaler_transform(data, scaler, inverse=False):
    if inverse:
        for element in data.columns:
            data[element] = data[element]*scaler[element]
        return data.reset_index(drop=True)
    else:
        for element in data.columns:
            data[element] = data[element]/scaler[element]
        return data.reset_index(drop=True)

def data_preprocess(train_data, test_data):
    scaler = scaler_fit(train_data)
    norm_train_data = scaler_transform(train_data, scaler)
    norm_test_data = scaler_transform(test_data, scaler)
    return norm_train_data, norm_test_data, scaler

def combination(list):
    output = []
    for i in range(len(list)-1):
        for j in range(len(list)-i-1):
            output.append([list[i], list[i+j+1]])
    return output

def dwt_find_pair(data=None, criteria=200, reload=False, reload_index=100):

    if reload:
        print("retreive last pair data")
        pair_record = pd.read_csv("D:/project/results/pair/dwt.csv")
        pair_record = pair_record.head(reload_index)                   
        print(f'retreived {pair_record.shape[0]} dtw pair data')      
        return pair_record.values.tolist()

    column_list = data.columns.to_list()
    test_pair = combination(column_list)
    print('total pair to test :'+ str(len(test_pair)))
    dist = []

    for pair in test_pair:
        stock1 = data[pair[0]].dropna()
        stock2 = data[pair[1]].dropna()
        stock1 = np.array(stock1, dtype=np.double)
        stock2 = np.array(stock2, dtype=np.double)
        dwt_dist = fastdtw.fastdtw(stock1, stock2)[0]
        
        if dwt_dist < criteria:
            print('Found new pair ' + str(pair) + ' with distance : ' + str(dwt_dist))
            dist.append([pair[0], pair[1], dwt_dist])
        
    pair_record = pd.DataFrame(dist, columns=['pair1', 'pair2', 'dist'])
    pair_record = pair_record.sort_values('dist', ascending=True)
    pair_record.to_csv('D:/project/results/pair/dwt' + str(criteria) + ".csv", index=False)
    print('total pair found :'+ str(len(dist)))
    
    return dist

def ssd_find_pair(data, criteria, reload=False, reload_index=False):
    
    if reload:
        print("retreive last pair data")
        pair_record = pd.read_csv("D:/project/results/pair/ssd.csv")
        pair_record = pair_record.head(reload_index)                     
        print(f'retreived {pair_record.shape[0]} ssd pair data')      
        return pair_record.values.tolist()

    column_list = data.columns.to_list()
    test_pair = combination(column_list)
    dist = []

    for pair in test_pair:
        stock1 = data[pair[0]].dropna()
        stock2 = data[pair[1]].dropna()
        
        if len(stock1) != len(stock2):
            continue
        
        if len(stock1) % 2 != 0:
            stock2 = stock2[:-1]
            stock1 = stock1[:-1]
            
        stock1 = stock1.values.reshape(-1, 2)
        stock2 = stock2.values.reshape(-1, 2)
        
        stock1 = np.array(np.mean(stock1, axis=1))
        stock2 = np.array(np.mean(stock2, axis=1))
        
        ssd_dist = np.sum((stock1 - stock2)**2)
        if ssd_dist < criteria:
            #print('Found new pair ' + str(pair) + ' with distance : ' + str(ssd_dist))
            dist.append([pair[0], pair[1], ssd_dist])
        
    pair_record = pd.DataFrame(dist, columns=['pair1', 'pair2', 'dist'])
    pair_record = pair_record.sort_values('dist', ascending=True)
    pair_record.to_csv('D:/project/results/pair/ssd' + str(criteria) + ".csv", index=False)
    print('total pair found :'+ str(len(dist)))
    
    return dist

def pair_search(criteria, train_num):
    train_data, test_data = data_import(train_num=train_num)
    norm_train_data, norm_test_data, scaler = data_preprocess(train_data, test_data)
    
    dtw = dwt_find_pair(norm_train_data, criteria=criteria[0], reload=False)
    ssd = ssd_find_pair(norm_train_data, criteria=criteria[1], reload=False)
    
    return 0
    
def pair_divergence(data, pair_list):
    pair_div = {}
    for pair in pair_list:
        stock_1, stock_2 = pair[0], pair[1]
        price_1, price_2 = data[stock_1], data[stock_2]
        diff = np.mean(abs(price_1 - price_2))
        pair_div[str(stock_1 + '&' + stock_2)] = diff
    return pair_div
    
def enter(record, a, b, direction, invest_amount):
    record[7] = True 
    if direction:
        record[0] = b[0]
        record[1] = invest_amount/b[1]
        record[2] = b[1]
        record[3] = a[0]
        record[4] = invest_amount/a[1]
        record[5] = a[1]
        return record
    
    else:
        record[0] = a[0]
        record[1] = invest_amount/a[1]
        record[2] = a[1]
        record[3] = b[0]
        record[4] = invest_amount/b[1]
        record[5] = b[1]
        return record

def trade_execute(norm_test_data, trade_pair, scaler, gap, initial_capital, invest_amount):
    
    name_a, name_b = trade_pair[0], trade_pair[1]
    stock1 = norm_test_data[name_a].dropna()
    stock2 = norm_test_data[name_b].dropna()
    test_data = scaler_transform(norm_test_data, scaler, inverse=True)
    stock1_price = test_data[name_a]
    stock2_price = test_data[name_b]

    trade_period = min(len(stock1), len(stock2))
    in_position = False
    
    trade_record = []
    first_record = [name_a, 0, stock1_price[0], name_b, 0, stock2_price[0], 1, in_position, initial_capital]
    trade_record.append(first_record)
    
    for i in range(1, trade_period):
            
        direction_before = bool(stock1[i-1] >= stock2[i-1])
        direction = bool(stock1[i] >= stock2[i])
        record_before = trade_record[i-1]

        #update position status when no event
        if True:
            record = record_before
            record[2] = test_data[record[0]][i]
            record[5] = test_data[record[3]][i]
            record[6] = i
            record[8] = initial_capital + record[1]*record[2] - record[4]*record[5]

        #not in position, gap large
        if (abs(stock1[i] - stock2[i]) > gap * 2) & (not in_position):
            in_position = True
            a, b = [name_a, stock1_price[i]], [name_b, stock2_price[i]]
            record = enter(record, a, b, direction, invest_amount)

        #in position, price cross
        if in_position & (direction_before != direction):
            in_position = False
            initial_capital = record[8]
            record[1] = 0
            record[4] = 0
            record[7] = in_position

        #in postion, forcibly liquidate when time end
        if i == trade_period - 1:
            record[1] = 0
            record[4] = 0
            record[7] = False
            break
            
        trade_record.append(record.copy())

    print("Trade execution for " + trade_pair[0] + ' & ' + trade_pair[1] + " completed.")

    return trade_record 
############################
def backtest_result(num, method, invest):
    ### preprocess
    train_data, test_data = data_import(test_num=1258)
    norm_train_data, norm_test_data, scaler = data_preprocess(train_data, test_data)

    ### first find pair that are similar
    reload = True
    if method == 'dtw':
        trade_list = dwt_find_pair(norm_train_data, criteria=70, reload=reload, reload_index=num)
    else:
        trade_list = ssd_find_pair(norm_train_data, criteria=70, reload=reload, reload_index=num)
    
    entering_criteria = pair_divergence(norm_train_data, trade_list)

    output_format = ['long', 'unit_long', 'price_long', 'short', 'unit_short', 'price_short', 'time', 'in_positon', 'value']
    # trade_execute and review by pair
    for trade_pair in trade_list:
        
        pair_name = trade_pair[0] + '&' + trade_pair[1]
        trade_record = trade_execute(norm_test_data.copy(), trade_pair, scaler,
                                     gap=entering_criteria[pair_name], invest_amount=invest, initial_capital=10000)
        df_trade = pd.DataFrame(trade_record, columns=output_format)
        if method == 'dtw':
            df_trade.to_csv('D:/project/results/trade_review_dtw/' + pair_name + '.csv', index=False)
        else:
            df_trade.to_csv('D:/project/results/trade_review_ssd/' + pair_name + '.csv', index=False)
            
    return 0
##########################################
#backtest_result(500, 'dtw', 200000)
#backtest_result(500, 'ssd', 200000)

#pair_search(criteria=[30, 0.5], train_num=506)