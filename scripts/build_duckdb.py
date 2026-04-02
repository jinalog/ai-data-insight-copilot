"""
build_duckdb.py

목적
    - raw CSV 데이터를 DuckDB 테이블로 적재하고 분석용 마트(View) 생성

입력
    - data/raw/*.csv

출력
    - data/processed/insight.duckdb

핵심 로직
    - CSV → DuckDB 테이블 적재
    - 일자/카테고리 기반 매출 집계 뷰 생성
    - 이벤트 퍼널 집계 뷰 생성

설계 의도
    - LLM 질의 및 BI 분석에서 재사용 가능한 집계 레이어 제공

한계 / 향후 개선
    - Materialized View 미적용
    - 대용량 데이터 처리 최적화 없음
    - Parquet 기반 저장 고려 가능
"""


from __future__ import annotations

from pathlib import Path
import duckdb

# DB 파일 저장 경로 설정
DB_PATH = "data/processed/insight.duckdb"


def main() -> None:
    # 1. 저장 경로 폴더 생성
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # 2. DuckDB 연결 (파일이 없으면 새로 생성)
    con = duckdb.connect(DB_PATH)

    # 3. Raw Data(CSV)를 DB 테이블로 로드 (이미 있으면 덮어씀)
    # read_csv_auto: 데이터 타입을 DuckDB가 자동으로 추론하여 읽어옴
    print("Loading CSV data into DuckDB...")
    
    # users.csv를 users 테이블로 적재
    con.execute("""
        CREATE OR REPLACE TABLE users AS
        SELECT * FROM read_csv_auto('data/raw/users.csv');
    """)

    # products.csv를 products 테이블로 적재
    con.execute("""
        CREATE OR REPLACE TABLE products AS
        SELECT * FROM read_csv_auto('data/raw/products.csv');
    """)

    # events.csv를 events 테이블로 적재
    con.execute("""
        CREATE OR REPLACE TABLE events AS
        SELECT * FROM read_csv_auto('data/raw/events.csv');
    """)

    # orders.csv를 orders 테이블로 적재
    con.execute("""
        CREATE OR REPLACE TABLE orders AS
        SELECT * FROM read_csv_auto('data/raw/orders.csv');
    """)

    # 4. Daily Revenue Mart 생성
    # 일자별, 카테고리별로 주문 건수와 매출 총액을 집계
    print("Creating mart_daily_revenue view...")
    
    # 일자별/카테고리별 매출 마트 뷰 생성
    con.execute("""
        CREATE OR REPLACE VIEW mart_daily_revenue AS
        SELECT
            CAST(order_time AS DATE) AS order_date,
            category,
            COUNT(*) AS order_count,
            SUM(amount) AS revenue
        FROM orders
        GROUP BY 1, 2
        ORDER BY 1, 2;
    """)

    # 5. Daily Funnel Mart 생성
    # 일자별로 View -> Click -> Add to Cart -> Purchase로 이어지는 행동 수를 집계
    print("Creating mart_funnel_daily view...")
    
    # 일자별 퍼널 집계 뷰 생성
    con.execute("""
        CREATE OR REPLACE VIEW mart_funnel_daily AS
        SELECT
            CAST(event_time AS DATE) AS event_date,
            SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
            SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS clicks,
            SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_to_carts,
            SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
        FROM events
        GROUP BY 1
        ORDER BY 1;
    """)

    con.close() # 연결 종료
    print(f"DuckDB built at: {DB_PATH}")


if __name__ == "__main__":
    main() # 직접 실행 시 main 호출