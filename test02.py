import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from konlpy.tag import Kkma
from konlpy.tag import Okt
from wordcloud import WordCloud
import nltk
import streamlit as st

def main():
    st.header('최대 7일 이내의 뉴스 키워드를 찾을 수 있습니다')
    date = st.text_input('키워드를 보고싶은 일자를 입력해주세요. ex)20210324')
    news_url = 'https://news.naver.com/main/ranking/popularDay.nhn?date={}'.format(date)

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
    req = requests.get(news_url, headers = headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    news_titles = soup.select('.rankingnews_box > ul > li > div > a')

    crowled_title = []
    for i in range(len(news_titles)):
        crowled_title.append(news_titles[i].text)
    # st.write(crowled_title)


    title = "".join(crowled_title)
    filtered_title = title.replace('.', ' ').replace('"',' ').replace(',',' ').replace("'"," ").replace('·', ' ').replace('=',' ').replace('\n',' ')

    tw = Okt()
    tokens_ko = tw.nouns(filtered_title)

    ko = nltk.Text(tokens_ko, name='기사 내 명사')

    new_ko=[]
    for word in ko:
        if len(word) > 1 and word != '단독' and  word != ' ':
            new_ko.append(word)

    ko = nltk.Text(new_ko, name = '기사 내 명사 두 번째')

    data = ko.vocab().most_common(150)

    data = dict(data)

    font = 'C:\Windows\Fonts\HMFMPYUN.ttf' #이 친구는 코랩과는 다르다 ㅋㅋㅋㅋ
    wc = WordCloud(font_path=font,\
            background_color="white", \
            width=1000, \
            height=1000, \
            max_words=100, \
            max_font_size=300)
    wc = wc.generate_from_frequencies(data)



    fig = plt.figure()  # 스트림릿에서 plot그리기
    plt.title(date +' '+ 'KeyWords')
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()
    st.pyplot(fig)





if __name__ == '__main__':
    main()
