import os
import requests
import urllib.parse
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup  # 💡 [필수] 누락되었던 BeautifulSoup 임포트 추가

load_dotenv()


def extract_title_from_url(url):
    """URL에 접속해서 제목을 가져오되, 서버 차단 시 URL 주소창 텍스트를 해독하는 우회 함수"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # 타임아웃을 주어 서버가 무한 로딩에 빠지는 것을 방지합니다.
        res = requests.get(url, headers=headers, timeout=5)

        # 1. 서버가 차단당하지 않고 성공적으로 접속되었을 때 (status 200)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                return og_title.get("content").strip()

            title_tag = soup.title.string if soup.title else ""
            if title_tag:
                return title_tag.strip()

        # 2. 💡 [강력한 우회 전략] 클라우드 서버 IP가 쇼핑몰로부터 차단(403 등)당했을 때
        print("⚠️ 서버가 쇼핑몰로부터 차단당했습니다. URL 텍스트 분석 및 해독을 시작합니다.")

        # 주소창에 %E2%9C... 처럼 인코딩되어 깨진 한글을 읽을 수 있게 디코딩(해독)합니다.
        decoded_url = urllib.parse.unquote(url)

        # 네이버 쇼핑 카탈로그 주소 구조 대응 (예: catalog/123456 -> 번호 추출)
        match = re.search(re.escape("catalog/") + r"(\d+)", decoded_url)
        if match:
            return f"네이버 카탈로그 {match.group(1)}"

        # 일반적인 쇼핑몰 주소의 마지막 경로 슬래시(/) 뒤에서 상품 힌트 단어 추출
        url_parts = [p for p in decoded_url.split('/') if p]
        if url_parts:
            last_part = url_parts[-1].split('?')[0]  # 주소 뒤의 지저분한 옵션(?...) 제거
            if len(last_part) > 2:
                # 붙어있는 대시(-)나 언더바(_)를 공백으로 치환해 검색어로 쓰기 좋게 만듭니다.
                return last_part.replace('-', ' ').replace('_', ' ')

        return None
    except Exception as e:
        print(f"URL 파싱 에러 발생: {e}")
        return None


def get_product_info(keyword, min_price=10000, max_price=None, custom_exclude=""):
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")

    # 💡 [핵심 작동] 만약 사용자가 'http'로 시작하는 웹 주소를 검색창에 넣었다면?
    if keyword.startswith("http"):
        print("🔗 URL이 감지되었습니다. 상품명을 추출합니다...")
        extracted_title = extract_title_from_url(keyword)

        if not extracted_title:
            print("🚨 URL에서 상품명을 유추하는 데 실패했습니다.")
            return None, None, None

        print(f"📝 추출된 상품명: {extracted_title}")
        # 추출한 제목을 진짜 검색어(keyword)로 교체하여 네이버 API로 보냅니다!
        keyword = extracted_title

    # ==========================================
    # 네이버 쇼핑 API 검색 가동
    # ==========================================
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

            base_excluded = ['케이스', '필름', '보호', '파우치', '스트랩', '중고', '렌탈', '대여', '해외', '거치대', '케이블', '충전기', '공기계', '매입',
                             '액정', '교환', '리퍼']

            if custom_exclude:
                user_excludes = [w.strip() for w in custom_exclude.split(',') if w.strip()]
                base_excluded.extend(user_excludes)

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