"""
app.py

목적
    - AI Data Insight Copilot의 FastAPI 서버 진입점
    - 자연어 질문을 받아 오케스트레이터 실행 후 JSON 응답 반환

입력
    - POST /query
      - question: 사용자 자연어 질문

출력
    - QueryResponse 형식의 JSON 응답
    - GET /health 상태 확인 응답

핵심 로직
    - 환경변수 로드
    - Orchestrator 초기화
    - 요청 유효성 검사
    - 오케스트레이터 실행
    - 결과를 API 응답 모델로 변환

한계 / 향후 개선
    - 현재는 예외를 일괄 500으로 처리
    - LLM/DB/Validation 오류를 세분화한 에러 핸들링 가능
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from copilot.pipeline.orchestrator import Orchestrator
from copilot.interfaces.api.schemas import QueryRequest, QueryResponse

# .env 파일에서 OPENAI_API_KEY 등 환경변수 로드
load_dotenv()

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="AI Data Insight Copilot API",
    version="0.1.0",
)

# 애플리케이션 시작 시 오케스트레이터 1회 초기화
# - DuckDB 경로
# - 스키마 메타데이터
# - KPI 메타데이터
# - SQL 예시 메타데이터를 주입
orchestrator = Orchestrator(
    db_path="data/processed/insight.duckdb",
    schema_path="metadata/schema/tables.json",
    kpi_path="metadata/business/kpi_definitions.json",
    sql_examples_path="metadata/business/sql_examples.json",
)


@app.get("/health")
def health() -> dict[str, str]:
    """
    헬스체크 엔드포인트
    - 서버 프로세스가 살아있는지 확인하는 용도
    """
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    """
    질의 엔드포인트
    - 사용자 질문을 받아 오케스트레이터 실행
    - 최종 결과를 QueryResponse로 변환해 반환
    """
    question = request.question.strip()

    # 빈 질문 방지
    if not question:
        raise HTTPException(status_code=400, detail="질문을 입력해주세요.")

    # 너무 짧은 질문 방지
    if len(question) < 3:
        raise HTTPException(status_code=400, detail="질문이 너무 짧습니다.")

    try:
        # 코어 파이프라인 실행
        result = orchestrator.run(question)

        # 내부 결과 객체를 API 응답 모델로 매핑
        return QueryResponse(
            question=result.question,
            query_type=result.query_type,
            plan_context=result.plan_context,
            retrieved_context=result.retrieved_context,
            sql=result.sql,
            validation_reason=result.validation_reason,
            preview=result.preview,
            row_count=result.row_count,
            insight_context=result.insight_context,
            summary=result.summary,
            evaluation_summary=result.evaluation_summary,
            evaluation_path=result.evaluation_path,
        )
    except Exception as e:
        # 현재는 단순하게 500으로 래핑
        raise HTTPException(status_code=500, detail=str(e))