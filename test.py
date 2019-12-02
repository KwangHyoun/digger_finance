#%%

from data_loading import pack
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime


print('Success!')
# print(pack.PRP.price.value.head(10))


print(pack.MP.mkt_open)

test_from = '2019-01-01'
test_to = '2019-09-30'


stg_01 = (pack.PRP.price_high.value - pack.PRP.price_low.value)/(pack.PRP.price.value-pack.PRP.price_open.value)
stg_01 = stg_01.loc[pack.MP.mkt_open]
print(stg_01.loc[test_from:test_to])
stg_01 = stg_01.loc[test_from:test_to]

cond_t = pd.DataFrame(np.where((stg_01>1)&(stg_01<1.1), True, False), columns = stg_01.columns, index=stg_01.index)
print(cond_t)
stg_01 = stg_01[cond_t]
print(stg_01)

stg_01.dropna(axis=1, how='all', inplace=True)
stg_01.dropna(axis=0, how='all', inplace=True)

stg_01_w = stg_01.apply(lambda row: row/row.sum(), axis=1) # 포트폴리오 내 종목 비중
stg_01_w = stg_01_w.shift(1).dropna(axis=0, how='all') # 다음 날 구매

stg_02 = (pack.PRP.price_high.value - pack.PRP.price_low.value)/(pack.PRP.price.value-pack.PRP.price_open.value)
stg_02 = stg_02.loc[pack.MP.mkt_open]
stg_02 = stg_02.loc[test_from:test_to]

cond_t = pd.DataFrame(np.where((stg_02>1.1)&(stg_02<1000), True, False), columns=stg_02.columns, index=stg_02.index)
stg_02 = np.log(stg_02[cond_t])

stg_02.dropna(axis=1, how='all', inplace=True)
stg_02.dropna(axis=0, how='all', inplace=True)

stg_02_w = stg_02.apply(lambda row: row/row.sum(), axis=1) # 포트폴리오 내 종목 비중
stg_02_w = stg_02_w.shift(1).dropna(axis=0, how='all') # 다음 날 구매

def reduction(large_df, small_df):
    return large_df.loc[small_df.index,small_df.columns]

# Return empty DataFrame 
def plate(df):
    return pd.DataFrame(columns=df.columns, index=df.index)

# Return empty Series
def stick(df, stick_name=None):
    return pd.Series(index=df.index, name=stick_name)


# Property
## Asset1 = Asset & Remain Cash
## Asset2 = Asset & Remain Cash
class Asset:
    def __init__(self, name):
        # 1) 자산 이름
        self.asset_name = name
        
    def activate(self, init_invest, dates, items):
        # 1) init_invest : 초기 투자금액
        # 2) period : 투자 기간내 유의한 날짜(자산 배분 변화일)
        # 3) items : 투자 자산군 내 개별 종목들
        self.init_invest = init_invest # 초기 투자값
        self.portfolio = pd.DataFrame(data=np.zeros((dates.size, items.size)), # 리밸런스시 보유할 종목 수
                                      index=dates, columns=items)
        self.trade = pd.DataFrame(data=np.zeros((dates.size, items.size)), # 주문 수
                                  index=dates, columns=items)
        self.wallet = pd.DataFrame(data=np.zeros((dates.size, 3)), # 자산 가치 평가
                                  index=dates, columns=[self.asset_name, 'cash', 'total'])
        self.wallet.iloc[0].cash = init_invest
        self.wallet.iloc[0].total = init_invest

list(stg_01_w.index).index(stg_01_w.index[0])

