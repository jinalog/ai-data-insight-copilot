"""
analyst.py

목적
    - 조회 결과와 구조화 인사이트를 바탕으로 최종 한국어 비즈니스 요약 생성

입력
    - 사용자 질문
    - 결과 CSV 미리보기
    - 구조화 인사이트 문자열

출력
    - 한국어 자연어 요약

핵심 로직
    - 결과 데이터와 인사이트를 grounding으로 사용
    - 비즈니스 의미 중심으로 간결하게 요약
"""

from __future__ import annotations

import os
from textwrap import dedent

from openai import OpenAI


class Analyst:
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def summarize(self, question: str, result_csv: str, insight_context: str = "") -> str:
        prompt = dedent(
            f"""
            You are an AI insight analyst.
            Summarize the query result for a business user.

            Requirements:
            - Answer in Korean.
            - Focus on business implications.
            - Keep it concise.
            - If trend exists, mention increase/decrease.
            - Do not invent facts beyond the data.
            - If structured insight context is provided, use it as grounding.

            User question:
            {question}
            
            Structured insight context:
            {insight_context}

            Query result (CSV):
            {result_csv}
            """
        ).strip()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text.strip()