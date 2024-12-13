import pandas as pd
import numpy as np
import os
import algo_main as al
import matplotlib.pyplot as plt

#Remark: sorry for this mess, I thought it was for temperal use only......
#################### tmp function
def get_pair(num, method):
    if method == 'dtw':
        pair_list = al.dwt_find_pair(data=None, criteria=0, reload=True, reload_index=num) 
    if method == 'ssd':
        pair_list = al.ssd_find_pair(data=None, criteria=0, reload=True, reload_index=num)
    return pair_list

def max_consecutive_length(lst, element):
    max_length = 0
    current_length = 0
    for i in range(len(lst)):
        if lst[i] == element:
            current_length += 1
            max_length = max(max_length, current_length)
        else:
            current_length = 0
    return max_length

def get_voo_stat():
    data = pd.read_csv("D:/project/data/sp500/voo.csv")
    data = data[['Date', 'Close/Last']]
    
    tmp1 = data.index[data['Date'] == '11/01/2024'].values[0]
    tmp2 = data.index[data['Date'] == '11/01/2021'].values[0]
    
    data = data.iloc[tmp1:tmp2+1]
    
    return data['Close/Last'].values.tolist()

################### working function

def get_summary_data(num, method):
    summary = []
    summary_columns = ['name', 'max_drawdown', 'total_return', 'std', 'idle']
    pair_list = get_pair(num, method)
    for pair in pair_list:
        
        file_name = pair[0] + '&' + pair[1]
        if method == 'dtw':
            file_path = 'D:/data/algo_package/trade_review_dtw/' + file_name + '.csv'
        if method == 'ssd': 
            file_path = 'D:/data/algo_package/trade_review_ssd/' + file_name + '.csv'
        data = pd.read_csv(file_path)
        
        value = data['value']
        position_inc = data['in_positon']
        
        maxdown = min(value)
        total_return = (value[len(value)-1] - value[0]) / value[0]
        idle_time = position_inc[~position_inc].shape[0]
        value_std = np.std(value)
        #sharpe_ratio = total_return / value_std
        
        summary.append([file_name, maxdown, total_return, value_std, idle_time])
    
    summary = pd.DataFrame(summary, columns=summary_columns)
    summary.to_csv('D:/data/algo_package/all_trade_review_' + method + '.csv', index=False)
        
    return summary

def get_full_review(num, method):
    pair_list = get_pair(num, method)
    value = np.zeros(750)
    for pair in pair_list:
        file_name = pair[0] + '&' + pair[1]
        if method == 'dtw':
            file_path = 'D:/project/results/trade_review_dtw/' + file_name + '.csv'
        if method == 'ssd': 
            file_path = 'D:/project/results/trade_review_ssd/' + file_name + '.csv'
        data = pd.read_csv(file_path)
        value += data['value']
    value = value.dropna()

    maxdown = min(value)/value[0] * 100
    percentage_change = (value[len(value)-1] - value[0]) / value[0] * 100
    std = np.std(value)/value[0]
    sharpe = percentage_change/100/std
    
    feature = [maxdown, percentage_change, std, sharpe]

    val = pd.DataFrame(value, columns=['value'])
    #val.to_csv('D:/data/algo_package/total_value.csv')
        
    return feature, val

def get_pair_review(pair, method, rank):
    pair_name = pair[0] + '&' + pair[1]
    path_name = 'D:/project/results/trade_review_' + method + '/' + pair_name + '.csv'
    trade_data = pd.read_csv(path_name)
    
    in_position = trade_data['in_positon'].tolist()
    value = trade_data['value'].tolist()
    
    max_divergence = min(value)
    std = np.std(value)
    gain = (value[-1] - value[0]) / value[0]
    
    is_divergence = False
    trade_enter_point = 0
    enter_point_index = []
    close_point_index = []
    
    #print(in_position[-2])
    if in_position[-2] == True:
        is_divergence = True
    
    if in_position[0] == True:
        trade_enter_point += 1
        enter_point_index.append(0)
    for i in range(len(in_position)):
        if in_position[i] == True and in_position[i-1] == False:
            trade_enter_point += 1
            enter_point_index.append(i)
    
    trade_converge_time = []
    gain_per_converge = []
    timer = 0
    for index in enter_point_index:
        for j in range(index, len(in_position)):
            timer += 1
            if in_position[j] == False:
                close_point_index.append(j)
                break
        trade_converge_time.append(timer)
        timer = 0
        
    for i in range(len(enter_point_index)):
        gain_per_converge.append((value[close_point_index[i]] - value[enter_point_index[i]]) / value[enter_point_index[i]])
    
    review_list = [pair_name, method, rank, gain, max_divergence, std,
                   trade_enter_point, np.mean(trade_converge_time), np.mean(gain_per_converge), is_divergence]
    
    print("Review " + str(pair_name) + " " + str(method) + " done")
    
    return review_list

