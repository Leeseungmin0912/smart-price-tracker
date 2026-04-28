import sqlite3
import pandas as pd

DB_NAME = "tracker.db"

def init_db():
    """데이터베이스와 테이블을 처음 생성하는 함수"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT,
                  title TEXT,
                  target_price INTEGER,
                  current_price INTEGER,
                  status TEXT)''')
    conn.commit()
    conn.close()

# 💡 [누락되었던 함수 추가] 상품 등록을 위해 꼭 필요한 함수입니다!
def add_product(url, title, target_price, current_price):
    """새로운 상품을 DB에 추가하는 함수"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO products (url, title, target_price, current_price, status) VALUES (?, ?, ?, ?, ?)",
              (url, title, target_price, current_price, "⏳ 추적 중"))
    conn.commit()
    conn.close()

def get_all_products():
    """DB에 있는 모든 상품을 Pandas 데이터프레임으로 가져오는 함수"""
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT 
        title as '상품명', 
        current_price as '현재가', 
        target_price as '희망가', 
        url as '구매 링크', 
        status as '상태' 
    FROM products
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_product_status(title, new_status, new_price):
    """상품의 상태와 최신 가격을 업데이트하는 함수"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE products SET status = ?, current_price = ? WHERE title = ?",
              (new_status, new_price, title))
    conn.commit()
    conn.close()

def clear_db():
    """DB에 있는 모든 데이터를 삭제하는 함수"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM products")
    c.execute("DELETE FROM sqlite_sequence WHERE name='products'")
    conn.commit()
    conn.close()