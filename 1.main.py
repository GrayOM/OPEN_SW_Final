import streamlit as st
import random
import string
import base64
import pandas as pd
import kagglehub
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
username = os.getenv("API_USERNAME")

# 비밀번호 생성 함수
def generate_password(length, include_upper, include_lower, include_digits, include_specials, exclude_ambiguous, excluded_specials):
    # 사용자가 선택한 문자 집합을 기반으로 구성
    characters = ''
    if include_upper:
        characters += string.ascii_uppercase
    if include_lower:
        characters += string.ascii_lowercase
    if include_digits:
        characters += string.digits
    if include_specials:
        characters += string.punctuation

    # 모호한 문자 제거
    if exclude_ambiguous:
        ambiguous_chars = 'O0I1|'
        characters = ''.join([c for c in characters if c not in ambiguous_chars])

    # 특수문자 제외 처리
    if excluded_specials:
        characters = ''.join([c for c in characters if c not in excluded_specials])

    # 아무 문자 옵션도 선택하지 않은 경우 숫자로만 구성
    if not characters:
        characters = string.digits

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# 브루트 포스 예상 시간 계산 함수
def brute_force_time_estimate(length, num_characters):
    attempts = num_characters ** length
    # 초 단위로 시간 계산
    speed = 1e9  # 초당 10억 번 시도 가능 가정
    time_seconds = attempts / speed

    # 시간을 읽기 쉬운 단위로 변환
    intervals = (
        ('년', 60 * 60 * 24 * 365.25),
        ('개월', 60 * 60 * 24 * 30),
        ('일', 60 * 60 * 24),
        ('시간', 60 * 60),
        ('분', 60),
        ('초', 1),
    )

    result = []
    for name, count in intervals:
        value = int(time_seconds // count)
        if value:
            time_seconds -= value * count
            result.append(f"{value} {name}")
    return ', '.join(result) if result else '0 초'

# 비밀번호 유출 여부 확인 함수
def check_password_leak(password, leaked_passwords):
    return password in leaked_passwords

# 비밀번호 위험성 평가 함수
def evaluate_password_strength(password, leaked_passwords):
    # 문자 집합 크기 계산
    char_set = 0
    if any(c.isupper() for c in password):
        char_set += 26
    if any(c.islower() for c in password):
        char_set += 26
    if any(c.isdigit() for c in password):
        char_set += 10
    if any(c in string.punctuation for c in password):
        char_set += len(string.punctuation)

    # 모호한 문자 포함 여부 확인
    if any(c in 'O0I1|' for c in password):
        char_set -= len([c for c in password if c in 'O0I1|'])

    # 브루트 포스 예상 시간 계산
    time_to_crack = brute_force_time_estimate(len(password), char_set)  # 예상 시간 계산

    # "년"이 포함되지 않으면 위험으로 판단
    if '년' not in time_to_crack:
        strength = "위험"  # "년"이 포함되지 않으면 위험
        time_to_crack = "5년 미만"  # 계산 시간이 5년 미만인 경우
    else:
        # 계산 시간이 5년 이상인지 5년 미만인지 판단
        time_in_years = 0
        # 예상 시간에서 "년"을 추출하고, 년을 제외한 값이 5년 이상이면 안전으로 판단
        if '년' in time_to_crack:
            years_str = time_to_crack.split('년')[0].strip()
            time_in_years = float(years_str) if years_str else 0

        if time_in_years >= 5:
            strength = "안전"
            time_to_crack = f"{int(time_in_years)}년 이상"
        elif time_in_years < 5 and time_in_years > 0:
            strength = "중간"
            time_to_crack = f"{int(time_in_years)}년 미만"
        else:
            strength = "위험"
            time_to_crack = "5년 미만"

    # RockYou 데이터셋에서 비밀번호가 유출된 경우
    is_leaked = password in leaked_passwords

    # 유출된 비밀번호일 경우 위험
    if is_leaked:
        strength = "위험"
        time_to_crack = "유출됨"

    return strength, time_to_crack, is_leaked


################## Streamlit 앱 시작####################

# 스타일 정의
st.markdown("""
    <style>
    .image-container {              /* title 옆 물감 이미지 */
        margin-top: -100px;         /* margin 간격 조정 */
    }
    .title {                        /* title */
        text-align: center;         /* 가운데 정렬 */
        font-family: 'Times New Roman', sans-serif;  /* Arial 폰트 */
        font-size: 50px;            /* 글자 크기 */
        font-weight: bold;          /* 굵게 */
        color: white;                /* 색상 */
        margin-left: -350px;        /* 타이틀과 이미지의 간격 조정 */
        margin-top: 80px;           /* 타이틀과 이미지의 간격 조정 */
        text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.5), -4px -4px 8px rgba(0, 0, 0, 0.5), /* 제목 그림자 */
            4px -4px 8px rgba(0, 0, 0, 0.5), -4px 4px 8px rgba(0, 0, 0, 0.5);
    }
    .header-box1 {                  /* 첫번째 header */
        text-align: center;
        background: #f0f0f0;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 10px;
        margin: 20px auto;
        width: 70%;
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-top : -70px;
    }
    .header-box2 {                  /* 두번째 header */
        text-align: center;
        background: #f0f0f0;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 10px;
        margin: 20px auto;
        width: 70%;
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
    .password-box {                 /* 비밀번호를 출력할 상자 */
        width: 400px;
        height: 40px;
        background: #F2F2F2;        /* 상자 색상(현재는 회색 -> 추후 빨, 파, 초로 변경해야함) */
        text-align: center;
        font-size: 18px;
        border-radius: 10px;
        margin-top: -5px;
        padding: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 이미지와 타이틀을 양옆으로 배치
col1, col2 = st.columns(2)

# 왼쪽 column : 이미지
with col1:
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image("image/colorsImage.jpeg", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

# 오른쪽 column : 타이틀
with col2:
    st.markdown('<div class="title">비밀번호 생성기 및 검사기</div>', unsafe_allow_html=True)

# 헤더 디자인
st.markdown('<div class="header-box1">안전한 비밀번호를 생성해드립니다.</div>', unsafe_allow_html=True)

# Kaggle 데이터셋 다운로드 함수
def download_kaggle_data():
    try:
        st.write("Downloading dataset...")
        path = kagglehub.dataset_download("wjburns/common-password-list-rockyoutxt")
        st.success("Dataset downloaded successfully!")
        return path
    except Exception as e:
        st.error(f"Error downloading dataset: {e}")
        return None

# Kaggle 데이터 다운로드 및 파일 경로 가져오기
dataset_path = download_kaggle_data()
if dataset_path:
    file_path = os.path.join(dataset_path, "rockyou.txt")
else:
    st.error("Kaggle 데이터를 다운로드하지 못했습니다. 앱을 재시작하거나 환경 변수를 확인하세요.")
    st.stop()

# RockYou 데이터 로드
if os.path.exists(file_path):
    st.write("Loading RockYou dataset...")
    with open(file_path, "r", encoding="latin-1") as file:
        leaked_passwords = set(line.strip() for line in file)
    st.success(f"RockYou 데이터가 로드되었습니다. 총 {len(leaked_passwords)} 개의 비밀번호를 확인할 수 있습니다.")
else:
    st.error("RockYou 데이터셋 파일을 찾을 수 없습니다.")
    st.stop()

# 비밀번호 길이 선택
password_length = st.slider("비밀번호 길이를 선택하세요", min_value=8, max_value=32, value=12)

# 비밀번호 개수 선택
num_passwords = st.slider("생성할 비밀번호 개수를 선택하세요", min_value=1, max_value=5, value=1)

# 문자 옵션 선택을 가로로 나열 (2행으로 변경)
col1, col2, col3 = st.columns(3)
with col1:
    include_uppercase = st.checkbox("대문자 포함")
with col2:
    include_lowercase = st.checkbox("소문자 포함")
with col3:
    include_digits = st.checkbox("숫자 포함")

# 다음 행에 가로로 나열  
col4, col5, col6 = st.columns(3)
with col4:
    include_specials = st.checkbox("특수문자 포함")
    excluded_specials = ""  # 특수문자 제외 문자열 초기화
with col5:
    exclude_ambiguous = st.checkbox("모호한 문자 제외 (O, 0, I, 1, |)")
with col6:
    use_base64 = st.checkbox("비밀번호를 Base64로 인코딩")

# 특수문자 체크박스 체크 시, 특수문자 제외 텍스트 상자 활성화
if include_specials:       
    excluded_specials = st.text_input("제외하고싶은 특수문자를 공백 없이 입력하세요. (없을 시 빈칸)")

# 비밀번호 생성 버튼
generate_button = st.button("비밀번호 생성", help="버튼을 누르면 비밀번호를 생성합니다.")
# 비밀번호를 미리 표시할 자리 설정 (빈 공간을 미리 준비)
password_display_area = st.empty()


# 버튼 클릭 시 비밀번호 생성
if generate_button:
    passwords = []  # 생성된 비밀번호를 저장할 리스트
    estimated_times = []  # 브루트 포스 예상 시간을 저장할 리스트
    evaluations = []  # 각 비밀번호 위험성 평가 결과를 저장할 리스트

    for _ in range(num_passwords):
        # 비밀번호 생성
        pwd = generate_password(password_length, include_uppercase, include_lowercase, include_digits, include_specials, exclude_ambiguous, excluded_specials)
        passwords.append(pwd)

        # Base64 인코딩 옵션 처리
        if use_base64:
            pwd_encoded = base64.b64encode(pwd.encode()).decode()  # Base64로 인코딩
            st.success(f"{pwd} -> (Base64 인코딩) -> {pwd_encoded}")
            pwd = pwd_encoded  # 인코딩된 비밀번호로 업데이트

        # 문자 집합 크기 계산
        char_set = 0
        if include_uppercase:
            char_set += 26  # 대문자 포함 시 문자 집합에 26 추가
        if include_lowercase:
            char_set += 26  # 소문자 포함 시 문자 집합에 26 추가
        if include_digits:
            char_set += 10  # 숫자 포함 시 문자 집합에 10 추가
        if include_specials:
            char_set += len(string.punctuation)  # 특수 문자 포함 시 특수문자 개수 추가
        if exclude_ambiguous:
            ambiguous_chars = 'O0I1|'  # 모호한 문자 정의
            char_set -= len(ambiguous_chars)  # 모호한 문자 제거 시 문자 집합 크기에서 제외

        # 브루트 포스 안전성 검사
        estimated_time = brute_force_time_estimate(password_length, char_set)
        estimated_times.append(estimated_time)

        # 비밀번호 위험성 평가 수행
        strength, time_to_crack, is_leaked = evaluate_password_strength(pwd, leaked_passwords)
        evaluations.append((strength, time_to_crack, is_leaked))  # 평가 결과를 리스트에 추가

    # 각 비밀번호를 박스에 표시
    for i, (pwd, eval_result, est_time) in enumerate(zip(passwords, evaluations, estimated_times)):
        strength, time_to_crack, is_leaked = eval_result

        # 박스 색상 설정 (위험성에 따라)
        if strength == "위험":
            box_color = "#F6CED8"  # 빨간색 (위험)
            eval_color = "#F6CED8"  # 글자색 빨간색
            text_shadow = "1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"  # 글자 테두리 (검정색)
        elif strength == "중간":
            box_color = "#F5F6CE"  # 노란색 (중간)
            eval_color = "#F5F6CE"  # 글자색 노란색
            text_shadow = "1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"  # 글자 테두리 (검정색)
        else:
            box_color = "#CEF6CE"  # 초록색 (안전)
            eval_color = "#CEF6CE"  # 글자색 초록색
            text_shadow = "1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"  # 글자 테두리 (검정색)

        # 비밀번호 출력 박스와 위험성 평가 결과를 오른쪽에 표시
        password_box = st.empty()  # 각 비밀번호 박스를 빈 공간으로 설정
        password_box.markdown(
            f'<div style="display: flex; align-items: center;">'
            f'<div class="password-box" style="background-color: {box_color}; padding: 10px; margin-right: 10px;">{pwd}</div>'
            f'<div style="font-weight: bold; font-size: 16px; color: {eval_color}; text-shadow: {text_shadow}; padding: 5px;">{strength}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
        # 예상 크래킹 시간 출력
        st.info(f"비밀번호가 깨질 때까지 예상 시간: {est_time}")


# 사용자 비밀번호 입력 및 검사
st.markdown('<div class="header-box2">비밀번호 유출 검사</div>', unsafe_allow_html=True)

user_password = st.text_input("비밀번호를 입력하세요:", type="password")

if st.button("비밀번호 검사"):
    if user_password:
        # 문자 집합 크기 계산
        char_set_user = 0
        if any(c.isupper() for c in user_password):
            char_set_user += 26
        if any(c.islower() for c in user_password):
            char_set_user += 26
        if any(c.isdigit() for c in user_password):
            char_set_user += 10
        if any(c in string.punctuation for c in user_password):
            char_set_user += len(string.punctuation)

        # 모호한 문자 포함 여부 확인
        if any(c in 'O0I1|' for c in user_password):
            char_set_user -= len([c for c in user_password if c in 'O0I1|'])

        estimated_time_user = brute_force_time_estimate(len(user_password), char_set_user)
        st.info(f"이 비밀번호가 깨질 때까지 예상 시간: {estimated_time_user}")

        is_leaked = check_password_leak(user_password, leaked_passwords)
        if is_leaked:
            st.warning("경고: 이 비밀번호는 RockYou 데이터셋에 포함되어 있습니다!")
        else:
            st.success("이 비밀번호는 안전합니다. RockYou 데이터셋에 포함되어 있지 않습니다.")