"""
insight_engine.py

목적
    - SQL 조회 결과를 구조화된 수치 인사이트로 변환

입력
    - pandas DataFrame

출력
    - InsightResult(row_count, columns, numeric_columns, summary_text)

핵심 로직
    - 행 수, 컬럼 목록, 숫자 컬럼 추출
    - 숫자 컬럼에 대해 min/max/mean 계산
    - 첫 값/마지막 값 변화량 계산
    - 최대/최소 행 요약
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class InsightResult:
    row_count: int
    columns: list[str]
    numeric_columns: list[str]
    summary_text: str


class InsightEngine:
    def analyze(self, df: pd.DataFrame) -> InsightResult:
        row_count = len(df)
        columns = df.columns.tolist()
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

        # 빈 결과는 별도 처리
        if df.empty:
            return InsightResult(
                row_count=0,
                columns=columns,
                numeric_columns=numeric_columns,
                summary_text="조회 결과가 비어 있습니다.",
            )

        lines: list[str] = []
        lines.append(f"row_count: {row_count}")
        lines.append(f"columns: {columns}")
        lines.append(f"numeric_columns: {numeric_columns}")

        # 숫자 컬럼 최대 3개까지만 요약
        for col in numeric_columns[:3]:
            series = df[col].dropna()
            if series.empty:
                continue

            lines.append(f"[metric: {col}]")
            lines.append(f"- min: {float(series.min()):,.2f}")
            lines.append(f"- max: {float(series.max()):,.2f}")
            lines.append(f"- mean: {float(series.mean()):,.2f}")

            # 첫 값과 마지막 값의 변화량 계산
            if len(series) >= 2:
                first_val = float(series.iloc[0])
                last_val = float(series.iloc[-1])
                diff = last_val - first_val

                if first_val != 0:
                    pct = (diff / first_val) * 100
                    lines.append(f"- first_to_last_change: {diff:,.2f} ({pct:.2f}%)")
                else:
                    lines.append(f"- first_to_last_change: {diff:,.2f}")

                # 최대/최소 값이 발생한 행도 함께 기록
                max_idx = series.idxmax()
                min_idx = series.idxmin()

                max_row = df.loc[max_idx].to_dict()
                min_row = df.loc[min_idx].to_dict()

                lines.append(f"- max_row: {self._safe_dict(max_row)}")
                lines.append(f"- min_row: {self._safe_dict(min_row)}")

        summary_text = "\n".join(lines)

        return InsightResult(
            row_count=row_count,
            columns=columns,
            numeric_columns=numeric_columns,
            summary_text=summary_text,
        )

    def _safe_dict(self, row: dict[str, Any]) -> dict[str, str]:
        # 직렬화 안정성을 위해 모든 값을 문자열로 변환
        return {k: str(v) for k, v in row.items()}