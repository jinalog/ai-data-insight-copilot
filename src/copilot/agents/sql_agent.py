"""
sql_agent.py

목적
    - 자연어 질문을 DuckDB SQL로 변환하는 LLM 기반 SQL 생성기

입력
    - 사용자 질문
    - 스키마 컨텍스트
    - Retrieval 컨텍스트
    - Planner 컨텍스트

출력
    - SQL 문자열

핵심 로직
    - 강한 규칙을 포함한 프롬프트 구성
    - DuckDB SQL 생성
"""

from __future__ import annotations

import os
from textwrap import dedent

from openai import OpenAI


class SQLAgent:
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate_sql(
        self, 
        question: str, 
        schema_context: str, 
        retrieved_context: str = "", 
        planner_context: str = "",
    ) -> str:
        prompt = dedent(
            f"""
            You are a data analyst assistant.
            Convert the user's question into a valid DuckDB SQL query.

            Rules:
            - Use only the provided tables and columns.
            - Return SQL only.
            - Prefer explicit date filters when needed.
            - If the user asks for a trend, aggregate by date.
            - Do not include markdown fences.
            - Use DuckDB SQL dialect.
            - Use CAST(column AS DATE) when converting timestamp to date.
            - Do NOT use DATE(column).
            - Use CURRENT_DATE for relative date filtering.
            - For "purchase count", use COUNT(*) from orders unless stated otherwise.
            - If the user asks for a trend, group by CAST(timestamp_column AS DATE).
            - Do not ignore explicit table requests in the user question.
            - If the user mentions a table that does not exist in the schema, do not substitute another table silently.
            - If the user asks date aggregation, the SQL must include CAST(... AS DATE), GROUP BY, and ORDER BY.
            - If the request cannot be satisfied with the provided schema, still return the best possible SQL grounded only in the schema and follow validation feedback.

            Schema information:
            {schema_context}
            
            Planner guidance:
            {planner_context}
            
            Helpful SQL examples and validation feedback:
            {retrieved_context}       

            User question:
            {question}
            """
        ).strip()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text.strip()