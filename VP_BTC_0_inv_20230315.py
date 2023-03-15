#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import pyupbit
import datetime
import pandas as pd
import numpy as np
import warnings

#from scipy.signal import savgol_filter
#from scipy.signal import savitzky_golay

#import matplotlib.pyplot as plt


# In[2]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)


# In[3]:


candle_type = '60min'
#candle_type = 'day'

if candle_type == '1min' :
    candle_adapt = 'minute1'
    time_unit = 1
elif candle_type == '3min' :
    candle_adapt = 'minute3'
    time_unit = 3
elif candle_type == '5min' :
    candle_adapt = 'minute5'
    time_unit = 5
elif candle_type == '10min' :
    candle_adapt = 'minute10'
    time_unit = 10
elif candle_type == '15min' :
    candle_adapt = 'minute15'
    time_unit = 15
elif candle_type == '30min' :
    candle_adapt = 'minute30'
    time_unit = 30
elif candle_type == '60min' :
    candle_adapt = 'minute60'
    time_unit = 60
elif candle_type == '240min' :
    candle_adapt = 'minute240'
    time_unit = 240
elif candle_type == 'day' :
    candle_adapt = 'day'
    time_unit = (60 * 24)
elif candle_type == 'month' :
    candle_adapt = 'month'
    time_unit = 60 * 24 * 30


# In[4]:


# 몇건의 과거 이력을 참조할 것인가

candle_count = int(60/time_unit) * 300


# In[5]:


# 전체 자산 중 몇 % 자산을 투자할 것인가?

invest_ratio = 0.1   # 보유 금액의 최대 몇 % 를 투자할것인가 (예> 0.1 <-- 보유금액 10% 투자) 


# In[6]:


# 투자 대상 코인
#coin_No = 0
coin_inv = 'KRW-BTC'
check_currency = 'KRW'


# In[7]:


# 기본 조건

### moving average 산출 구간 설정
ma_duration_short = 7   # 단기 ma 산출 기간
ma_duration_mid = 15   # 단기 ma 산출 기간
ma_duration_long = 30   # 장기 ma 산출 기간

### stochastic 산출 구간 설정
slow_sto_k_duration = 100   # slow stochastic_k 산출 기간
slow_sto_d_duration = 30   # slow stochastic_k 산출 기간

transaction_fee_ratio = 0.0005   # 거래 수수료 비율

time_factor = 9   # 클라우드 서버와 한국과의 시차


# In[8]:


# 정식 조건

# 매수, 매도 조건

### buy_transaction 조건값 설정
ma_short_under_duration = 6   # 최근 몇개 기간동안의 ma_short의추이를 살펴볼것인지 지정
ema_long_duration = 30
buy_cri_vol_times = 0.8   # 전 구간 평균 거래량 대비, 직전 구간 (또는 직전직전 구간)에서 거래량이 얼마 이상이여야 buy_transaction을 수행할 것인가
vol_duration = 12   # 몇 개월 동안의 평균 거래량 기준으로 ref vol을 설정할 것인가
ratio_ema_o_short_long_buy_1 = [1.005, 1.007]
ratio_ema_long_1 = 1.0003   # 현재 구간에서의 ema_long값과 직전구간 ema_long값의 비율이 얼마 이상일때 buy transaction을 수행하는가 (여러 필요 조건중의 하나)
buy_price_up_unit = 2   # 매수시 몇 가격 unit 까지 상향해서 구매할 것인가
decrese_day_duration = 22
ratio_ema_o_short_long_buy_2 = [1.002, 1.004]
ratio_ema_long_2 = 1.0004

### sell transaction 조건값 설정
sellable_profit = 0.0   # 판매가능 이익율
sell_force_loss = 0.02   # 강제 판매 손실율
sell_ma_long_ratio = 1.00059   # 1.00059
slow_sto_k_cri = 0.9
slow_sto_k_count = 1
ratio_sell_ema_long_chg_state = 0.9999   # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)
ratio_sell_ema_mid_chg_state = 0.9995   # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)


# In[9]:


# For Test
'''
# 매수, 매도 조건

### buy_transaction 조건값 설정
ma_short_under_duration = 6   # 최근 몇개 기간동안의 ma_short의추이를 살펴볼것인지 지정
ema_long_duration = 30
buy_cri_vol_times = 0.1   # 전 구간 평균 거래량 대비, 직전 구간 (또는 직전직전 구간)에서 거래량이 얼마 이상이여야 buy_transaction을 수행할 것인가
vol_duration = 12   # 몇 개월 동안의 평균 거래량 기준으로 ref vol을 설정할 것인가
ratio_ema_o_short_long = [1.001, 1.01]
ratio_ema_long = 1.0001   # 현재 구간에서의 ema_long값과 직전구간 ema_long값의 비율이 얼마 이상일때 buy transaction을 수행하는가 (여러 필요 조건중의 하나)
buy_price_up_unit = 2   # 매수시 몇 가격 unit 까지 상향해서 구매할 것인가

### sell transaction 조건값 설정
sellable_profit = 0.0   # 판매가능 이익율
sell_force_loss = 0.02   # 강제 판매 손실율
sell_ma_long_ratio = 1.003   # 1.00059
slow_sto_k_cri = 0.5
slow_sto_k_count = 1
ratio_sell_ema_long_chg_state = 1.0001   # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)
'''


