"""
schema_registry.py

목적
    - 스키마 메타데이터와 KPI 메타데이터를 읽어 LLM 프롬프트용 문맥 생성

입력
    - tables.json
    - kpi_definitions.json

출력
    - SQLAgent에 전달할 schema prompt 문자열

핵심 로직
    - 테이블/컬럼/설명 렌더링
    - KPI 정의/SQL 힌트/소스 테이블 렌더링
"""

from __future__ import annotations

import json
from pathlib import Path


class SchemaRegistry:
    def __init__(self, schema_path: str, kpi_path: str) -> None:
        self.schema = self._load_json(schema_path)
        self.kpis = self._load_json(kpi_path)

    @staticmethod
    def _load_json(path: str) -> dict:
        with Path(path).open("r", encoding="utf-8") as f:
            return json.load(f)

    def render_schema_prompt(self) -> str:
        lines: list[str] = []
        lines.append("Available tables:")
        
        # 1) 허용된 테이블과 컬럼 구조 설명
        for table in self.schema["tables"]:
            lines.append(f"- {table['name']}: {table['description']}")
            for col in table["columns"]:
                lines.append(
                    f"  - {col['name']} ({col['type']}): {col['description']}"
                )

        # 2) KPI 정의 추가
        lines.append("\nKPI definitions:")
        for kpi in self.kpis["kpis"]:
            lines.append(
                f"- {kpi['name']}: {kpi['definition']} "
                f"(hint: {kpi['sql_hint']}, source: {kpi['source_table']})"
            )
            
        return "\n".join(lines)