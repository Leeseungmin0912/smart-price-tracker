import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()


def get_product_info(keyword, min_price=10000, max_price=None, custom_exclude=""):
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")

    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    params = {
        "query": keyword,
        "display": 100,
        "sort": "sim"
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            # 1. 기본 금지어 세팅
            base_excluded = ['케이스', '필름', '보호', '파우치', '스트랩', '중고', '렌탈', '대여', '해외', '거치대', '케이블', '충전기', '공기계', '매입',
                             '액정', '교환', '리퍼']

            if custom_exclude:
                user_excludes = [w.strip() for w in custom_exclude.split(',') if w.strip()]
                base_excluded.extend(user_excludes)

            # 💡 [핵심 기술 추가] 사용자가 대놓고 '충전기'를 검색했다면, 금지어 목록에서 '충전기'를 빼줍니다!
            # (검색어에 없는 단어들만 진짜 금지어로 남깁니다)
            active_excluded = [word for word in base_excluded if word not in keyword]

            clean_keyword = re.sub(r'[^a-zA-Z0-9가-힣\s]', '', keyword)
            search_words = clean_keyword.split()

            print(f"\n🔍 [{keyword}] 검색 시작... (필터 적용 중)")

            valid_items = []

            for item in items:
                title = item['title'].replace('<b>', '').replace('</b>', '')
                price = int(item['lprice'])

                clean_title = re.sub(r'[^a-zA-Z0-9가-힣]', '', title).upper()

                is_exact_match = True
                for word in search_words:
                    if word.upper() not in clean_title:
                        is_exact_match = False
                        break
                if not is_exact_match:
                    continue

                # 💡 수정: 기존 excluded_words 대신 똑똑해진 active_excluded를 사용합니다.
                is_excluded = any(word in title for word in active_excluded)
                if is_excluded:
                    continue

                if price < min_price:
                    continue
                if max_price and price > max_price:
                    continue

                link = item['link']
                valid_items.append((title, price, link))

            if valid_items:
                cheapest_item = min(valid_items, key=lambda x: x[1])
                print(f"🎯 조건에 맞는 최저가 발견!: {cheapest_item[0]} ({cheapest_item[1]}원)\n")
                return cheapest_item[0], cheapest_item[1], cheapest_item[2]
            else:
                print("🚨 검색어 및 필터 조건에 맞는 상품을 찾지 못했습니다.")
                return None, None, None

        else:
            print(f"🚨 API 에러: {response.status_code}")
            return None, None, None

    except Exception as e:
        print(f"🚨 에러 발생: {e}")
        return None, None, None