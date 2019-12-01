from _setting import setting
import pandas as pd
import time
from enum import Enum
import pickle



# Enum Class 상속 받을 경우 생성자 사용 불가능
# 데이터팩 파싱을 위한 정보
base_dir = str(setting['base_dir'])

def dropComma(df):
    return df.apply(lambda row: row.astype('str').str.replace(',','')).astype('float')

    
class PackInfo_DataGuide():
    class PRP(Enum): # Price Related Pack
        directory = setting['data_dir']+'/price_pack.pkl'
        price_open = '수정시가(원)'
        price_high = '수정고가(원)'
        price_low = '수정저가(원)'
        price = '수정주가(원)'
        return_1w = '수익률 (1주)(%)'
        return_1m = '수익률 (1개월)(%)'
        return_3m = '수익률 (3개월)(%)'
        return_6m = '수익률 (6개월)(%)'
        return_12m = '수익률 (12개월)(%)'
        eturn_ytd = '수익률 (YTD)(%)'
        vol_5d = '변동성 (5일)'
        vol_20d = '변동성 (20일)'
        vol_60d = '변동성 (60일)'
        vol_120d = '변동성 (120일)'
        vold_52w = '변동성 (52주)'
        
    class MP(Enum): # Market Pack
        directory = setting['data_dir']+'/market_pack.pkl'
        kospi_open = '시가지수(포인트)'
        kodaq_open = '시가지수(포인트)'
        kospi_high = '고가지수(포인트)'
        kodaq_high = '고가지수(포인트)'
        kospi_low = '저가지수(포인트)'
        kodaq_low = '저가지수(포인트)'
        kospi = '종가지수(포인트)'
        kodaq = '종가지수(포인트)'
        kospi_trading_volume = '거래대금(원)' 
        kodaq_trading_volume = '거래대금(원)'   
        # market_open = None
        
    class SDP(Enum): # Supply and Demand Pack
        directory = setting['data_dir']+'/liquidity_pack.pkl'
        inst_sell = '매도대금(기관계)(만원)'
        inst_buy = '매수대금(기관계)(만원)'
        inst = '순매수대금(기관계)(만원)'
        foreign_sell = '매도대금(외국인계)(만원)'
        foreign_buy = '매수대금(외국인계)(만원)'
        foreign = '순매수대금(외국인계)(만원)'
        individual_sell = '매도대금(개인)(만원)'
        individual_buy = '매수대금(개인)(만원)'
        individual = '순매수대금(개인)(만원)'
            
    class QP(Enum): # Quality Related Pack
        pass
    
    def __init__(self):
        pass
    
    
    
# 데이터팩 파싱 
class DataGuideData(PackInfo_DataGuide):
    # PackInfo = PackInfo_DataGuide() # 클래스 선언과 함께 생성
    market_open = None
    
    def __init__(self):
        # Pack Data - PRP, MP, SDP, QP
        # self.PackInfo = PackInfo_DataGuide() # Pack 구성 정보를 담을 Pack Information Set
        self.Pack = PackInfo_DataGuide() # Pack 구성 정보를 바탕으로 개별 데이터가 저장될 Data Set
        self.PRD = None # Parsing 대상이 되는 전체 Raw Data - Price Related
        self.MD = None # Parsing 대상이 되는 전체 Raw Data - Market
        self.SDD = None # Parsing 대상이 되는 전체 Raw Data - Supply & Demand 
        self.QD = None # Parsing 대상이 되는 전체 Raw Data - Quality
        self.monthly_return = None
        self.monthly_return_ie = None

        print('Reading Begin...')
        
        self._read() # Read data 
        self._unpack() # Unpack files
        
        self.Pack.MP.mkt_open = (self.Pack.MP.kospi.value).dropna().index
        # self._monthlyreturn()
        # self._monthlyreturn() # Calculate Monthly Return
        
    def _read(self):
        print('File loading... ', end='')
        start = time.time()
        self.PRD = pd.read_pickle(self.Pack.PRP.directory.value)
        self.MD = pd.read_pickle(self.Pack.MP.directory.value)
        # self.SDD = dropComma(pd.read_pickle(self.Pack.SDP.directory.value))
        # self.QD = pd.read_pickle(self.PackInfo.QP.directory.value)
        print('complete!!', time.time()-start, 'sec')
              
    def _unpack(self):
        print('File unpacking... ', end='')
        start = time.time()
        
        # PRICE RELATED DATA UNPACK
        for i, component in enumerate(self.Pack.PRP):
            if component.name == 'directory': continue
            component._value_ = self.PRD.xs(tuple(self.Pack.PRP)[i].value, level=1, axis=1)
        '''
        # SUPPLY&DEMAND UNPACK
        for i, component in enumerate(self.Pack.SDP):
            if component.name == 'directory': continue
            component._value_ = self.SDD.xs(tuple(self.Pack.SDP)[i].value, level=1, axis=1)
        '''
        # MARKET DATA UNPACK
        for i, component in enumerate(self.Pack.MP):
            if component.name == 'directory': continue
            mkt = '코스피' if component.name[:5] == 'kospi' else '코스닥'
            component._value_ = (self.MD[mkt])[tuple(self.Pack.MP)[i].value]
        self.market_open = (self.Pack.MP.kospi.value.dropna()).index
        
        print('complete', time.time()-start, 'sec')
        
    def _monthlyreturn(self):
        monthlyPrice_init = self.Pack.PRP.price.value.resample('M').first()
        monthlyPrice_end = self.Pack.PRP.price.value.resample('M').last()
        
        self.monthly_return = (((monthlyPrice_init).astype('float')/(monthlyPrice_init.shift(1)).astype('float').shift(-1))-1)
        # self.monthly_return_ie = (monthlyPrice_end/monthlyPrice_init)-1 # 월초 매수 월말 매도
        
    # Data integrity check    
    def _updateData(self):
        pass
    
print('??????')
_DT = DataGuideData()
pack = _DT.Pack