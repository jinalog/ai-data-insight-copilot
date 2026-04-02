"""
duckdb_client.py

목적
    - DuckDB에 대한 조회 전용 접근을 담당

입력
    - DB 경로
    - SQL

출력
    - pandas DataFrame
    - 테이블별 날짜 범위 정보

핵심 로직
    - read-only 연결
    - SQL 실행 후 DataFrame 반환
    - orders / events 날짜 범위 조회
"""

from __future__ import annotations

import duckdb
import pandas as pd


class DuckDBClient:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def query(self, sql: str) -> pd.DataFrame:
        # 읽기 전용으로 DB 연결
        con = duckdb.connect(self.db_path, read_only=True)
        try:
            return con.execute(sql).fetchdf()
        finally:
            con.close()

    def get_date_ranges(self) -> dict[str, tuple[str | None, str | None]]:
        # CLI 등에서 데이터 범위를 보여주기 위한 보조 메서드
        con = duckdb.connect(self.db_path, read_only=True)
        try:
            orders_df = con.execute(
                """
                SELECT
                    MIN(CAST(order_time AS DATE)) AS min_date,
                    MAX(CAST(order_time AS DATE)) AS max_date
                FROM orders
                """
            ).fetchdf()

            events_df = con.execute(
                """
                SELECT
                    MIN(CAST(event_time AS DATE)) AS min_date,
                    MAX(CAST(event_time AS DATE)) AS max_date
                FROM events
                """
            ).fetchdf()

            orders_min = None if pd.isna(orders_df.loc[0, "min_date"]) else str(orders_df.loc[0, "min_date"])
            orders_max = None if pd.isna(orders_df.loc[0, "max_date"]) else str(orders_df.loc[0, "max_date"])

            events_min = None if pd.isna(events_df.loc[0, "min_date"]) else str(events_df.loc[0, "min_date"])
            events_max = None if pd.isna(events_df.loc[0, "max_date"]) else str(events_df.loc[0, "max_date"])

            return {
                "orders": (orders_min, orders_max),
                "events": (events_min, events_max),
            }
        finally:
            con.close()