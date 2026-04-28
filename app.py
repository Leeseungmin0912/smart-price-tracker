import streamlit as st
import pandas as pd
from Scraper import get_product_info
import database
import threading
import bot  # 우리가 만든 bot.py를 불러옵니다.

# 💡 서버가 켜질 때 봇을 백그라운드 쓰레드로 딱 한 번만 실행합니다.
if 'bot_started' not in st.session_state:
    thread = threading.Thread(target=bot.job_loop) # bot.py에 job_loop 함수를 만들어야 합니다.
    thread.daemon = True
    thread.start()
    st.session_state['bot_started'] = True

st.set_page_config(page_title="Smart Price Tracker", page_icon="🛒", layout="wide")
database.init_db()

# ================= 사이드바: 상품 검색 및 등록 =================
# ... 앞부분 코드 동일 ...

# ================= 사이드바: 상품 검색 및 등록 =================
with st.sidebar:
    st.title("➕ 새로운 상품 등록")

    # clear_on_submit을 False로 해서 검색 실패해도 입력한 값이 날아가지 않게 합니다.
    with st.form("add_form", clear_on_submit=False):
        search_keyword = st.text_input("🔍 검색어", placeholder="예: 갤럭시 S26 자급제 256")
        target_price = st.number_input("💰 알림 희망 가격 (원)", min_value=0, step=100)

        # 💡 [핵심 UI] 고급 검색 필터 (토글 형태)
        with st.expander("⚙️ 고급 검색 필터 (선택사항)"):
            min_p = st.number_input("최소 가격 (너무 싼 가짜 상품 제외)", value=10000, step=10000)
            max_p = st.number_input("최대 가격 (0이면 제한 없음)", value=0, step=10000)
            custom_ex = st.text_input("추가 제외어 (쉼표로 구분)", placeholder="예: 해외, 가개통, S급")

        submit_button = st.form_submit_button("최저가 추적 시작")

    if submit_button:
        if search_keyword:
            with st.spinner("네이버 쇼핑 최저가를 찾는 중입니다..."):
                # 최대 가격이 0이면 None으로 변환해서 제한이 없도록 처리
                max_p_val = max_p if max_p > 0 else None

                # 💡 수집 엔진에 필터 조건들을 함께 던져줍니다!
                title, price, link = get_product_info(
                    keyword=search_keyword,
                    min_price=min_p,
                    max_price=max_p_val,
                    custom_exclude=custom_ex
                )

                if title:
                    database.add_product(link, title, target_price, price)
                    st.success(f"✅ 추적 시작!\n\n**{title}**\n\n현재 최저가: **{price:,}원**")
                    # 성공했을 때만 화면을 새로고침해서 표에 반영합니다
                    st.rerun()
                else:
                    st.error("조건에 맞는 결과가 없습니다. 필터를 조정하거나 핵심 키워드만 입력해보세요.")
        else:
            st.warning("검색어를 입력해주세요.")

# ================= 메인 화면: 추적 리스트 =================
st.title("🚇 Smart Price Tracker")
st.subheader("현재 추적 중인 상품 목록")

df = database.get_all_products()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="전체 추적 상품", value=f"{len(df)} 개")
with col2:
    st.metric(label="API 상태", value="🟢 정상 (차단 방지)")
with col3:
    st.metric(label="최근 업데이트", value="방금 전")

st.divider()

if len(df) > 0:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,  # 불필요한 숫자 인덱스 숨기기
        column_config={
            "현재가": st.column_config.NumberColumn(format="%d 원"),
            "희망가": st.column_config.NumberColumn(format="%d 원"),
            # 💡 [핵심 UX 개선] 길고 지저분한 URL 대신 깔끔한 링크 텍스트로 보여줍니다!
            "구매 링크": st.column_config.LinkColumn(
                "구매 링크",
                display_text="🔗 구매하러 가기"
            )
        }
    )
else:
    st.info("현재 추적 중인 상품이 없습니다. 왼쪽 사이드바에서 상품을 검색해보세요!")