def backtest(port_weight, deposit, trading_type='D-0O0C', asset_name='stock', fee_rate=0.00015, tax_rate=0.003):
    # 1) Port_weight : 전략에 따라 매 리밸런스기 보유해야할 종목 비중
    # 2) deposit : 최초 투자금액
    # 3) trading_type : Daily/Weekly/Monthly/Conditionally - Buy at Open/Close after n date, Sell at Open/Close after n date
    # 4) asset_name : 자산명
    # 5) fee_rate : 기관 중개 수수료
    # 6) tax_rate : 세금
    
    trading_type = trading_type.split('-')
    
    # 투자전략(매 리밸런스기 자산 분배 비율)
    asset = Asset(asset_name)
    asset.activate(deposit, port_weight.index, port_weight.columns)
    
    # trading_type에 따라 매수가격 및 매도가격 데이터프레임 설정
    price_buy = reduction(pack.PRP.price_open.value, port_weight)
    price_sell = reduction(pack.PRP.price_open.value, port_weight)
    
    def _backtesting(row):
        t = row.name
        if t!= port_weight.index[0]:
            # 리밸런스 시점 필요 주문 파악 - 매도 후 - 매수 가능
            ## 1) Wallet Total 파악
            ## 2) 필요한 주문 규모 파악
            ## 2) 매도 금액            
            asset.wallet.loc[t].total = asset.wallet.loc[t].cash + (asset.portfolio.loc[t]*price_sell.loc[t]).sum() # 현금 + 갖고있는 자산의 청산가치
            print(asset.wallet.loc[t].total)
            asset_alloc = row*asset.wallet.loc[t].total # 자산당 배정 금액
            asset.trade.loc[t] = (asset_alloc//price_buy.loc[t])-asset.portfolio.iloc[list(port_weight.index).index(row.name)-1] # 배정 금액을 바탕으로 종목별 실제 주문하는 규모
            # asset.portfolio.loc[t] = 
            # asset.trade.loc[t] -= asset.portfolio.loc[t]
            # asset.wallet.loc[t].cash += asset.trade.loc
            
        else:
            # 최초 주문시 매도 없음
            ## 1) 종목별 할당 금액 계산
            ## 2) 종목별 실제 구매 가능 수 계산 - 이후 리밸런스 신호가 오지 않는한 이 포트폴리오 유지한다고 가정
            ## 3) 리밸런스 주문
            ## 4) 리밸런스 후 자산변화(ash, asset_name, total)
            asset_alloc = row * asset.wallet.loc[t].total 
            asset.portfolio.loc[t] = asset_alloc//(price_buy.loc[t])
            asset.trade.loc[t] = asset.portfolio.loc[t]
            
        trade_buy = (asset.trade.loc[t])[asset.trade.loc[t]>0]
        trade_sell = (asset.trade.loc[t])[asset.trade.loc[t]<0]
        
        # print((trade_buy*price_buy.loc[t]).sum())
        # print('*****\n\n\n BUY\n', trade_buy, '\nSELL\n',trade_sell)
        fee_buy = (trade_buy*price_buy.loc[t]).sum()*fee_rate
        fee_sell = (trade_sell*price_sell.loc[t]).sum()*fee_rate
        tax = (trade_sell*price_sell.loc[t]).sum()*tax_rate
        cost = fee_buy + fee_sell + tax
        # print('\nCOST :',cost/10000000000000000,'\n\n')
        
        asset.wallet.loc[t:].cash = asset.wallet.loc[t].total-(trade_buy*price_buy.loc[t]).sum()+(trade_sell*price_sell.loc[t]).sum()-cost   
        
    port_weight.T.apply(lambda row: _backtesting(row))
    
    return asset


test_return = (pack.PRP.price.value/pack.PRP.price_open.value-1)
test_return = reduction(test_return, stg_02_w)

print('stg_01')
print(stg_01_w)

result1 = backtest(stg_01_w, 10000000000000000)
result2 = backtest(stg_02_w, 10000000000000000)
print(result1.wallet)

print((result2.wallet.cash - result1.wallet.cash).plot())
print('---------------result-------------------')
print(result1.wallet.cash.plot())
print(result1.wallet.stock)

# print(result.value.stock)
# print(result1.cash.plot())
print('---------------final result-------------------')
result1.wallet.cash.pct_change().plot()

