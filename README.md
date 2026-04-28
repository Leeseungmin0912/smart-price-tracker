# 🛒 Smart Price Tracker (최저가 24시간 추적 봇)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Telegram API](https://img.shields.io/badge/Telegram_API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

## 📌 프로젝트 소개
**Smart Price Tracker**는 사용자가 원하는 상품과 희망 가격을 등록하면, 백그라운드에서 24시간 네이버 쇼핑 최저가를 감시하고 목표가 도달 시 텔레그램으로 즉시 알림을 보내주는 파이썬 기반의 자동화 파이프라인입니다. 

단순한 웹 스크래핑을 넘어, **웹 프론트엔드 대시보드(UI) - 관계형 데이터베이스(DB) - 백그라운드 스케줄러(Bot) - 메신저 API(Notification)** 로 이어지는 전체 데이터 흐름을 직접 설계하고 구현했습니다.

👉 **[Live Demo 보러가기](여기에_Streamlit_Cloud_배포_주소를_넣어주세요)**

---

## 🚀 주요 기능 (Key Features)

* **대시보드 UI (Streamlit):**
  * 직관적인 웹 인터페이스를 통해 새로운 추적 상품을 등록하고 현재 상태를 조회합니다.
  * 검색어, 희망 가격, 최소/최대 가격 필터, 제외 키워드 등 정교한 검색 조건을 설정할 수 있습니다.
* **백그라운드 자동화 스케줄링 (Schedule):**
  * 메인 웹 서버와 독립된 쓰레드(Thread)에서 봇이 동작하며, 지정된 주기(ex. 1분)마다 DB를 스캔하여 가격 변동을 감시합니다.
* **데이터베이스 관리 (SQLite3 & Pandas):**
  * 상품 정보, 목표가, 현재 상태(⏳ 추적 중, ✅ 달성 완료)를 영구적으로 저장하고 상태를 업데이트합니다.
* **실시간 텔레그램 알림 (Telegram Bot API):**
  * 수집된 현재가가 사용자의 목표가보다 낮아지는 즉시, 상품 상세 정보와 바로 구매 가능한 링크를 스마트폰으로 전송합니다.

---

## 🏗️ 시스템 아키텍처 (Architecture)

1. **`app.py`**: Streamlit 기반의 사용자 인터페이스 및 봇 백그라운드 쓰레드 실행
2. **`scraper.py`**: 네이버 쇼핑 데이터 검색 및 최저가, 링크 등 핵심 정보 파싱
3. **`database.py`**: SQLite3를 활용한 추적 상품 CRUD 로직 및 Pandas 데이터프레임 변환
4. **`bot.py`**: Schedule 모듈을 활용한 정기적 가격 감시 및 조건 판단 로직
5. **`notifier.py`**: Telegram API 연동 및 Markdown 형태의 알림 메시지 발송

---

## 🛠️ 기술 스택 (Tech Stack)
* **Language:** Python 3
* **Frontend:** Streamlit
* **Database:** SQLite3
* **Libraries:** `pandas`, `requests`, `schedule`, `python-dotenv`
* **Deployment:** Streamlit Community Cloud

---

## ⚙️ 로컬 실행 방법 (How to Run)

1. 저장소를 클론합니다.
```bash
git clone [https://github.com/Leeseungmin0912/smart-price-tracker.git](https://github.com/Leeseungmin0912/smart-price-tracker.git)
cd smart-price-tracker
```
2. 필요 라이브러리를 설치합니다.
```
pip install -r requirements.txt
```
3. 환경 변수 파일`(.env)`을 루트 디렉토리에 생성하고 키값을 입력합니다.
```bash
TELEGRAM_BOT_TOKEN="당신의_텔레그램_봇_토큰"
TELEGRAM_CHAT_ID="당신의_텔레그램_챗_아이디"
```
4. 애플리케이션을 실행합니다.
```bash
streamlit run app.py
```
-----
👉 [Live Demo 보러가기](https://sptnanfu.streamlit.https://sptnanfu.streamlit.app/)


