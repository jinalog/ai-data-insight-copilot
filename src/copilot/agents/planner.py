"""
planner.py

목적
    - 사용자 질문을 구조화하여 SQL 생성 전에 분석 방향을 정리

입력
    - 자연어 질문

출력
    - query_type
    - time_grain
    - metric_hint
    - dimension_hint
    - limit_hint
    - analysis_goal
    - requested_tables
    - requires_date_aggregation

핵심 로직
    - 질문 유형 분류
    - 시간 단위 추론
    - 핵심 KPI/차원/Top-N 힌트 추출
"""

from __future__ import annotations

# import re
from dataclasses import dataclass


@dataclass
class PlanResult:
    query_type: str
    time_grain: str
    metric_hint: str
    dimension_hint: str
    limit_hint: int | None
    analysis_goal: str
    requested_tables: list[str]
    requires_date_aggregation: bool


class Planner:
    # 질문에서 직접 언급 가능한 허용 테이블 목록
    ALLOWED_TABLES = {
        "users",
        "products",
        "events",
        "orders",
        "mart_daily_revenue",
        "mart_funnel_daily",
    }

    def plan(self, question: str) -> PlanResult:
        q = question.lower().strip()

        requested_tables = self._extract_requested_tables(q)
        requires_date_aggregation = self._requires_date_aggregation(q)

        query_type = self._detect_query_type(q, requires_date_aggregation)
        time_grain = self._detect_time_grain(q, requires_date_aggregation)
        metric_hint = self._detect_metric_hint(q)
        dimension_hint = self._detect_dimension_hint(q)
        limit_hint = self._detect_limit_hint(q)

        analysis_goal = self._build_analysis_goal(
            query_type=query_type,
            metric_hint=metric_hint,
            dimension_hint=dimension_hint,
            time_grain=time_grain,
            limit_hint=limit_hint,
        )

        return PlanResult(
            query_type=query_type,
            time_grain=time_grain,
            metric_hint=metric_hint,
            dimension_hint=dimension_hint,
            limit_hint=limit_hint,
            analysis_goal=analysis_goal,
            requested_tables=requested_tables,
            requires_date_aggregation=requires_date_aggregation,
        )

    def render_plan_context(self, plan: PlanResult) -> str:
        # SQLAgent에 넘길 플래너 힌트 문자열
        lines = [
            "Planner hints:",
            f"- query_type: {plan.query_type}",
            f"- time_grain: {plan.time_grain}",
            f"- metric_hint: {plan.metric_hint}",
            f"- dimension_hint: {plan.dimension_hint}",
            f"- limit_hint: {plan.limit_hint}",
            f"- analysis_goal: {plan.analysis_goal}",
            f"- requested_tables: {plan.requested_tables}",
            f"- requires_date_aggregation: {plan.requires_date_aggregation}",
        ]
        return "\n".join(lines)

    def _detect_query_type(self, q: str, requires_date_aggregation: bool) -> str:
        if requires_date_aggregation:
            return "trend"
        if any(keyword in q for keyword in ["추이", "trend", "일자별", "시간별"]):
            return "trend"
        if any(keyword in q for keyword in ["top", "상위", "가장 높은", "많은"]):
            return "top_n"
        if any(keyword in q for keyword in ["비교", "compare", "대비"]):
            return "comparison"
        if any(keyword in q for keyword in ["비율", "전환율", "cvr", "rate"]):
            return "rate"
        return "aggregation"

    def _detect_time_grain(self, q: str, requires_date_aggregation: bool) -> str:
        if requires_date_aggregation:
            return "day"
        if any(keyword in q for keyword in ["일자별", "일별", "day", "최근", "지난", "날짜"]):
            return "day"
        if any(keyword in q for keyword in ["주별", "주간", "week"]):
            return "week"
        if any(keyword in q for keyword in ["월별", "월간", "month"]):
            return "month"
        return "none"

    def _detect_metric_hint(self, q: str) -> str:
        if "매출" in q:
            return "revenue"
        if any(keyword in q for keyword in ["구매 건수", "주문 건수", "purchase count", "order count"]):
            return "purchase_count"
        if any(keyword in q for keyword in ["전환율", "cvr", "conversion"]):
            return "conversion_rate"
        return "unknown"

    def _detect_dimension_hint(self, q: str) -> str:
        if "카테고리" in q:
            return "category"
        if "국가" in q:
            return "country"
        if any(keyword in q for keyword in ["디바이스", "device"]):
            return "device_type"
        return "none"

    def _detect_limit_hint(self, q: str) -> int | None:
        if "top 3" in q or "상위 3" in q:
            return 3
        if "top 5" in q or "상위 5" in q:
            return 5
        if "top 10" in q or "상위 10" in q:
            return 10
        return None

    def _extract_requested_tables(self, q: str) -> list[str]:
        # 사용자가 테이블명을 직접 말한 경우 반영
        found = []
        for table in self.ALLOWED_TABLES:
            if table in q:
                found.append(table)
        return sorted(found)

    def _requires_date_aggregation(self, q: str) -> bool:
        keywords = ["date()", "date 함수", "날짜별", "일자별", "일별", "날짜로", "date로", "날짜 집계", "일자 집계"]
        return any(keyword in q for keyword in keywords)

    def _build_analysis_goal(
        self,
        query_type: str,
        metric_hint: str,
        dimension_hint: str,
        time_grain: str,
        limit_hint: int | None,
    ) -> str:
        # 사람이 읽을 수 있는 분석 목표 문장 생성
        parts = [f"Find {metric_hint}"]
        if query_type == "trend":
            parts.append(f"as a {time_grain}-level trend")
        elif query_type == "top_n":
            parts.append("rank the highest values")
        elif query_type == "comparison":
            parts.append("compare between groups")
        elif query_type == "rate":
            parts.append("calculate a rate metric")
        else:
            parts.append("aggregate the result")

        if dimension_hint != "none":
            parts.append(f"by {dimension_hint}")

        if limit_hint is not None:
            parts.append(f"limit result to top {limit_hint}")

        return ", ".join(parts)