# In[10]:


#업비트 계정 설정

access_key = "ixWxT1mblIf6FJ7afaS3MLZ1eyovfIcTwSapB2VD"
secret_key = "Fll2k01gQthoKrdAhjcTFcYrh0o7Dejtzp4J6J0R"

upbit = pyupbit.Upbit(access_key, secret_key)


# In[11]:


tickers = pyupbit.get_tickers()

LIST_coin_KRW = []

for i in range (0, len(tickers), 1):
    if tickers[i][0:3] == 'KRW':
        LIST_coin_KRW.append(tickers[i])

LIST_check_coin_currency = []

for i in range (0, len(LIST_coin_KRW), 1):
    LIST_check_coin_currency.append(LIST_coin_KRW[i][4:])

LIST_check_coin_currency_2 = []

for i in range (0, len(LIST_check_coin_currency), 1) :
    temp = 'KRW-' + LIST_check_coin_currency[i]
    LIST_check_coin_currency_2.append(temp)


# In[12]:


# 잔고 조회, 현재가 조회 함수 정의

def get_balance(target_currency):   # 현급 잔고 조회
    """잔고 조회"""
    balances = upbit.get_balances()   # 통화단위, 잔고 등이 Dictionary 형태로 balance에 저장
    for b in balances:
        if b['currency'] == target_currency:   # 화폐단위('KRW', 'KRW-BTC' 등)에 해당하는 잔고 출력
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_balance_locked(target_currency):   # 거래가 예약되어 있는 잔고 조회
    """잔고 조회"""
    balances = upbit.get_balances()   # 통화단위, 잔고 등이 Dictionary 형태로 balance에 저장
    for b in balances:
        if b['currency'] == target_currency:   # 화폐단위('KRW', 'KRW-BTC' 등)에 해당하는 잔고 출력
            if b['locked'] is not None:
                return float(b['locked'])
            else:
                return 0
    return 0

def get_avg_buy_price(target_currency):   # 거래가 예약되어 있는 잔고 조회
    """평균 매수가 조회"""
    balances = upbit.get_balances()   # 통화단위, 잔고 등이 Dictionary 형태로 balance에 저장
    for b in balances:
        if b['currency'] == target_currency:   # 화폐단위('KRW', 'KRW-BTC' 등)에 해당하는 잔고 출력
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0

'''
def get_current_price(invest_coin):
    """현재가 조회"""
    #return pyupbit.get_orderbook(tickers=invest_coin)[0]["orderbook_units"][0]["ask_price"]
    return pyupbit.get_current_price(invest_coin)
'''
#price = pyupbit.get_current_price("KRW-BTC")


# In[13]:


# Reference 거래량 설정

DF_volume_cri = pyupbit.get_ohlcv(coin_inv, count = vol_duration , interval = 'month')
volume_cri = DF_volume_cri['volume'].sum() / int((60/time_unit) * 24 * 30 * vol_duration) 


# In[14]:


print('volume_cri : ', volume_cri)


# In[15]:


#DF_raw = pyupbit.get_ohlcv(LIST_check_coin_currency_2[coin_No], count = candle_count, interval = candle_adapt)

#DF_test = DF_raw.copy()


# In[16]:


# 매수 최소단위 산출
unit_factor = 0
unit_value = 0

def unit_value_calc (DF_test) :
    if DF_test['open'][-1] >= 1000000 :  # 200만원 이상은 거래단위가 1000원, 100~200만원은 거래단위가 500원이지만 편의상 200만원 이상과 함께 처리
        unit_factor = -3
        unit_value = 1000
    elif DF_test['open'][-1] >= 100000 :
        unit_factor = -2
        unit_value = 50
    elif DF_test['open'][-1] >= 10000 :
        unit_factor = -1
        unit_value = 10
    elif DF_test['open'][-1] >= 1000 :
        unit_factor = -1
        unit_value = 5
    elif DF_test['open'][-1] >= 100 :
        unit_factor = 0
        unit_value = 1
    else :
        unit_factor = 1
        unit_value = 0.1
        
    return unit_value

print ('DF_volume_cri[open][-1] : {0}  / unit_value : {1}'.format(DF_volume_cri['open'][-1], unit_value_calc(DF_volume_cri)))


# In[17]:


