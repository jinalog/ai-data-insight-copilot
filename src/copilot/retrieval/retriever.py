"""
retriever.py

목적
    - 사용자 질문과 유사한 SQL 예시를 찾아 SQL 생성 품질을 보강

입력
    - KPI 메타데이터 파일
    - SQL 예시 메타데이터 파일
    - 사용자 질문

출력
    - SQLAgent 프롬프트에 넣을 예시 문자열

핵심 로직
    - 질문을 소문자로 정규화
    - sql_examples.json의 question_examples와 단순 패턴 매칭
    - 매칭된 예시 최대 3개 반환
"""

import json

class ContextRetriever:

    def __init__(self, kpi_path: str, sql_examples_path: str):
        # 현재 구현에서는 KPI를 직접 쓰지 않지만, 확장 가능성을 위해 함께 로드
        with open(kpi_path, encoding="utf-8") as f:
            self.kpis = json.load(f)["kpis"]

        with open(sql_examples_path, encoding="utf-8") as f:
            self.examples = json.load(f)["examples"]

    def retrieve(self, question: str) -> str:
        q = question.lower()
        matched_examples = []

        # 질문 문자열에 예시 패턴이 포함되면 해당 SQL 예시를 컨텍스트로 사용
        for example in self.examples:
            for pattern in example["question_examples"]:
                if pattern in q:
                    matched_examples.append(example)
                    break

        context_lines = []

        for ex in matched_examples[:3]:
            context_lines.append(f"Example: {ex['description']}")
            context_lines.append(f"SQL: {ex['sql']}")

        return "\n".join(context_lines)