"""
schemas.py

목적
    - FastAPI 요청/응답 스키마 정의
    - 클라이언트와 서버 간 데이터 계약(contract) 역할 수행

입력
    - QueryRequest
      - question: 사용자 자연어 질문

출력
    - QueryResponse
      - query_type, sql, preview, summary 등 전체 분석 결과

핵심 로직
    - Pydantic BaseModel 기반 요청/응답 형식 정의
    - FastAPI 문서 자동화 및 검증 지원

설계 의도
    - 단순 답변뿐 아니라 plan/retrieval/validation/evaluation까지 노출하여
      설명 가능하고 디버깅 가능한 분석 시스템으로 구성
"""

from __future__ import annotations

from pydantic import BaseModel


class QueryRequest(BaseModel):
    # 사용자 입력 요청 모델
    question: str


class QueryResponse(BaseModel):
    # API 응답 모델
    question: str                # 원본 질문
    query_type: str              # planner가 판단한 질의 유형
    plan_context: str            # planner가 만든 힌트 문자열
    retrieved_context: str       # retrieval로 찾은 SQL 예시/보강 컨텍스트
    sql: str                     # 최종 생성 SQL
    validation_reason: str       # validator 결과
    preview: str                 # 결과 미리보기 CSV
    row_count: int               # 결과 행 수
    insight_context: str         # 구조화 인사이트 문자열
    summary: str                 # 최종 한국어 요약
    evaluation_summary: str      # 평가 요약
    evaluation_path: str         # 저장된 평가 로그 파일 경로