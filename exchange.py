# -----------------------------------------------------------------------------
# 여러가지 방법의 데이터 시각화 표현해볼려고 시도함.
# -----------------------------------------------------------------------------

import streamlit as st          #streamlit용
import pandas as pd             #그래프 사용용도
import datetime                 #그래프 사용용도
import time                     #그래프 사용용도
import matplotlib.pyplot as plt #그래프 표현을위해 사용
import matplotlib               #그래프 표현을위해 사용
from io import BytesIO          #IO 모듈의 바이트 IO 작업
import matplotlib.pyplot as plt #그래프 표현을위해 사용
import matplotlib               #그래프 표현을위해 사용
import plotly.express as px     #그래프 표현을위해 사용
import yfinance as yf           #주가 불러오기위해 사용

from tracemalloc import start   #파이썬이 할당한 메모리 블록을 추적
from matplotlib import ticker   #그래프 축 눈금 간격 설정

 
# -----------------------------------------------------------------------------
# 설정한 주식 값 출력해주는 함수
# 주식,가상화폐 코드, 소스에서 입력후 출력
# 코드명으로 종목 추가 해주어야함
# -----------------------------------------------------------------------------


st.subheader('주식,가상화폐 변동율') #sidebar표시
# 종믁은 시장 코드로 입력해주어야함.
# 추가는 간단하게 '이름명':'코드'
tickers ={
  'Samsung Electronics':'005930.KS',
  'SK hynix':'000660.KS',
  'TESLA' :'TSLA',
  'BTC-USD':'BTC-USD'
}

rt = dict(map(reversed,tickers.items()))
#종목받아옴
dd = st.multiselect('select',tickers.keys())
#종목 여러개선택
start = st.date_input('Start', value=pd.to_datetime('2022-11-01'))
#시작기간설정
end = st.date_input('End',value=pd.to_datetime('today'))
#종료기간설정

#데이터 프레임
if len(dd) > 0:
  for i in dd:
    df = yf.download(tickers[i],start,end)['Adj Close']
    #종목닫기
    st.title(rt[tickers[i]])
    #종목명
    st.line_chart(df)
    #종목차트


 
 
 
 
 
 
# -----------------------------------------------------------------------------
# 날짜별 환율 데이터를 반환하는 함수
# - 입력 인수: currency_code(통화코드), last_page_num(페이지 수)
# - 반환: 환율 데이터
# -----------------------------------------------------------------------------
def get_exchange_rate_data(currency_code, last_page_num):
    base_url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn"
    df = pd.DataFrame()
    
    for page_num in range(1, last_page_num+1):
        url = f"{base_url}?marketindexCd={currency_code}&page={page_num}"
        dfs = pd.read_html(url, header=1)
        
        # 통화 코드가 잘못 지정됐거나 마지막 페이지의 경우 for 문을 빠져나옴
        if dfs[0].empty: 
            if (page_num==1):
                print(f"통화 코드({currency_code})가 잘못 지정됐습니다.")    
            else:
                print(f"{page_num}가 마지막 페이지입니다.")    
            break
            
        # page별로 가져온 DataFrame 데이터 연결
        df = pd.concat([df, dfs[0]], ignore_index=True) 
        time.sleep(0.1) # 0.1초간 멈춤        
        
    return df
# -----------------------------------------------------------------------------
  
st.subheader("환율 정보를 가져오는 웹 앱")

# 사이드바의 폭을 조절. {width:250px;} 으로 지정하면 폭을 250픽셀로 지정
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{width:250px;}
    </style>
    """, unsafe_allow_html=True
)


currency_name_symbols = {"미국 달러":"USD", "유럽연합 유로":"EUR", 
                         "일본 엔(100)":"JPY", "중국 위안":"CNY"}
currency_name = st.sidebar.selectbox('통화 선택', currency_name_symbols.keys())

clicked = st.sidebar.button("환율 데이터 가져오기")

if(clicked==True):

    currency_symbol = currency_name_symbols[currency_name] # 환율 심볼 선택
    currency_code = f"FX_{currency_symbol}KRW"

    last_page_num = 20 # 네이버 금융에서 가져올 최대 페이지 번호 지정 
    
    # 지정한 환율 코드를 이용해 환율 데이터 가져오기
    df_exchange_rate = get_exchange_rate_data(currency_code, last_page_num)
    
    # 원하는 열만 선택
    df_exchange_rate = df_exchange_rate[['날짜', '매매기준율','사실 때',
                                         '파실 때', '보내실 때', '받으실 때']]
    
    # 최신 데이터와 과거 데이터의 순서를 바꿔 df_exchange_rate2에 할당
    df_exchange_rate2 = df_exchange_rate[::-1].reset_index(drop=True)

    # df_exchange_rate2의 index를 날짜 열의 데이터로 변경
    df_exchange_rate2 = df_exchange_rate2.set_index('날짜') 

    # df_exchange_rate2의 index를 datetime 형식으로 변환
    df_exchange_rate2.index = pd.to_datetime(df_exchange_rate2.index, 
                                             format='%Y-%m-%d') 

    # 1) 환율 데이터 표시
    st.subheader(f"[{currency_name}] 환율 데이터")
    st.dataframe(df_exchange_rate.head())  # 환율 데이터 표시(앞의 일부만 표시)
    
    # 1.1) 환율 변동폭 표시
    st.subheader(f"환율 변동폭")
    
    # 2) 차트 그리기
    # matplotlib을 이용한 그래프에 한글을 표시하기 위한 설정
    #matplotlib.rcParams["font.family"] ="Malgun Gothic"
    #matplotlib.rcParams["axes.unicode_minus"] =False
    
   
 # 선 그래프 그리기 (df_exchange_rate2 이용)
    ax = df_exchange_rate2['매매기준율'].plot(grid=True, figsize=(15, 5))
    plt.xticks(fontsize=15)             # X축 눈금값의 폰트 크기 지정
    plt.yticks(fontsize=15)             # Y축 눈금값의 폰트 크기 지정    
    fig = ax.get_figure()               # fig 객체 가져오기    
    st.pyplot(fig)     
    
    
    
    
    