def get_all_pair_review(num):
    
    for method in ['dtw', 'ssd']:
        
        pair_list = get_pair(num, method)
        rank = 1
        review_list = []
        
        for pair in pair_list:
            review = get_pair_review(pair, method, rank)
            rank += 1
            review_list.append(review)
            
        review_df = pd.DataFrame(review_list, columns=['pair', 'method', 'rank', 'gain','max_divergence','std',
                                                       'trade_enter_point', 'avg_converge_time', 'avg_gain_per_converge', 'is_divergence'])
        review_df.to_csv('D:/project/results/trade_review_all_summary/all_pair_review_' + method + '.csv', index=False)
            
    return review_list
            
############################ plotting function
# all review using meta data
def plotting(voo):
    df1 = pd.read_csv("D:/project/results/aggregated_portfolio_review/meta_dtw.csv")
    df2 = pd.read_csv("D:/project/results/aggregated_portfolio_review/meta_ssd.csv")
    
    columns = df1.columns
    plt.figure(figsize=(8, 6))

    voo_maxdown = min(voo)/voo[-1] * 100
    voo_return = (voo[0] - voo[-1])/voo[-1] * 100
    std = np.std(voo)/voo[-1]
    voo_sharpe = voo_return/std/100

    for column in columns:
        plt.plot(df1[column], label='dtw', linestyle='-')
        plt.plot(df2[column], label='ssd', linestyle='--')
        if column == columns[0]:
            plt.axhline(y=voo_maxdown, color='g', linestyle='--', label='voo')
        if column == columns[1]:
            plt.axhline(y=voo_return, color='g', linestyle='--', label='voo')
        if column == columns[2]:
            plt.axhline(y=std, color='g', linestyle='--', label='voo')
        if column == columns[3]:
            plt.axhline(y=voo_sharpe, color='g', linestyle='--', label='voo')
        plt.title(f'Comparison of {column}')
        plt.xlabel('number of top rank pairs')
        plt.ylabel(column)
        plt.legend()
        plt.grid(True)
        print("doing")
        #plt.show()
        plt.savefig('D:/project/results/plot/aggre_port_review_plot/comparison_' + column + '.png')
        plt.close()

    return 0

# graph of a rank num pair
def plotting2(num):
    pair_record_dtw = pd.read_csv("D:/project/results/pair/dwt.csv")
    pair_record_ssd = pd.read_csv("D:/project/results/pair/ssd.csv")
    ssd_sample_1 = pair_record_ssd.iloc[num, 0]
    ssd_sample_2 = pair_record_ssd.iloc[num, 1]
    dtw_sample_1 = pair_record_dtw.iloc[num, 0]
    dtw_sample_2 = pair_record_dtw.iloc[num, 1]
    
    train, tmp = al.data_import()
    train_norm, tmp2, tmp3 = al.data_preprocess(train, tmp)
    
    dtw_series_1 = train_norm[dtw_sample_1]
    dtw_series_2 = train_norm[dtw_sample_2]
    
    ssd_series_1 = train_norm[ssd_sample_1]
    ssd_series_2 = train_norm[ssd_sample_2]

    dtw_std = np.std( dtw_series_1  - dtw_series_2 )
    ssd_std = np.std( ssd_series_1  - ssd_series_2 )

    plt.figure(figsize=(4, 3))
    for element in ['dtw', 'ssd']:
        if element == 'dtw':
            plt.figure(figsize=(4, 3))
            plt.plot(dtw_series_1, label=dtw_sample_1, linestyle='-')
            plt.plot(dtw_series_2, label=dtw_sample_2, linestyle='--')
            plt.title(f'DTW Comparison of {dtw_sample_1} and {dtw_sample_2}')
            plt.xlabel('time')
            plt.ylabel('normalized value')
            plt.legend()
            plt.grid(True)
            plt.savefig('D:/project/results/plot/example/dtw_comparison_' + dtw_sample_1 + '&' + dtw_sample_2 + '.png')
            plt.close()
        else:
            plt.figure(figsize=(4, 3))
            plt.plot(ssd_series_1, label=ssd_sample_1, linestyle='-')
            plt.plot(ssd_series_2, label=ssd_sample_2, linestyle='--')
            plt.title(f'SSD Comparison of {ssd_sample_1} and {ssd_sample_2}')
            plt.xlabel('time')
            plt.ylabel('normalized value')
            plt.legend()
            plt.grid(True)
            plt.savefig('D:/project/results/plot/example/ssd_comparison_' + ssd_sample_1 + '&' + ssd_sample_2 + '.png')
            plt.close()
            
    print([dtw_std, ssd_std])
            
    return [dtw_std, ssd_std]

