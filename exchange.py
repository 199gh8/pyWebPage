# 환율 데이터를 가져오는 웹 앱

import streamlit as st
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
import plotly.express as px

import yfinance as yf

    
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
  
st.title("환율 정보를 가져오는 웹 앱")

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
    
    
    
    
    
 #----------------------------------------
# 한국 주식 종목 코드를 가져오는 함수
#----------------------------------------
def get_stock_info(maket_type=None):
    # 한국거래소(KRX)에서 전체 상장법인 목록 가져오기
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"
    if maket_type == 'kospi':
        marketType = "stockMkt"  # 주식 종목이 코스피인 경우
    elif maket_type == 'kosdaq':
        marketType = "kosdaqMkt" # 주식 종목이 코스닥인 경우
    elif maket_type == None:
        marketType = ""
    url = "{0}?method={1}&marketType={2}".format(base_url, method, marketType)

    df = pd.read_html(url, header=0)[0]
    
    # 종목코드 열을 6자리 숫자로 표시된 문자열로 변환
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}") 
    
    # 회사명과 종목코드 열 데이터만 남김
    df = df[['회사명','종목코드']]
    
    return df
#----------------------------------------------------
# yfinance에 이용할 Ticker 심볼을 반환하는 함수
#----------------------------------------------------
def get_ticker_symbol(company_name, maket_type):
    df = get_stock_info(maket_type)
    code = df[df['회사명']==company_name]['종목코드'].values
    code = code[0]
    
    if maket_type == 'kospi':
        ticker_symbol = code +".KS" # 코스피 주식의 심볼
    elif maket_type == 'kosdaq':
        ticker_symbol = code +".KQ" # 코스닥 주식의 심볼
    
    return ticker_symbol
#---------------------------------------------------------

st.title("주식 정보를 가져오는 웹 앱")

# 사이드바의 폭을 조절. {width:250px;} 으로 지정하면 폭을 250픽셀로 지정
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{width:250px;}
    </style>
    """, unsafe_allow_html=True
)

st.sidebar.header("회사 이름과 기간 입력")

# 주식 종목 이름을 입력 받아서 지정
stock_name = st.sidebar.text_input('회사 이름', value="NAVER")  
# 기간을 입력 받아서 지정
date_range = st.sidebar.date_input("시작일과 종료일",           
                 [datetime.date(2019, 1, 1), datetime.date(2021, 12, 31)])

clicked = st.sidebar.button("주가 데이터 가져오기")

if(clicked == True):
    # 주식 종목과 종류 지정해 ticker 심볼 획득
    ticker_symbol = get_ticker_symbol(stock_name, "kospi") 
    ticker_data = yf.Ticker(ticker_symbol)
    
    start_p = date_range[0]                            # 시작일
    end_p = date_range[1] + datetime.timedelta(days=1) # 종료일 (지정된 날짜에 하루를 더함)
    # 시작일과 종료일 지정해 주가 데이터 가져오기
    df = ticker_data.history(start=start_p, end=end_p) 
    
    # 1) 주식 데이터 표시
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.head())  # 주가 데이터 표시(앞의 일부만 표시)
    
    # 2) 차트 그리기    
    
   
    
    # 선 그래프 그리기
    ax = df['Close'].plot(grid=True, figsize=(15, 5))
    plt.xticks(fontsize=15)                        # X축 눈금값의 폰트 크기 지정
    plt.yticks(fontsize=15)                        # Y축 눈금값의 폰트 크기 지정    
    fig = ax.get_figure()                          # fig 객체 가져오기    
    st.pyplot(fig)                                 # 스트림릿 웹 앱에 그래프 그리기
