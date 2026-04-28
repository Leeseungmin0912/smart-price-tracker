import time
import schedule
import database
from Scraper import get_product_info
from notifier import send_telegram_message


def job():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🤖 정기 가격 감시를 시작합니다...")

    # 1. DB에서 현재 저장된 모든 상품 가져오기
    df = database.get_all_products()

    # 추적할 상품이 없으면 종료
    if df.empty:
        print("감시할 상품이 없습니다.")
        return

    # 2. '추적 중'인 상품들만 걸러서 하나씩 확인
    active_items = df[df['상태'] == '⏳ 추적 중']

    for index, row in active_items.iterrows():
        title = row['상품명']
        target_price = row['희망가']
        link = row['구매 링크']

        print(f"  🔍 검사 중: {title[:20]}... (목표가: {target_price}원)")

        # 3. 네이버 API를 통해 현재 최저가를 다시 조회 (제목으로 정확도 검색)
        new_title, new_price, new_link = get_product_info(title)

        if new_price:
            # 4. 가격 비교!
            if new_price <= target_price:
                print(f"  🎉 목표가 달성! ({new_price}원)")

                # 메세지 구성 및 발송
                msg = (f"🚨 **최저가 알림** 🚨\n\n"
                       f"기다리시던 상품이 목표가에 도달했습니다!\n"
                       f"📦 **상품명:** {title}\n"
                       f"💰 **현재가:** {new_price:,}원 (목표가: {target_price:,}원)\n\n"
                       f"[👉 바로 구매하러 가기]({new_link})")
                send_telegram_message(msg)

                # DB 상태를 '완료'로 변경하여 다음번엔 검사하지 않게 함
                database.update_product_status(title, "✅ 달성 완료", new_price)
            else:
                print(f"  - 아직 비쌉니다. (현재가: {new_price}원)")
                # 가격이 바뀌었을 수 있으니 DB 가격만 최신화 (상태는 그대로 유지)
                database.update_product_status(title, "⏳ 추적 중", new_price)

    print("✅ 이번 주기 감시 완료.\n")


# ================= 스케줄러 설정 =================
print("🤖 Smart Price Bot 작동을 시작합니다.")
# 테스트를 위해 우선 '1분'마다 실행되게 설정합니다.
# (실제 사용할 땐 schedule.every(1).hours.do(job) 으로 바꾸세요)
schedule.every(1).minutes.do(job)

def job_loop():
    job()

    schedule.every(10).minutes.do(job)

# 무한 루프를 돌며 예약된 시간이 되면 job()을 실행합니다.
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    job_loop()