def plotting3():
    dtw_review = pd.read_csv('D:/project/results/trade_review_all_summary/all_pair_review_dtw.csv')
    ssd_review = pd.read_csv('D:/project/results/trade_review_all_summary/all_pair_review_ssd.csv')
    
    for column in dtw_review.columns:
        plt.plot(dtw_review[column], label='dtw', linestyle='-')
        plt.plot(ssd_review[column], label='ssd', linestyle='--')
        plt.title(f'Comparison of {column}')
        plt.xlabel('number of top rank pairs')
        plt.ylabel(column)
        plt.legend()
        plt.grid(True)
        
        plt.savefig('D:/project/results/plot/comparison_' + column + '.png')
        plt.close()
    
    return 0

def review_ccal_tmp(data):
    
    non_profit = data[data['gain'] < 0]
    profit = data[data['gain'] > 0]
    
    non_profit_percent = non_profit.shape[0] /50 *100
    average_loss = np.sum(non_profit['gain'])/ non_profit.shape[0]
    average_gain = np.sum(profit['gain'])/( 50 - non_profit.shape[0] )
    
    output = [int(non_profit_percent), round(average_loss,4), round(average_gain,4)]
    #print(output)
    #print(np.sum(non_profit['gain']) - np.sum(profit['gain']))
    
    average_open_num = np.sum(data['trade_enter_point']) / 50
    
    total_time = np.sum(profit['avg_converge_time'] * profit['trade_enter_point'])
    average_time = total_time / np.sum(profit['trade_enter_point'])
    
    average_maxdown = np.sum(data['max_divergence'])/ 50 / 10000
    
    output2 = [average_open_num, round(average_time,4) , round(average_maxdown,4)]
    print(output2)
    
    return output

def review_indi():
    ssd_data = pd.read_csv('D:/project/results/trade_review_all_summary/all_pair_review_ssd.csv')
    dtw_data = pd.read_csv('D:/project/results/trade_review_all_summary/all_pair_review_dtw.csv')

    dtw_data_list = []
    ssd_data_list = []
    for i in range(10):
        dtw_data_list.append( dtw_data[(dtw_data['rank'] <= (i+1)*50) & (dtw_data['rank'] > 50*i)]  )
        ssd_data_list.append( ssd_data[(ssd_data['rank'] <= (i+1)*50) & (ssd_data['rank'] > 50*i)]  )
        #if i == 7:
            #print(ssd_data[(ssd_data['rank'] <= (i+1)*50) & (ssd_data['rank'] > 50*i)] )

    review_1_list = []
    for j in range(10):
        print('\n'+'dtw'+str(j*50))
        tmp1 = review_ccal_tmp(dtw_data_list[j])
        review_1_list.append(tmp1)
        print('ssd'+str(j*50))
        tmp2 = review_ccal_tmp(ssd_data_list[j])
        review_1_list.append(tmp2)

   
    return 0
############################################################
def main():

    dtw_meta_summaries = []
    ssd_meta_summaries = []
    for num in range(1, 501):
        for method in ['dtw', 'ssd']:
           feature, val = get_full_review(num, method)
           if method == 'dtw':
                dtw_meta_summaries.append(feature)
                print(f'DTW {num}th summary')
           else:
                ssd_meta_summaries.append(feature)
                print(f'SSD {num}th summary')
        
    dtw_meta_summaries = pd.DataFrame(dtw_meta_summaries, columns=['max drawdown in percentage', 'total return in percentage','normalized standard deviation', 'sharpe ratio'])
    ssd_meta_summaries = pd.DataFrame(ssd_meta_summaries, columns=['max drawdown in percentage', 'total return in percentage','normalized standard deviation', 'sharpe ratio'])
    dtw_meta_summaries.to_csv("D:/project/results/aggregated_portfolio_review/meta_dtw.csv", index=False)
    ssd_meta_summaries.to_csv("D:/project/results/aggregated_portfolio_review/meta_ssd.csv", index=False)
    
    voo = get_voo_stat()
    plotting(voo)

    return 0
############################################################
#main()
#plotting(get_voo_stat())
#plotting2(199)
review_indi()
#get_all_pair_review(500)