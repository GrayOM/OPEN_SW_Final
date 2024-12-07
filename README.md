# 🔐  OPEN_SW_Final 2조 비밀번호 생성기

이 프로젝트는 Streamlit을 사용하여 **안전한 비밀번호 생성**과 **유출된 비밀번호 확인** 기능을 제공합니다. 이 애플리케이션은 사용자가 비밀번호의 강도를 선택하고, 비밀번호의 브루트 포스 공격 예상 시간을 확인하며, RockYou 데이터셋을 기반으로 유출 여부를 검사할 수 있도록 설계되었습니다.

---

###  2조 참가자
- 👨‍💻 **박승민**
- 👨‍💻 **장우혁**
- 👨‍💻 **엄승현**

---

## 📋 주요 기능

### 1. 🔑 비밀번호 생성
- 비밀번호 길이를 설정할 수 있습니다 (8~32자).
- 대문자, 소문자, 숫자, 특수문자 포함 여부를 선택할 수 있습니다.
- 모호한 문자(`O`, `0`, `I`, `1`, `|`)를 제외할 수 있습니다.
- 선택적으로 Base64로 인코딩된 비밀번호를 생성합니다.

### 2. ⏱️ 브루트 포스 예상 시간 계산
- 비밀번호가 브루트 포스 공격으로 깨질 때까지의 예상 시간을 계산합니다.
- 비밀번호의 문자 집합 크기와 길이를 고려하여 시간을 예측합니다.

### 3. 🔍 RockYou 데이터셋 기반 유출 검사
- Kaggle에서 다운로드한 **RockYou 데이터셋**을 사용하여 비밀번호 유출 여부를 확인합니다.
- 유출된 비밀번호는 경고 메시지를 표시하며, 안전한 비밀번호는 성공 메시지를 표시합니다.

---

## 🔧 추가 기능

### 1. 🚨 비밀번호 위험성 평가 시각화
- 비밀번호 생성 후 브루트 포스 예상 시간을 이용해 3단계로 나누어 위험성을 평가합니다.
- 1년 미만 : 위험 / 1년 이상 5년 미만 : 중간 / 5년 이상 : 안전
- 만약 생성된 비밀번호가 RockYou 데이터셋에 포함되어 있다면 "위험"으로 간주하고 유출되었다는 메시지를 표시합니다.

### 2. 🚫 특수문자 종류 제외 기능
- 비밀번호 생성 시 제외하고싶은 특수문자를 입력하여 그 문자는 제외하고 비밀번호를 생성할 수 있습니다.
- 특수문자 체크박스 선택 시 텍스트상자가 활성화 됩니다.
- 특수문자 입력 후 엔터를 누르면 적용이 됩니다.

### 3. 🔐 비밀번호 추천 기능 추가
- 비밀번호 생성 추천 기능을 사용하여 자동으로 비밀번호를 생성할 수 있습니다.
- 추천 기능 체크박스 선택 시 추천 목록이 활성화 됩니다.
- 비밀번호의 사용처를 선택한 뒤에 생성을 누르면 자동으로 비밀번호를 생성합니다.

---

## 🖼️ 실행 예시

비밀번호 생성기:

![image](https://github.com/user-attachments/assets/20fcd1c0-5e24-401b-884c-8f781796f33a)

비밀번호 검출기:

![image](https://github.com/user-attachments/assets/d8695163-223f-4cd1-a96e-9477b4b12393)
---

## 🛠️ 설치 및 실행

### 1. 📥 요구 사항
- Python 3.8 이상
- Streamlit, pandas, kagglehub, python-dotenv 패키지 설치