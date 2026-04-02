"""
evaluator.py

목적
    - 생성된 SQL과 실행 결과를 규칙 기반으로 평가하고 JSON 로그로 저장

입력
    - 질문
    - query_type
    - SQL
    - row_count
    - 실행 성공 여부

출력
    - EvaluationResult
    - 저장된 JSON 파일 경로

핵심 로직
    - query_type과 SQL 구조 정합성 점검
    - group by / order by / limit 유무 확인
    - 결과 비어 있는지 기록
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class EvaluationResult:
    timestamp: str
    question: str
    query_type: str
    sql: str
    sql_execution_success: bool
    is_empty_result: bool
    row_count: int
    has_group_by: bool
    has_order_by: bool
    has_limit: bool
    query_type_alignment: str
    notes: str


class Evaluator:
    def __init__(self, output_dir: str = "outputs/eval_results") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def evaluate(
        self,
        question: str,
        query_type: str,
        sql: str,
        row_count: int,
        sql_execution_success: bool,
    ) -> EvaluationResult:
        normalized_sql = sql.lower()

        has_group_by = "group by" in normalized_sql
        has_order_by = "order by" in normalized_sql
        has_limit = "limit " in normalized_sql
        is_empty_result = row_count == 0

        query_type_alignment, notes = self._check_alignment(
            query_type=query_type,
            sql=normalized_sql,
            has_group_by=has_group_by,
            has_order_by=has_order_by,
            has_limit=has_limit,
        )

        return EvaluationResult(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            question=question,
            query_type=query_type,
            sql=sql,
            sql_execution_success=sql_execution_success,
            is_empty_result=is_empty_result,
            row_count=row_count,
            has_group_by=has_group_by,
            has_order_by=has_order_by,
            has_limit=has_limit,
            query_type_alignment=query_type_alignment,
            notes=notes,
        )

    def save(self, result: EvaluationResult) -> str:
        # 평가 결과를 JSON 파일로 저장
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f.json")
        path = self.output_dir / filename

        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(result), f, ensure_ascii=False, indent=2)

        return str(path)

    def _check_alignment(
        self,
        query_type: str,
        sql: str,
        has_group_by: bool,
        has_order_by: bool,
        has_limit: bool,
    ) -> tuple[str, str]:
        # 질문 유형별로 SQL 구조가 맞는지 간단히 평가
        if query_type == "trend":
            if has_group_by and has_order_by:
                return "good", "trend 유형에 필요한 group by / order by가 포함되어 있습니다."
            return "weak", "trend 유형인데 group by 또는 order by가 부족할 수 있습니다."

        if query_type == "top_n":
            if has_order_by and has_limit:
                return "good", "top_n 유형에 필요한 order by / limit가 포함되어 있습니다."
            return "weak", "top_n 유형인데 order by 또는 limit가 부족할 수 있습니다."

        if query_type == "aggregation":
            if has_group_by or "sum(" in sql or "count(" in sql or "avg(" in sql:
                return "good", "aggregation 유형에 적절한 집계 표현이 포함되어 있습니다."
            return "weak", "aggregation 유형인데 집계 함수가 부족할 수 있습니다."

        if query_type == "rate":
            if "/" in sql or "rate" in sql or "cvr" in sql:
                return "good", "rate 유형으로 보이는 계산식이 포함되어 있습니다."
            return "weak", "rate 유형인데 비율 계산식이 명확하지 않을 수 있습니다."

        return "unknown", "정의되지 않은 query_type입니다."