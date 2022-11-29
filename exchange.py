# -----------------------------------------------------------------------------
# 주식, 가상화폐 기록 확인 후 바로 환율 까지 볼수있는 페이지
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

#sidebar표시
st.subheader('주식,가상화폐 변동율') 
# 종믁은 시장 코드로 입력해주어야함.
# 추가는 간단하게 '이름명':'코드'
tickers ={
  'Samsung Electronics':'005930.KS',
  'SK hynix':'000660.KS',
  'TESLA' :'TSLA',
  'BTC-USD' :'BTC-USD'
}

#종목받아옴
rt = dict(map(reversed,tickers.items()))
#종목 여러개선택
dd = st.multiselect('select',tickers.keys())
#시작기간설정
start = st.date_input('Start', value=pd.to_datetime('2022-11-01'))
#종료기간설정
end = st.date_input('End',value=pd.to_datetime('today'))

#데이터 프레임
if len(dd) > 0:
  for i in dd:
    #종목닫기
    df = yf.download(tickers[i],start,end)['Adj Close']
    #종목명
    st.title(rt[tickers[i]])
    #종목차트
    st.line_chart(df)
    

 
# -----------------------------------------------------------------------------
# 환율데이터 가져오는 용도.
# -----------------------------------------------------------------------------

#통화 데이터 가져옴 최종 페이지 까지.
def get_exchange_rate_data(currency_code, last_page_num):
    #위의 코드와 다르게 네이버증권것을 가져옴.
    base_url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn"
    df = pd.DataFrame()
    
    #최종 페이지까지  가져옴
    for page_num in range(1, last_page_num+1):
        url = f"{base_url}?marketindexCd={currency_code}&page={page_num}"
        dfs = pd.read_html(url, header=1)
        
        # 코드지정 오류 or 마지막일시 페이지 빠져나옴.
        if dfs[0].empty: 
            if (page_num==1):
                print(f"({currency_code})error.")    
            else:
                print(f"{page_num}is last page.")    
            break
            
        # 페이지별 dataframe 연결용.
        df = pd.concat([df, dfs[0]], ignore_index=True) 
        
    return df
# -----------------------------------------------------------------------------
  
st.subheader("환율정보")

#사이드바 표시용.
st.markdown(
    """
    <style>
    #사이드바 넓이 지정
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{width:250px;}
    </style>
    """, unsafe_allow_html=True
)

#환율 카테고리 지정
currency_name_symbols = {"미국 달러":"USD", "유럽연합 유로":"EUR", 
                         "일본 엔(100)":"JPY", "중국 위안":"CNY"}

#통화 선택 유도용 표시
currency_name = st.sidebar.selectbox('통화 선택', currency_name_symbols.keys())

#클릭시, 데이터 가져오는 버튼
clicked = st.sidebar.button("환율 데이터 가져오기")

#클릭시 데이터 가져오도록 만드는 함수.
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
    matplotlib.rcParams['font.family'] = 'Malgun Gothic'
    matplotlib.rcParams['axes.unicode_minus'] = False
    
   
 # 선 그래프 그리기 (df_exchange_rate2 이용)
    ax = df_exchange_rate2['매매기준율'].plot(grid=True, figsize=(15, 5))
    plt.xticks(fontsize=15)             # X축 눈금값의 폰트 크기 지정
    plt.yticks(fontsize=15)             # Y축 눈금값의 폰트 크기 지정    
    fig = ax.get_figure()               # fig 객체 가져오기    
    st.pyplot(fig)     
    
    
    
    
    
