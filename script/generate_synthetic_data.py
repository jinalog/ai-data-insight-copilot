"""
generate_synthetic_data.py

목적
    - 분석용 샘플 데이터를 생성하여 data/raw 디렉토리에 CSV 형태로 저장

입력
    - 없음 (내부 랜덤 생성)

출력
    - data/raw/users.csv
    - data/raw/products.csv
    - data/raw/events.csv
    - data/raw/orders.csv

핵심 로직
    - 사용자 / 상품 / 이벤트 / 주문 데이터 생성
    - 이벤트 기반으로 주문 데이터 파생 생성

한계 / 향후 개선
    - 이벤트 발생 확률이 균등 분포 (비현실적)
    - 시즌성 / 사용자 행동 패턴 미반영
    - 실제 서비스 형태에 맞춘 funnel 분포 필요
"""

from __future__ import annotations

from pathlib import Path
from random import choice, randint, random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()


# 1. 사용자 데이터 생성
def generate_users(n: int = 1000) -> pd.DataFrame:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180) # 현재부터 180일 전까지의 기간 설정
    
    rows = []
    for user_id in range(1, n + 1):
        signup_at = start_date + timedelta(days=randint(0, 180)) # 가입일 180일 범위 안에서 랜덤
        rows.append(
            {
                "user_id": user_id,
                "country": choice(["KR", "JP", "TH", "TW"]),
                "device_type": choice(["ios", "android", "web"]),
                "signup_at": signup_at,
            }
        )
    return pd.DataFrame(rows)


# 2. 상품 데이터 생성
def generate_products(n: int = 200) -> pd.DataFrame:
    categories = ["electronics", "fashion", "beauty", "food", "home"]
    rows = []
    
    for product_id in range(1, n + 1):
        category = choice(categories)
        price = randint(10, 500) * 1000 # 1만 ~ 50만원 범위 가격
        rows.append(
            {
                "product_id": product_id,
                "product_name": fake.word().title(),
                "category": category,
                "price": price,
            }
        )
    return pd.DataFrame(rows)


# 3. 이벤트 데이터 생성 (조회, 클릭, 장바구니, 구매)
def generate_events(users_df: pd.DataFrame, products_df: pd.DataFrame, n: int = 30000,) -> pd.DataFrame:
    end = datetime.now()
    start = end - timedelta(days=59) # 최근 60일간의 데이터

    rows = []
    product_ids = products_df["product_id"].tolist()
    user_ids = users_df["user_id"].tolist()
    
    # TODO: 실제 서비스처럼 view > click > purchase 비대칭 분포 적용 필요
    event_types = ["view", "click", "add_to_cart", "purchase"]
    
    for event_id in range(1, n + 1):
        event_time = start + timedelta(
            days=randint(0, 59),
            hours=randint(0, 23),
            minutes=randint(0, 59),
            seconds=randint(0, 59),
        )
        
        rows.append(
            {
                "event_id": event_id,
                "user_id": choice(user_ids),
                "product_id": choice(product_ids),
                "event_type": choice(event_types),
                "event_time": event_time,
            }
        )
        
    return pd.DataFrame(rows)


# 4. 주문 데이터 생성 (이벤트 중 'purchase'만 골라내어 생성)
def generate_orders(events_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    purchase_df = events_df[events_df["event_type"] == "purchase"].copy()
    merged = purchase_df.merge(products_df, on="product_id", how="left")

    rows = []
    for i, row in enumerate(merged.itertuples(index=False), start=1):
        # 간단 할인 시뮬레이션 - 20%의 확률로 10% 할인 적용 (랜덤 요소 추가)
        price_multiplier = 0.9 if random() < 0.2 else 1.0
        
        rows.append(
            {
                "order_id": i,
                "user_id": row.user_id,
                "product_id": row.product_id,
                "order_time": row.event_time,
                "amount": int(row.price * price_multiplier),
                "category": row.category,
            }
        )
        
    return pd.DataFrame(rows)


# 5. 메인 실행
def main() -> None:
    # 데이터 저장 폴더 생성 (data/raw)
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 각 데이터프레임 생성
    users_df = generate_users()
    products_df = generate_products()
    events_df = generate_events(users_df, products_df)
    orders_df = generate_orders(events_df, products_df)
    
    # CSV 파일로 저장
    users_df.to_csv(data_dir / "users.csv", index=False)
    products_df.to_csv(data_dir / "products.csv", index=False)
    events_df.to_csv(data_dir / "events.csv", index=False)
    orders_df.to_csv(data_dir / "orders.csv", index=False)
    
    # 결과 요약 출력
    print("Synthetic data generated:")
    print(f"- users: {len(users_df)}")
    print(f"- products: {len(products_df)}")
    print(f"- events: {len(events_df)}")
    print(f"- orders: {len(orders_df)}")
    
    # 날짜 범위 확인 출력
    print("\nDate range:")
    print(f"- events: {events_df['event_time'].min()} ~ {events_df['event_time'].max()}")
    if not orders_df.empty:
        print(f"- orders: {orders_df['order_time'].min()} ~ {orders_df['order_time'].max()}")


if __name__ == "__main__":
    main()