#Moving average 산출

def DF_mv (DF_mv_target) :
    DF_mv_target['ratio_prior_to_cur'] = DF_mv_target['open'] / DF_mv_target['open'].shift(1)
    DF_mv_target['ratio_vol_to_aver'] = DF_mv_target['volume'] / volume_cri
    
    DF_mv_target['ema_open_short'] = DF_mv_target['open'].ewm(span = ma_duration_short, adjust=False).mean()
    DF_mv_target['ema_open_mid'] = DF_mv_target['open'].ewm(span = ma_duration_mid, adjust=False).mean()
    DF_mv_target['ema_open_long'] = DF_mv_target['open'].ewm(span = ma_duration_long, adjust=False).mean()
    
    DF_mv_target['diff_s_l'] = DF_mv_target['ema_open_short'] - DF_mv_target['ema_open_long']
    DF_mv_target['diff_s_m'] = DF_mv_target['ema_open_short'] - DF_mv_target['ema_open_mid']
    
    DF_mv_target['ema_o_s_consecutive_rise'] = 0
    DF_mv_target['ema_o_m_consecutive_rise'] = 0
    DF_mv_target['ema_o_l_consecutive_rise'] = 0
    
    for i in range (0, len(DF_mv_target), 1) :
        if (DF_mv_target['ema_open_short'][i] > DF_mv_target['ema_open_short'][i-1]) :
            DF_mv_target['ema_o_s_consecutive_rise'][i] = 1
        if (DF_mv_target['ema_open_mid'][i] > DF_mv_target['ema_open_mid'][i-1]) :
            DF_mv_target['ema_o_m_consecutive_rise'][i] = 1
        if (DF_mv_target['ema_open_long'][i] > DF_mv_target['ema_open_long'][i-1]) :
            DF_mv_target['ema_o_l_consecutive_rise'][i] = 1
    
    return DF_mv_target


# In[18]:


#Stochastic 산출

def DF_stochastic (DF_target_stochastic) :
    DF_target_stochastic['sto_max_in_dur'] = 0
    DF_target_stochastic['sto_min_in_dur'] = 0
    DF_target_stochastic['slow_sto_k'] = 0
    DF_target_stochastic['slow_sto_k_on'] = 0
    
    for i in range (slow_sto_k_duration, len(DF_target_stochastic), 1) :
        DF_target_stochastic['sto_max_in_dur'][i] = DF_target_stochastic.loc[DF_target_stochastic.iloc[(i - (slow_sto_k_duration-1)) : (i + 1)]['high'].idxmax()]['high']
        DF_target_stochastic['sto_min_in_dur'][i] = DF_target_stochastic.loc[DF_target_stochastic.iloc[(i - (slow_sto_k_duration-1)) : (i + 1)]['low'].idxmin()]['low']
        
    DF_target_stochastic['slow_sto_k'] = (DF_target_stochastic['open'] - DF_target_stochastic['sto_min_in_dur']) / (DF_target_stochastic['sto_max_in_dur'] - DF_target_stochastic['sto_min_in_dur'])
    #DF_test['slow_sto_d'] = DF_test['slow_sto_k'].rolling(slow_sto_d_duration).mean()
    
    for j in range (slow_sto_k_duration, len(DF_target_stochastic), 1) :
        #if (DF_target_stochastic['slow_sto_k'][j] > slow_sto_k_cri) and (DF_target_stochastic['slow_sto_k'][j] < 1.0) :
        if (DF_target_stochastic['slow_sto_k'][j] > slow_sto_k_cri) :
            DF_target_stochastic['slow_sto_k_on'][j] = 1
            
    return DF_target_stochastic


# In[ ]:





# In[19]:


bought_state = 0
bought_price = 0


# In[ ]:


# 정식 매수/매도 로직

currrent_price = 1

