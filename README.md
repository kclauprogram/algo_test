# algo_test

ref: https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=598dcc162548d1deabc9ef8eaa2de7609b7c7682#page=53
https://proceedings.neurips.cc/paper/2019/file/02f063c236c7eef66324b432b748d15d-Paper.pdf

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

3) dtw training detail   
3.1) not original dtw which is slow, we use fastdtw ( take average on 2 adjacent data point, the size to train reduce to half, but the distance path is not optimal(smallest) )
3.2) sort the pair arcording to the dtw distance ascendingly 

4) trade execution detail
4.1) pick the first n pairs based on previous criteria
4.2) open the position when the pairs gap > the mean of absolute distance of pairs * 2 , close the position when their price cross(previous open when a>b, close when a<b)
4.3) close the position when trade period end, severely punish the diverge pairs

5) review
5.1) comparison on the return, sharpe ratio on dwt trade, ssd trair and simple buy and hold
5.2) comparsion on the n (number of pairs picked to trade) effects on dtw trade and ssd trade
