import streamlit as st
import random
import string
import base64
import pandas as pd
from dotenv import load_dotenv
import os
import kagglehub

load_dotenv()
api_key = os.getenv("API_KEY")
username = os.getenv("API_USERNAME")

# 비밀번호 생성 함수
def generate_password(length, include_upper, include_lower, include_digits, include_specials, exclude_ambiguous):
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

# Streamlit 앱 시작
st.title("비밀번호 생성기")

st.header("비밀번호 생성 옵션")

# 비밀번호 길이 선택
password_length = st.slider("비밀번호 길이 선택:", min_value=8, max_value=32, value=12)

# 비밀번호 개수 선택
num_passwords = st.slider("생성할 비밀번호 개수:", min_value=1, max_value=5, value=1)

# 문자 옵션 선택
include_uppercase = st.checkbox("대문자 포함")
include_lowercase = st.checkbox("소문자 포함")
include_digits = st.checkbox("숫자 포함")
include_specials = st.checkbox("특수문자 포함")

# 모호한 문자 제외 옵션
exclude_ambiguous = st.checkbox("모호한 문자 제외 (O, 0, I, 1, |)")

# Base64 인코딩 옵션
use_base64 = st.checkbox("비밀번호를 Base64로 인코딩")

# 비밀번호 생성 버튼
if st.button("비밀번호 생성"):
    passwords = []
    estimated_times = []
    
    for _ in range(num_passwords):
        pwd = generate_password(password_length, include_uppercase, include_lowercase, include_digits, include_specials, exclude_ambiguous)
        passwords.append(pwd)

        if use_base64:
            pwd_encoded = base64.b64encode(pwd.encode()).decode()
            st.success(f"{pwd} -> (Base64 인코딩) -> {pwd_encoded}")
            pwd = pwd_encoded

        # 문자 집합 크기 계산
        char_set = 0
        if include_uppercase:
            char_set += 26
        if include_lowercase:
            char_set += 26
        if include_digits:
            char_set += 10
        if include_specials:
            char_set += len(string.punctuation)
        if exclude_ambiguous:
            ambiguous_chars = 'O0I1|'
            char_set -= len(ambiguous_chars)

        # 브루트 포스 안전성 검사
        estimated_time = brute_force_time_estimate(password_length, char_set)
        estimated_times.append(estimated_time)

    for pwd, est_time in zip(passwords, estimated_times):
        st.info(f"생성된 비밀번호: {pwd}")
        st.info(f"비밀번호가 깨질 때까지 예상 시간: {est_time}")

# 사용자 비밀번호 입력 및 검사
st.header("자신의 비밀번호 검사")

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

        # CSV 파일에서 유출된 비밀번호 로드
        try:
            leaked_df = pd.read_csv("leaked_passwords.csv")
            leaked_passwords = leaked_df['password'].astype(str).tolist()
            is_leaked = check_password_leak(user_password, leaked_passwords)
            if is_leaked:
                st.warning("경고: 이 비밀번호는 유출된 데이터베이스에 존재합니다!")
            else:
                st.success("이 비밀번호는 유출되지 않았습니다.")
        except FileNotFoundError:
            st.error("leaked_passwords.csv 파일을 찾을 수 없습니다.")
    else:
        st.error("비밀번호를 입력해주세요.")
