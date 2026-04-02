"""
sql_normalizer.py

목적
    - LLM이 생성한 SQL을 DuckDB 실행 전에 가볍게 보정

입력
    - 원본 SQL 문자열

출력
    - 후처리된 SQL 문자열

핵심 로직
    - markdown fence 제거
    - DATE(column) → CAST(column AS DATE)
    - INTERVAL 문법 최소 보정
"""

from __future__ import annotations

import re


class SQLNormalizer:
    """ DuckDB 실행 전 SQL을 가볍게 보정하는 후처리기 """

    def normalize(self, sql: str) -> str:
        normalized = sql.strip()

        normalized = self._remove_markdown_fence(normalized)
        normalized = self._replace_date_function(normalized)
        normalized = self._normalize_interval_syntax(normalized)

        return normalized.strip()

    def _remove_markdown_fence(self, sql: str) -> str:
        # ```sql ... ``` 형태 제거
        sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"^```\s*", "", sql)
        sql = re.sub(r"\s*```$", "", sql)
        return sql.strip()

    def _replace_date_function(self, sql: str) -> str:
        # DuckDB에서 일관된 날짜 변환을 위해 DATE() 대신 CAST 사용
        pattern = re.compile(
            r"\bDATE\s*\(\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\)",
            flags=re.IGNORECASE,
        )
        return pattern.sub(r"CAST(\1 AS DATE)", sql)

    def _normalize_interval_syntax(self, sql: str) -> str:
        # 예: INTERVAL 14 DAY -> INTERVAL '14' DAY
        pattern = re.compile(
            r"INTERVAL\s+(\d+)\s+DAY\b",
            flags=re.IGNORECASE,
        )
        return pattern.sub(r"INTERVAL '\1' DAY", sql)