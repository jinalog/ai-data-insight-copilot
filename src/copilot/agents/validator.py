"""
validator.py

목적
    - 생성된 SQL이 안전하고 질문 의도에 맞는지 검증

입력
    - SQL
    - 사용자 질문
    - 요청 테이블
    - 날짜 집계 요구 여부

출력
    - ValidationResult(is_valid, reason)

핵심 로직
    - SELECT/ WITH만 허용
    - 금지 키워드 차단
    - 허용 테이블만 사용
    - 질문 수준 검증(날짜 집계, 매출 계산 등)
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    reason: str


class SQLValidator:
    # 쓰기/DDL/위험 키워드 차단
    FORBIDDEN_KEYWORDS = {
        "insert", "update", "delete", "drop", "alter", "truncate",
        "create", "replace", "merge", "grant", "revoke", "attach",
        "copy", "export", "call",
    }
    
    # 현재 프로젝트에서 허용하는 테이블/뷰
    ALLOWED_TABLES = {
        "users",
        "products",
        "events",
        "orders",
        "mart_daily_revenue",
        "mart_funnel_daily",
    }

    def validate(self, sql: str) -> ValidationResult:
        normalized = self._normalize(sql)

        if not normalized:
            return ValidationResult(False, "SQL이 비어 있습니다.")

        if self._has_multiple_statements(sql):
            return ValidationResult(False, "여러 SQL 문장을 한 번에 실행할 수 없습니다.")

        if not self._starts_with_allowed_statement(normalized):
            return ValidationResult(False, "SELECT 또는 WITH로 시작하는 조회 쿼리만 허용됩니다.")

        forbidden = self._find_forbidden_keyword(normalized)
        if forbidden:
            return ValidationResult(False, f"허용되지 않은 키워드가 포함되어 있습니다: {forbidden}")

        tables = self._extract_table_names(normalized)
        disallowed = [t for t in tables if t not in self.ALLOWED_TABLES]
        if disallowed:
            return ValidationResult(
                False,
                f"허용되지 않은 테이블(또는 뷰)을 참조하고 있습니다: {', '.join(sorted(set(disallowed)))}",
            )

        return ValidationResult(True, "OK")

    def validate_against_question(
        self,
        question: str,
        sql: str,
        requested_tables: list[str] | None = None,
        requires_date_aggregation: bool = False,
    ) -> ValidationResult:
        # 1차: SQL 자체 안전성 검증
        base = self.validate(sql)
        if not base.is_valid:
            return base

        normalized_sql = self._normalize(sql)
        used_tables = self._extract_table_names(normalized_sql)
        q = question.lower().strip()

        # 명시적으로 '없는 테이블'을 언급한 경우
        if "없는 테이블" in q:
            return ValidationResult(
                False,
                "질문에 '없는 테이블'이 포함되어 있습니다. 존재하는 테이블만 사용하도록 사용자에게 재질문하거나 실패로 처리해야 합니다.",
            )

        # 사용자가 특정 테이블을 요청했으면 실제 SQL에 반영되었는지 확인
        if requested_tables:
            missing_tables = [t for t in requested_tables if t not in used_tables]
            if missing_tables:
                return ValidationResult(
                    False,
                    f"질문에서 요청한 테이블이 SQL에 반영되지 않았습니다: {', '.join(missing_tables)}",
                )

        # 날짜 집계 요구 시 CAST/GROUP BY/ORDER BY 확인
        if requires_date_aggregation:
            has_group_by = "group by" in normalized_sql
            has_cast_date = "cast(" in normalized_sql and " as date)" in normalized_sql
            has_order_by = "order by" in normalized_sql

            if not has_cast_date:
                return ValidationResult(
                    False,
                    "질문이 날짜 집계를 요구하지만 CAST(timestamp_column AS DATE)가 없습니다.",
                )
            if not has_group_by:
                return ValidationResult(
                    False,
                    "질문이 날짜 집계를 요구하지만 GROUP BY가 없습니다.",
                )
            if not has_order_by:
                return ValidationResult(
                    False,
                    "질문이 날짜 집계를 요구하지만 ORDER BY가 없습니다.",
                )

        # 질문이 매출이면 최소한 SUM(amount) 또는 revenue가 있어야 함
        if "매출" in q and "sum(amount)" not in normalized_sql and "revenue" not in normalized_sql:
            return ValidationResult(
                False,
                "질문이 매출을 요구하지만 SUM(amount) 또는 revenue 계산이 없습니다.",
            )

        return ValidationResult(True, "OK")

    @staticmethod
    def _normalize(sql: str) -> str:
        sql = sql.strip()
        sql = re.sub(r"\s+", " ", sql)
        return sql.lower()

    @staticmethod
    def _has_multiple_statements(sql: str) -> bool:
        stripped = sql.strip()
        if not stripped:
            return False
        semicolon_count = stripped.count(";")
        if semicolon_count == 0:
            return False
        if semicolon_count == 1 and stripped.endswith(";"):
            return False
        return True

    @staticmethod
    def _starts_with_allowed_statement(normalized_sql: str) -> bool:
        return normalized_sql.startswith("select ") or normalized_sql.startswith("with ")

    def _find_forbidden_keyword(self, normalized_sql: str) -> str | None:
        for keyword in self.FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{re.escape(keyword)}\b", normalized_sql):
                return keyword
        return None

    @staticmethod
    def _extract_table_names(normalized_sql: str) -> set[str]:
        patterns = [
            r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        ]
        found: set[str] = set()
        for pattern in patterns:
            matches = re.findall(pattern, normalized_sql, flags=re.IGNORECASE)
            found.update(m.lower() for m in matches)
        return found