while True:
    try :
        now = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
        print ('bought_state : {0}   / now : {1}'.format(bought_state, now))
        
        if (now.minute % time_unit == 1) & (0 < (now.second % 60) <= 15) :   # N시:01:00초 ~ N시:01:15초 사이 시각이면
            balances = upbit.get_balances()
            print ('current_aseet_status\n', balances)
            
            if bought_state == 0 :   # 매수가 없는 상태라면
                DF_invest_check = pyupbit.get_ohlcv(coin_inv, count = candle_count, interval = candle_adapt)
                
                DF_test_ma = DF_mv (DF_invest_check)
                print('DF_test_ma :\n', DF_test_ma)
                
                DF_test_stochastic = DF_stochastic (DF_test_ma)
                print('DF_test_stochastic :\n', DF_test_stochastic)
                
                print ('\n[BUY condition check]')
                print ('DF_test_stochastic[ema_o_l_consecutive_rise][-(ema_long_duration + 1) : -1].sum()_____[condition] greater {0} / [value] {1}'.format(5, DF_test_stochastic['ema_o_l_consecutive_rise'][-(ema_long_duration + 1) : -1].sum()))
                print ('DF_test_stochastic[ema_o_s_consecutive_rise][-(ma_short_under_duration + 1) : -1].sum()_____[condition] greater/equal than {0} / [value] {1}'.format((ma_short_under_duration - 1), DF_test_stochastic['ema_o_s_consecutive_rise'][-(ma_short_under_duration + 1) : -1].sum()))
                print ('DF_test_stochastic[ema_open_long][-1] / DF_test_stochastic[ema_open_long][-2])_____[condition] greater than {0} / [value] {1}'.format(ratio_ema_long_1, (DF_test_stochastic['ema_open_long'][-1] / DF_test_stochastic['ema_open_long'][-2])))
                print ('DF_test_stochastic[ratio_vol_to_aver][-2]____[condition] greater than {0} / [value] {1}'.format(buy_cri_vol_times, DF_test_stochastic['ratio_vol_to_aver'][-2]))
                print ('OR__DF_test_stochastic[ratio_vol_to_aver][-1]_____[condition] greater than {0} / [value] {1}'.format(buy_cri_vol_times, DF_test_stochastic['ratio_vol_to_aver'][-1]))
                print ('DF_test_stochastic[ema_open_short][-1] / DF_test_stochastic[ema_open_long][-1]_____[condition] greater than {0} / [value] {1}'.format(ratio_ema_o_short_long_buy_1[0], (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1])))
                print ('DF_test_stochastic[ema_open_short][-1] / DF_test_stochastic[ema_open_long][-1]_____[condition] Less than {0} / [value] {1}'.format(ratio_ema_o_short_long_buy_1[1], (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1])))
                
                # 매수 영역
                if ((DF_test_stochastic['ema_o_l_consecutive_rise'][-(ema_long_duration + 1) : -1].sum() > 5) and                     (DF_test_stochastic['ema_o_s_consecutive_rise'][-(ma_short_under_duration + 1) : -1].sum() > (ma_short_under_duration - 2)) and                     ((DF_test_stochastic['ema_open_long'][-1] / DF_test_stochastic['ema_open_long'][-2]) > ratio_ema_long_1) and                     ((DF_test_stochastic['ratio_vol_to_aver'][-3] > buy_cri_vol_times) or (DF_test_stochastic['ratio_vol_to_aver'][-2] > buy_cri_vol_times)) and                     (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1] > ratio_ema_o_short_long_buy_1[0]) and (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1] < ratio_ema_o_short_long_buy_1[1])) or                 ((DF_test_stochastic['ema_o_l_consecutive_rise'][-(ema_long_duration + 1) : -1].sum() > 5) and                  (DF_test_stochastic['ema_o_s_consecutive_rise'][-(ma_short_under_duration + 1) : -1].sum() > 1) and                  ((DF_test_stochastic.loc[DF_test_stochastic.iloc[-(decrese_day_duration + 1) : -1]['ema_open_long'].idxmin()]['ema_open_long'] * 1.0019) > DF_test_stochastic['ema_open_long'][-1]) and                  ((DF_test_stochastic['ratio_vol_to_aver'][-3] > (0.7 * buy_cri_vol_times)) or (DF_test_stochastic['ratio_vol_to_aver'][-2] > (0.7 * buy_cri_vol_times))) and                  (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1] > ratio_ema_o_short_long_buy_2[0]) and (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1] < ratio_ema_o_short_long_buy_2[1]) and                  ((DF_test_stochastic['ema_open_long'][-1] / DF_test_stochastic['ema_open_long'][-2]) > ratio_ema_long_2)) :
                    
                    print ('$$$$$ [{0}] buying_transaction is coducting $$$$$'.format(coin_inv))
                    
                    investable_budget = (get_balance(check_currency) + upbit.get_amount('ALL')) * invest_ratio
                    buying_volume = (investable_budget * (1 - transaction_fee_ratio)) / pyupbit.get_current_price(coin_inv)
                    currrent_price = pyupbit.get_current_price(coin_inv)
                    print ('\ncurrent_price : ', currrent_price)
                    buyable_price = currrent_price + (buy_price_up_unit * unit_value_calc(DF_invest_check))
                    print ('investable_budget : {0} / currrent_price : {1} / buying_volume : {2}'.format(investable_budget, currrent_price, buying_volume))
                    
                    #transaction_buy = upbit.buy_market_order(coin_inv, investable_budget)   # 시장가로 매수
                    transaction_buy1 = upbit.buy_limit_order(coin_inv, buyable_price, buying_volume)   # 지정가로 매수
                    time.sleep(10)
                    print ('buy_1ST_transaction_result :', transaction_buy1)
                    print ('time : {0}  /  buying_target_volume : {1}  /  bought_volume_until_now : {2}'.format((datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))), buying_volume, get_balance(coin_inv[4:])))
                    
                    if get_balance(coin_inv[4:]) <= (0.95 * buying_volume) :
                        now2 = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
                        while (0 <= (now2.minute % time_unit) <= 10) :   # 0분에서 10분 사이면
                            print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                            if (pyupbit.get_current_price(coin_inv) / currrent_price) < (1 - sell_force_loss) :   # 강제 매도 가격 이하로 현재가격이 하락하게 되면
                                transaction_buy_cancel1 = upbit.cancel_order(transaction_buy1['uuid'])   # 미처 못산 매수물량 취소
                                transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
                                time.sleep(5)
                                bought_state = 0
                                print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                                print ('sell_transaction_result_BY_FORCED_SELLING_in the WHILE_loop :', transaction_sell)
                            
                            time.sleep(1)
                            now2 = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
                            
                        transaction_buy_cancel1 = upbit.cancel_order(transaction_buy1['uuid'])
                        
                        
        # 매수 상태 점검
        if get_balance(coin_inv[4:]) > 0 :
            bought_state = 1
            print ('bought_state_in mid check : {0}'.format(bought_state))
            
        else :
            bought_state = 0
            print ('bought_state_in mid check : {0}'.format(bought_state))
            
        #매도 영역
        now3 = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
        if (now3.minute % time_unit == 1) & (0 < (now.second % 60) <= 15) :   # N시:01:00초 ~ N시:01:15초 사이 시각이면
            balances2 = upbit.get_balances()
            print ('current_aseet_status\n', balances2)
            
            if bought_state == 1 :   # 매수가 되어 있는 상태라면
                print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                print ('\n bought_state : {0}  [[[[[[[[[[[[ coin___{1} selling condition checking]]]]]]]]]] :'.format(bought_state, coin_inv))
                DF_invest_check_SELL = pyupbit.get_ohlcv(coin_inv, count = candle_count, interval = candle_adapt)
                DF_mov_avg_check_SELL = DF_mv (DF_invest_check_SELL)
                DF_stochastic_SELL = DF_stochastic (DF_mov_avg_check_SELL)
                
                print ('DF_stochastic_SELL\n', DF_stochastic_SELL)
                
                # 권장되는 매도 영역 판단
                
                print ('\nNORMAL SELL condition checking')
                print('DF_stochastic_SELL[open][-1] / currrent_price)_____[condition] greater than {0} / [value] {1}'.format((1 + sellable_profit), (DF_stochastic_SELL['open'][-1] / currrent_price)))
                print('DF_stochastic_SELL.iloc[-4 : -3][slow_sto_k_on].sum()_____[condition] greater/equal than {0} / [value] {1}'.format(slow_sto_k_count, DF_stochastic_SELL.iloc[-4 : -3]['slow_sto_k_on'].sum()))
                print('DF_stochastic_SELL.loc[DF_stochastic_SELL.iloc[-5 : -2][slow_sto_k].idxmax()][slow_sto_k]_____[condition] greater than {0} / [value] {1}'.format(slow_sto_k_cri, DF_stochastic_SELL.loc[DF_stochastic_SELL.iloc[-5 : -2]['slow_sto_k'].idxmax()]['slow_sto_k']))
                print('DF_stochastic_SELL[slow_sto_k][-1]_____[condition] Less than {0} / [value] {1}'.format((slow_sto_k_cri - 0.09), DF_stochastic_SELL['slow_sto_k'][-1]))
                print('DF_stochastic_SELL[ema_open_long][-1] / DF_stochastic_SELL[ema_open_long][-2]_____[condition] Less than {0} / [value] {1}'.format(sell_ma_long_ratio, (DF_stochastic_SELL['ema_open_long'][-1] / DF_stochastic_SELL['ema_open_long'][-2])))    
                
                if ((DF_stochastic_SELL['open'][-1] / currrent_price) > (1 + sellable_profit)) and                 ((DF_stochastic_SELL.iloc[-5 : -4]['slow_sto_k_on'].sum()) >= slow_sto_k_count) and                 (DF_stochastic_SELL.loc[DF_stochastic_SELL.iloc[-5 : -2]['slow_sto_k'].idxmax()]['slow_sto_k'] > slow_sto_k_cri) and (DF_stochastic_SELL['slow_sto_k'][-1] < (slow_sto_k_cri - 0.09)) and                 ((DF_stochastic_SELL['ema_open_long'][-1] / DF_stochastic_SELL['ema_open_long'][-2]) < sell_ma_long_ratio) :
                    
                    transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
                    time.sleep(5)
                    print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                    print ('sell_transaction_result_BY_ NORMAL _SELLING :', transaction_sell)
                    
                    bought_state = 0
                    
                    time.sleep(5)
                    
                
                # 추세 변화에 따른 매도 영역 판단
                print ('\nSTATE_CHANGE SELL condition checking')
                print ('DF_stochastic_SELL[ema_open_mid][-2] / DF_stochastic_SELL[ema_open_mid][-3]_____[condition] Less than {0} / [value] {1}'.format(ratio_sell_ema_mid_chg_state, (DF_stochastic_SELL['ema_open_mid'][-2] / DF_stochastic_SELL['ema_open_mid'][-3])))
                print ('DF_stochastic_SELL[ema_open_mid][-1] / DF_stochastic_SELL[ema_open_mid][-2]_____[condition] Less than {0} / [value] {1}'.format(ratio_sell_ema_mid_chg_state, (DF_stochastic_SELL['ema_open_mid'][-1] / DF_stochastic_SELL['ema_open_mid'][-2])))
                
                if ((DF_stochastic_SELL['ema_open_mid'][-2] / DF_stochastic_SELL['ema_open_mid'][-3]) < ratio_sell_ema_mid_chg_state) and ((DF_stochastic_SELL['ema_open_mid'][-1] / DF_stochastic_SELL['ema_open_mid'][-2]) < ratio_sell_ema_mid_chg_state) :
                    transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
                    time.sleep(5)
                    print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                    print ('sell_transaction_result_BY_ state_change _SELLING :', transaction_sell)
                    
                    bought_state = 0
                    
                    time.sleep(5)
                    
        
        # 하락시 강제 매도 영역
        if bought_state == 1 :   # 매수가 되어 있는 상태라면
            print ('\nFORCED SELL condition checking')
            
            if (pyupbit.get_current_price(coin_inv) / currrent_price) < (1 - sell_force_loss) :   # 강제 매도 가격 이하로 현재가격이 하락하게 되면
                transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
                time.sleep(5)
                print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                print ('sell_transaction_result_BY_ FORCED _SELLING :', transaction_sell)
                bought_state = 0
                time.sleep(5)
                
        time.sleep(5)
        
    except :
        print ('Error has occured!!!')


