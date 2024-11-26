import streamlit as st

# 앱 제목
st.title('Streamlit 기본 예제')

# 텍스트 입력 받기
name = st.text_input('이름을 입력하세요:', '')

# 버튼을 눌렀을 때의 반응
if st.button('이름 출력'):
    st.write(f'안녕하세요, {name}님!')
else:
    st.write('이름을 입력하고 버튼을 눌러주세요.')

# 슬라이더 예시
age = st.slider('나이를 선택하세요:', 1, 100, 25)
st.write(f'당신의 나이는 {age}살 입니다.')

# 데이터프레임 예시
import pandas as pd

# 간단한 데이터프레임 생성
data = {'이름': ['홍길동', '김철수', '이영희'],
        '나이': [25, 30, 22]}
df = pd.DataFrame(data)

st.write('간단한 데이터프레임:')
st.dataframe(df)

# 그래프 예시
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title('Sine Wave')

st.pyplot(fig)
