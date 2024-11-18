# algo_test

The idea is to find the stock that are similar to do pair trade, open the position when the price of stock diverge, close when they converge

0) data are S&P 500 stock close price, trade day of 2019 Nov 1 - 2021 Nov 1 as train data, trade day of 2021 Nov 1 - 2024 Nov 1 as test data(trading peroid)

1) preprocess
1.1) remove all the stock that have null in training data (12 of them)
1.2) the price data is normalized by divided to their mean

2) dynamic time warping(dtw) / squared sum distance(ssd) (ssd as comparision) (for yi please provide some intro to them)
2.1) good thing about dwt: allow for comparison of different length 
