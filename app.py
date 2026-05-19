import streamlit as st
import database
import threading
import bot
from Scraper import get_product_info # 💡 수집 함수 임포트 필수!

# 1. [필수] 페이지 설정은 반드시 코드 최상단에 위치해야 합니다.
st.set_page_config(page_title="Smart Price Tracker", page_icon="🛒", layout="wide")

# 2. [필수] 서버 시작 시 DB 테이블 생성
database.init_db()

@st.cache_resource
def start_background_bot():
    thread = threading.Thread(target=bot.job_loop)
    thread.daemon = True
    thread.start()
    return True

start_background_bot()

# ================= 사이드바: 상품 검색 및 등록 =================
with st.sidebar:
    st.title("➕ 새로운 상품 등록")

    with st.form("add_form", clear_on_submit=False):
        search_keyword = st.text_input("🔍 검색어", placeholder="예: 갤럭시 S26 자급제 256")
        target_price = st.number_input("💰 알림 희망 가격 (원)", min_value=0, step=100)

        with st.expander("⚙️ 고급 검색 필터 (선택사항)"):
            min_p = st.number_input("최소 가격", value=10000, step=10000)
            max_p = st.number_input("최대 가격 (0이면 제한 없음)", value=0, step=10000)
            custom_ex = st.text_input("추가 제외어 (쉼표로 구분)", placeholder="예: 해외, 가개통, S급")

        submit_button = st.form_submit_button("최저가 추적 시작")

    if submit_button:
        if search_keyword:
            with st.spinner("네이버 쇼핑 최저가를 찾는 중입니다..."):
                max_p_val = max_p if max_p > 0 else None
                title, price, link = get_product_info(
                    keyword=search_keyword,
                    min_price=min_p,
                    max_price=max_p_val,
                    custom_exclude=custom_ex
                )

                if title:
                    database.add_product(link, title, target_price, price)
                    st.success(f"✅ 추적 시작!\n\n**{title}**\n\n현재 최저가: **{price:,}원**")
                    st.rerun()
                else:
                    st.error("조건에 맞는 결과가 없습니다. 필터를 조정해보세요.")
        else:
            st.warning("검색어를 입력해주세요.")

# ================= 메인 화면: 추적 리스트 =================
st.title("🚀 Smart Price Tracker")
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
        width='stretch',
        hide_index=True,
        column_config={
            "현재가": st.column_config.NumberColumn(format="%d 원"),
            "희망가": st.column_config.NumberColumn(format="%d 원"),
            "구매 링크": st.column_config.LinkColumn(
                "구매 링크",
                display_text="🔗 구매하러 가기"
            )
        }
    )
else:
    st.info("현재 추적 중인 상품이 없습니다. 왼쪽 사이드바에서 상품을 검색해보세요!")
