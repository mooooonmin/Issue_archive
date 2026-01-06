import streamlit as st

st.header('이것은 헤더입니다')

st.markdown('1. 리스트 아이템 1\n2. 리스트 아이템 2')
st.markdown('[홈페이지](url)')
st.markdown(
    '''
    This is main text.
    This is how to change the color of text :red[Red,] :blue[Blue,] :green[Green.]
    This is **Bold** and *Italic* text
    '''
)

st.write('이것은 write 함수를 사용한 텍스트입니다.')

import pandas as pd
df = pd.DataFrame({
    'column 1':[1, 2, 3],
    'column 2':[4, 5, 6]
})

st.write(df)

email = st.text_input('이메일 주소를 입력하세요', 'example@example.com')
st.write(email)

value = st.slider('값을 선택하세요', min_value=0, max_value=100, value=50)
st.write('선택한 값:', value)

range_values = st.slider(
    '범위를 선택하세요',
    min_value=0, max_value=100,
    value=(25, 75),
    step=5
)
st.write('선택한 범위:', range_values)

import datetime

start_date, end_date = st.slider(
    '날짜 범위를 선택하요',
    min_value=datetime.date(2020,1,1),
    max_value=datetime.date.today(),
    value=(datetime.date(2020,1,1), datetime.date.today()),
    format='YYYY-MM-DD'
)

st.write('선택한 시작 날짜:', start_date)
st.write('선택한 종료 날짜:', end_date)

if st.button('클릭하세요'):
    st.write('버튼이 클릭되었습니다.')
    
else:
    st.write('버튼을 클릭해 주세요.')
agree = st.checkbox('이용 약관에 동의합니다.')

if agree:
    st.write('약관에 동의하셨습니다.')
else:
    st.write('약관 동의가 필요합니다.')
    
options = ['옵션 1','옵션 2', '옵션 3']

selected_option = st.selectbox('옵션을 선택하세요', options)
st.write('선택한 옵션:', selected_option)

country = st.selectbox('국가를 선택하세요:', ['한국','미국','일본'])
if country == '한국':
    city = st.selectbox('도시를 선택하세요:', ['서울','부산','대구'])
elif country == '미국':
    city = st.selectbox('도시를 선택하세요:', ['뉴욕','샌프란시스코','시카고'])
elif country == '일본':
    city = st.selectbox('도시를 선택하세요:', ['도쿄','오사카','교토'])
    
st.write('선택한 도시:', city)

from PIL import Image

uploaded_file = st.file_uploader('이미지 파일을 업로드해주세요', type=['jpg','png'])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 이미지', use_column_width=True)
    
# matplotlib
import matplotlib.pyplot as plt
import numpy as np
# 데이터 생성
x = np.linspace(0, 10, 30)
y = np.sin(x)
# Matplotlib pyplot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y)
# Streamlit 애플리케이션에 그래프 표시
st.pyplot(fig)
# Plotly chart
import plotly.express as px
df = px.data.iris()
# Plotly Express를 사용한 그래프 생성
fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')
# Streamlit 애플리케이션에 그래프 표시
st.plotly_chart(fig)