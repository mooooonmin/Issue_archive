import streamlit as st

user_name = st.sidebar.text_input('이름을 입력해 주세요:')

user_age = st.sidebar.slider('나이:', 0, 100, 25)

submit_button = st.sidebar.button('제출')

if submit_button:
    st.write(f'안녕하세요 {user_name}님!')
    st.write(f'당신의 나이는 {user_age} 입니다.')
    
col1, col2 = st.columns(2)

with col1:
    st.header('첫 번째 컬럼')
    st.image('image1.jpg')
    
with col2:
    st.header('두 번째 컬럼')
    st.image('image2.jpg')
    
tab1, tab2 = st.tabs(['탭 1', '탭 2'])

with tab1:
    st.header('이것은 첫 번째 탭')
    st.write('여기에는 첫 번째 탭의 컨텐츠가 표시됩니다.')
    
with tab2:
    st.header('이것은 두 번째 탭')
    st.write('여기에는 두 번째 탭의 컨텐츠가 표시됩니다.')