# In[ ]:


# For Test 매수/매도 로직
'''
currrent_price = 1

while True:
    
    now = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
    print ('bought_state : {0}   / now : {1}'.format(bought_state, now))
    
    if (now.minute % time_unit == 0) & (55 < (now.second % 60) <= 59) :   # N시:00:55초 ~ N시:00:59초 사이 시각이면
        balances = upbit.get_balances()
        print ('current_aseet_status\n', balances)
        
        if bought_state == 0 :   # 매수가 없는 상태라면
            DF_invest_check = pyupbit.get_ohlcv(coin_inv, count = candle_count, interval = candle_adapt)
            
            print('DF_test_ma :\n', DF_test_ma)
            
            DF_test_stochastic = DF_stochastic (DF_test_ma)
            print('DF_test_stochastic :\n', DF_test_stochastic)
            
            
            print ('\n[BUY condition check]')
            print ('DF_test_stochastic[ema_o_l_consecutive_rise][-(ema_long_duration + 1) : -1].sum()_____[condition] greater {0} / [value] {1}'.format(5, DF_test_stochastic['ema_o_l_consecutive_rise'][-(ema_long_duration + 1) : -1].sum()))
            print ('DF_test_stochastic[ema_o_s_consecutive_rise][-(ma_short_under_duration + 1) : -1].sum()_____[condition] greater/equal than {0} / [value] {1}'.format((ma_short_under_duration - 1), DF_test_stochastic['ema_o_s_consecutive_rise'][-(ma_short_under_duration + 1) : -1].sum()))
            print ('DF_test_stochastic[ema_open_long][-1] / DF_test_stochastic[ema_open_long][-2])_____[condition] greater than {0} / [value] {1}'.format(ratio_ema_long, (DF_test_stochastic['ema_open_long'][-1] / DF_test_stochastic['ema_open_long'][-2])))
            print ('DF_test_stochastic[ratio_vol_to_aver][-2]____[condition] greater than {0} / [value] {1}'.format(buy_cri_vol_times, DF_test_stochastic['ratio_vol_to_aver'][-2]))
            print ('OR__DF_test_stochastic[ratio_vol_to_aver][-1]_____[condition] greater than {0} / [value] {1}'.format(buy_cri_vol_times, DF_test_stochastic['ratio_vol_to_aver'][-1]))
            print ('DF_test_stochastic[ema_open_short][-1] / DF_test_stochastic[ema_open_long][-1]_____[condition] greater than {0} / [value] {1}'.format(ratio_ema_o_short_long[0], (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1])))
            print ('DF_test_stochastic[ema_open_short][-1] / DF_test_stochastic[ema_open_long][-1]_____[condition] Less than {0} / [value] {1}'.format(ratio_ema_o_short_long[1], (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1])))
            
            # 매수 영역
            print ('$$$$$ [{0}] buying_transaction is cheking $$$$$'.format(coin_inv))
            if (DF_test_stochastic['ema_o_l_consecutive_rise'][-(ema_long_duration + 1) : -1].sum() > 0) and \
            (DF_test_stochastic['ema_o_s_consecutive_rise'][-(ma_short_under_duration + 1) : -1].sum() >= 0) and \
            ((DF_test_stochastic['ema_open_long'][-1] / DF_test_stochastic['ema_open_long'][-2]) > ratio_ema_long) and \
            ((DF_test_stochastic['ratio_vol_to_aver'][-2] > buy_cri_vol_times) or (DF_test_stochastic['ratio_vol_to_aver'][-1] > buy_cri_vol_times)) and \
            (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1] > ratio_ema_o_short_long[0]) and (DF_test_stochastic['ema_open_short'][-1] / DF_test_stochastic['ema_open_long'][-1] < ratio_ema_o_short_long[1]) :            
            
                print ('$$$$$ [{0}] buying_transaction is coducting $$$$$'.format(coin_inv))
                    
                investable_budget = get_balance(check_currency) * invest_ratio
                buying_volume = (investable_budget * (1 - transaction_fee_ratio)) / pyupbit.get_current_price(coin_inv)
                currrent_price = pyupbit.get_current_price(coin_inv)
                print ('\ncurrent_price : ', currrent_price)
                buyable_price = currrent_price + (buy_price_up_unit * unit_value)
                print ('investable_budget : {0} / currrent_price : {1} / buying_volume : {2}'.format(investable_budget, currrent_price, buying_volume))
                
                #transaction_buy = upbit.buy_market_order(coin_inv, investable_budget)   # 시장가로 매수
                transaction_buy1 = upbit.buy_limit_order(coin_inv, buyable_price, buying_volume)   # 지정가로 매수
                time.sleep(10)
                print ('buy_1ST_transaction_result :', transaction_buy1)
                print ('time : {0}  /  buying_target_volume : {1}  /  bought_volume_until_now : {2}'.format((datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))), buying_volume, get_balance(coin_inv[4:])))
                
                if get_balance(coin_inv[4:]) <= (0.95 * buying_volume) :
                    now2 = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
                    while (0 <= (now2.minute % time_unit) <= 10) :   # 0분에서 10분 사이면
                        if (pyupbit.get_current_price(coin_inv) / currrent_price) < (1 - sell_force_loss) :   # 강제 매도 가격 이하로 현재가격이 하락하게 되면
                            transaction_buy_cancel1 = upbit.cancel_order(transaction_buy1['uuid'])   # 미처 못산 매수물량 취소
                            transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
                            time.sleep(5)
                            bought_state = 0
                            print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                            print ('sell_transaction_result_BY_FORCED_SELLING_in the WHILE_loop :', transaction_sell)
                            
                            time.sleep(1)
                            now2 = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
                    
                    transaction_buy_cancel1 = upbit.cancel_order(transaction_buy1['uuid'])
                    
                                  
                                
                   
    # 매수 상태 점검
    if get_balance(coin_inv[4:]) > 0 :
        bought_state = 1
        print ('bought_state_in mid check : {0}'.format(bought_state))
    else : 
        bought_state = 0
        print ('bought_state_in mid check : {0}'.format(bought_state))
 
                    
    #매도 영역
    now3 = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
    if (now3.minute % time_unit == 0) & (55 < (now.second % 60) <= 59) :   # N시:00:55초 ~ N시:00:59초 사이 시각이면
        balances2 = upbit.get_balances()
        print ('current_aseet_status\n', balances2)
        
        if bought_state == 1 :   # 매수가 되어 있는 상태라면
            print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
            print ('\n bought_state : {0}  [[[[[[[[[[[[ coin___{1} selling condition checking]]]]]]]]]] :'.format(bought_state, coin_inv))
            DF_invest_check_SELL = pyupbit.get_ohlcv(coin_inv, count = candle_count, interval = candle_adapt)
            DF_mov_avg_check_SELL = DF_mv (DF_invest_check_SELL)
            DF_stochastic_SELL = DF_stochastic (DF_mov_avg_check_SELL)
            
            print ('DF_stochastic_SELL\n', DF_stochastic_SELL)
            
            
            # 권장되는 매도 영역 판단
            print ('\nNORMAL SELL condition checking')
            print('DF_stochastic_SELL[open][-1] / currrent_price)_____[condition] greater than {0} / [value] {1}'.format((1 + sellable_profit), (DF_stochastic_SELL['open'][-1] / currrent_price)))
            print('DF_stochastic_SELL.iloc[-4 : -3][slow_sto_k_on].sum()_____[condition] greater/equal than {0} / [value] {1}'.format(slow_sto_k_count, DF_stochastic_SELL.iloc[-4 : -3]['slow_sto_k_on'].sum()))
            print('DF_stochastic_SELL.loc[DF_stochastic_SELL.iloc[-5 : -2][slow_sto_k].idxmax()][slow_sto_k]_____[condition] greater than {0} / [value] {1}'.format(slow_sto_k_cri, DF_stochastic_SELL.loc[DF_stochastic_SELL.iloc[-5 : -2]['slow_sto_k'].idxmax()]['slow_sto_k']))
            print('DF_stochastic_SELL[slow_sto_k][-1]_____[condition] Less than {0} / [value] {1}'.format((slow_sto_k_cri - 0.09), DF_stochastic_SELL['slow_sto_k'][-1]))
            print('DF_stochastic_SELL[ema_open_long][-1] / DF_stochastic_SELL[ema_open_long][-2]_____[condition] Less than {0} / [value] {1}'.format(sell_ma_long_ratio, (DF_stochastic_SELL['ema_open_long'][-1] / DF_stochastic_SELL['ema_open_long'][-2])))   
                        
            if ((DF_stochastic_SELL['open'][-1] / currrent_price) > (1 + sellable_profit)) and \
            ((DF_stochastic_SELL.iloc[-4 : -3]['slow_sto_k_on'].sum()) >= 0) and \
            (DF_stochastic_SELL.loc[DF_stochastic_SELL.iloc[-5 : -2]['slow_sto_k'].idxmax()]['slow_sto_k'] > (slow_sto_k_cri - 0.5)) and (DF_stochastic_SELL['slow_sto_k'][-1] < (slow_sto_k_cri - 0.09)) and \
            ((DF_stochastic_SELL['ema_open_long'][-1] / DF_stochastic_SELL['ema_open_long'][-2]) < sell_ma_long_ratio) :
                
                transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
                time.sleep(5)
                print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                print ('sell_transaction_result_BY_ NORMAL _SELLING :', transaction_sell)
                
                bought_state = 0
                
                time.sleep(5)
            
            
            # 추세 변화에 따른 매도 영역 판단
            print ('\nSTATE_CHANGE SELL condition checking')
            print ('DF_stochastic_SELL[ema_open_long][-2] / DF_stochastic_SELL[ema_open_long][-3]_____[condition] Less than {0} / [value] {1}'.format(ratio_sell_ema_long_chg_state, (DF_stochastic_SELL['ema_open_long'][-2] / DF_stochastic_SELL['ema_open_long'][-3])))
            print ('DF_stochastic_SELL[ema_open_long][-1] / DF_stochastic_SELL[ema_open_long][-2]_____[condition] Less than {0} / [value] {1}'.format(ratio_sell_ema_long_chg_state, (DF_stochastic_SELL['ema_open_long'][-1] / DF_stochastic_SELL['ema_open_long'][-2])))
            
            if ((DF_stochastic_SELL['ema_open_long'][-2] / DF_stochastic_SELL['ema_open_long'][-3]) < ratio_sell_ema_long_chg_state) and ((DF_stochastic_SELL['ema_open_long'][-1] / DF_stochastic_SELL['ema_open_long'][-2]) < ratio_sell_ema_long_chg_state) :
                
                transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
                time.sleep(5)
                print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
                print ('sell_transaction_result_BY_ state_change _SELLING :', transaction_sell)
                
                bought_state = 0
                
                time.sleep(5)
        
        
    # 하락시 강제 매도 영역
    if bought_state == 1 :   # 매수가 되어 있는 상태라면
        
        print ('\nFORCED SELL condition checking')
            
        if (pyupbit.get_current_price(coin_inv) / currrent_price) < (1 - sell_force_loss) :   # 강제 매도 가격 이하로 현재가격이 하락하게 되면
            
            transaction_sell = upbit.sell_market_order(coin_inv, get_balance(coin_inv[4:]))   # 시장가에 매도
            time.sleep(5)
            print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
            print ('sell_transaction_result_BY_ FORCED _SELLING :', transaction_sell)
            bought_state = 0
            time.sleep(5)
        
    time.sleep(1)
'''


# In[ ]:


bought_price


# In[ ]:


pyupbit.get_current_price('KRW-NEO')


# In[ ]:


get_balance ('KRW')


# In[ ]:


upbit.get_balances()[coin_inv]['avg_buy_price']


# In[ ]:


upbit.get_balances()[coin_inv[4:]]


# In[ ]:


upbit.get_balances()


# In[ ]:


coin_inv


# In[ ]:


upbit.get_balances()[1]['avg_buy_price']


# In[ ]:


upbit.get_balances()['currency' == 'BTC']['avg_buy_price']


# In[ ]:


upbit.get_balances()[0]['currency']


# In[ ]:




