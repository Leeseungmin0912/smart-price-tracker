import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(message):
    # .env에서 가져오되, 혹시 모르니 질문자님의 ID를 직접 써줍니다.
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = "6260703032"  # 👈 여기에 질문자님의 ID를 직접 넣었습니다!

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        # 터미널에 성공/실패 여부를 출력하게 만들었습니다.
        if response.status_code == 200:
            print("✅ [성공] 텔레그램 메시지가 발송되었습니다!")
        else:
            print(f"❌ [실패] 에러 내용: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"🚨 [에러] 연결 실패: {e}")
        return False


# 지금 바로 마우스 우클릭 -> Run 'notifier' 해서 메시지가 오는지 보세요!
if __name__ == "__main__":
    send_telegram_message("🤖 **알림 시스템 가동!**\n최저가 사냥을 시작합니다.")