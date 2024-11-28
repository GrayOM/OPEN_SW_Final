import os
import random
import string
import base64
import pandas as pd
import kagglehub
import streamlit as st
from dotenv import load_dotenv


# 환경 변수 로드
load_dotenv()
api_key = os.getenv("API_KEY")
username = os.getenv("API_USERNAME")


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
    
    

# 비밀번호 생성 함수
def generate_password(length, include_upper, include_lower, include_digits, include_specials, exclude_ambiguous):
    characters = ''
    if include_upper:
        characters += string.ascii_uppercase
    if include_lower:
        characters += string.ascii_lowercase
    if include_digits:
        characters += string.digits
    if include_specials:
        characters += string.punctuation
    if exclude_ambiguous:
        ambiguous_chars = 'O0I1|'
        characters = ''.join([c for c in characters if c not in ambiguous_chars])
    if not characters:
        characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# 브루트 포스 예상 시간 계산 함수
def brute_force_time_estimate(length, num_characters):
    attempts = num_characters ** length
    speed = 1e9  # 초당 10억 번 시도 가능 가정
    time_seconds = attempts / speed
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

# Streamlit 앱 시작
st.title("비밀번호 생성기 및 유출 여부 확인")

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

# 비밀번호 생성 옵션
st.header("비밀번호 생성기")
password_length = st.slider("비밀번호 길이:", min_value=8, max_value=32, value=12)
num_passwords = st.slider("생성할 비밀번호 개수:", min_value=1, max_value=5, value=1)
include_uppercase = st.checkbox("대문자 포함")
include_lowercase = st.checkbox("소문자 포함")
include_digits = st.checkbox("숫자 포함")
include_specials = st.checkbox("특수문자 포함")
exclude_ambiguous = st.checkbox("모호한 문자 제외 (O, 0, I, 1, |)")
use_base64 = st.checkbox("Base64 인코딩")

if st.button("비밀번호 생성"):
    passwords = []
    for _ in range(num_passwords):
        password = generate_password(password_length, include_uppercase, include_lowercase, include_digits, include_specials, exclude_ambiguous)
        if use_base64:
            password = base64.b64encode(password.encode()).decode()
        passwords.append(password)
    st.write("생성된 비밀번호:")
    for pwd in passwords:
        st.code(pwd)

# 비밀번호 유출 여부 검사
st.header("비밀번호 유출 여부 확인")
user_password = st.text_input("검사할 비밀번호를 입력하세요:", type="password")

if st.button("비밀번호 유출 여부 검사"):
    if user_password:
        is_leaked = check_password_leak(user_password, leaked_passwords)
        if is_leaked:
            st.warning("경고: 이 비밀번호는 RockYou 데이터셋에 포함되어 있습니다!")
        else:
            st.success("이 비밀번호는 안전합니다. RockYou 데이터셋에 포함되어 있지 않습니다.")
        # 브루트 포스 예상 시간 계산
        char_set_size = len(set(user_password))  # 비밀번호 내 고유 문자 수
        estimated_time = brute_force_time_estimate(len(user_password), char_set_size)
        st.info(f"브루트 포스 공격으로 이 비밀번호를 깨는 데 걸리는 예상 시간: {estimated_time}")
    else:
        st.error("비밀번호를 입력하세요.")
