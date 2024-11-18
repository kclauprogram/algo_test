# algo_test

The idea is to find the stock that are similar to do pair trade, open the position when the price of stock diverge, close when they converge

0) data are S&P 500 stock close price, trade day of 2019 Nov 1 - 2021 Nov 1 as train data, trade day of 2021 Nov 1 - 2024 Nov 1 as test data(trading peroid)

1) preprocess
1.1) remove all the stock that have null in training data (12 of them)
1.2) the price data is normalized by divided to their mean
1.3) total 119316 pair to be tested


2) dynamic time warping(dtw) / squared sum distance(ssd) (ssd as comparision) (for yi please provide some intro to them)
2.1) good thing about dwt: allow for comparison of different length(some stock may have different length and ssd cannot directly be calculated)
2.2) less strict on the variance, allow for more profitable pairs (minimize ssd is equal to minimize the pair variance, so the stock should diverge less on the pair found by ssd)
2.3) comparision is done by introducing some time lag, capture the relationship of stocks better (ssd directly compare the price on the same day, but even the stocks are similar, they may not react the same magnitide the same day due to time needed for information to flow, which one of the crucial explanation on why pair trade workings, ssd failed to capture this feature)
2.4) drawback on dwt: VERY VERY time-consuming ( O(n^2) complexity, especially when we have > 100000 pair)

3)dtw trainig detail   
