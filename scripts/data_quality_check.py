"""
data_quality_check.py

목적
    - raw 데이터의 기본 품질을 검증하여 ETL 파이프라인의 안정성 확보

입력
    - data/raw/*.csv

출력
    - 없음 (검증 실패 시 AssertionError 발생)

핵심 로직
    - 필수 컬럼 null 여부 검사
    - 허용된 값 범위 검사
    - 기본 수치 데이터 유효성 검사

한계 / 향후 개선
    - 중복 키 검사 없음
    - referential integrity 검사 없음
    - 이상치 탐지 / 패턴 기반 검증 없음
"""


import pandas as pd


# 1. 생성된 데이터 불러오기
users = pd.read_csv("data/raw/users.csv")
products = pd.read_csv("data/raw/products.csv")
events = pd.read_csv("data/raw/events.csv")
orders = pd.read_csv("data/raw/orders.csv")


print("Running Data Quality Checks...")

# 2. 필수 키 null 검사
assert users["user_id"].isnull().sum() == 0
assert products["product_id"].isnull().sum() == 0

# 3. 허용된 이벤트 타입만 존재해야 함
assert events["event_type"].isin(
    ["view", "click", "add_to_cart", "purchase"]
).all()

# 4. 주문 금액은 모두 양수
assert (orders["amount"] > 0).all()

print("Data Quality Check Passed (Basic Checks Only)")