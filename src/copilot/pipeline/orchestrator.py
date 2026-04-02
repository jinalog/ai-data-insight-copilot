"""
orchestrator.py

목적
    - AI Data Insight Copilot의 전체 실행 흐름을 제어하는 중앙 오케스트레이터

입력
    - 사용자 자연어 질문
    - 스키마 메타데이터 경로
    - KPI 메타데이터 경로
    - SQL 예시 메타데이터 경로
    - DuckDB 경로

출력
    - SQL
    - 미리보기 결과
    - 구조화 인사이트
    - 최종 자연어 요약
    - 평가 요약 및 평가 로그 경로

핵심 로직
    - 질문 분석(Planner)
    - 스키마/KPI/예시 SQL 기반 컨텍스트 생성
    - SQL 생성 → 정규화 → 검증
    - 검증 실패 시 피드백 기반 재시도
    - DB 조회 후 인사이트 생성 및 요약
    - 결과 평가 및 저장
"""

from __future__ import annotations

from dataclasses import dataclass

from copilot.agents.analyst import Analyst
from copilot.agents.sql_agent import SQLAgent
from copilot.agents.validator import SQLValidator
from copilot.context.schema_registry import SchemaRegistry
from copilot.datastore.duckdb_client import DuckDBClient
from copilot.retrieval.retriever import ContextRetriever
from copilot.agents.sql_normalizer import SQLNormalizer
from copilot.agents.planner import Planner
from copilot.agents.insight_engine import InsightEngine
from copilot.evaluation.evaluator import Evaluator


@dataclass
class QueryResult:
    # 최종 응답 객체
    question: str
    sql: str
    summary: str
    row_count: int
    preview: str
    validation_reason: str
    retrieved_context: str
    plan_context: str
    query_type: str
    insight_context: str
    evaluation_summary: str
    evaluation_path: str


class Orchestrator:
    def __init__(
        self,
        db_path: str,
        schema_path: str,
        kpi_path: str,
        sql_examples_path: str,
    ) -> None:
        # 실행에 필요한 구성요소를 한 번에 조립
        self.db = DuckDBClient(db_path) # DB 실행 클라이언트
        self.registry = SchemaRegistry(schema_path, kpi_path) # 스키마/KPI 레지스트리
        self.retriever = ContextRetriever(kpi_path, sql_examples_path) # RAG 검색기
        self.planner = Planner() # 질문 의도 분석기
        self.sql_agent = SQLAgent() # SQL 생성 LLM 에이전트
        self.normalizer = SQLNormalizer() # SQL 후처리 정규화기
        self.validator = SQLValidator() # SQL 안전성/의미 검증기
        self.insight_engine = InsightEngine() # 통계 기반 구조화 인사이트 생성기
        self.analyst = Analyst() # 자연어 요약 LLM 에이전트
        self.evaluator = Evaluator() # SQL 품질 평가기

    def run(self, question: str) -> QueryResult:        
        # 1) 스키마 + KPI 문맥 생성
        schema_context = self.registry.render_schema_prompt()
        
        # 2) 질문 분석
        plan = self.planner.plan(question)
        plan_context = self.planner.render_plan_context(plan)
        
        # 3) 유사 SQL 예시 검색 (RAG)
        base_retrieved_context = self.retriever.retrieve(question)
        retrieved_context = base_retrieved_context
        
        # 4) SQL 생성/검증 재시도 설정
        max_retry = 2
        retry_count = 0

        sql = ""
        validation_reason = "UNKNOWN"

        while retry_count <= max_retry:
            # 5) 자연어 → SQL 생성
            raw_sql = self.sql_agent.generate_sql(
                question=question,
                schema_context=schema_context,
                retrieved_context=retrieved_context,
                planner_context=plan_context,
            )
            
            # 6) LLM 출력 후처리
            sql = self.normalizer.normalize(raw_sql)
            
            # 7) SQL 검증
            validation = self.validator.validate_against_question(
                question=question,
                sql=sql,
                requested_tables=plan.requested_tables,
                requires_date_aggregation=plan.requires_date_aggregation,
            )
            validation_reason = validation.reason

            if validation.is_valid:
                break
            
            # 8) 실패 시 검증 피드백을 붙여 재생성
            retry_count += 1
            if retry_count > max_retry:
                raise ValueError(f"SQL 검증 실패: {validation.reason}")

            # 이전 SQL과 실패 사유를 컨텍스트에 덧붙여 LLM이 수정 방향을 인지하도록 함
            retrieved_context = (
                base_retrieved_context
                + "\n\n[VALIDATION FEEDBACK]\n"
                + f"- previous_sql: {sql}\n"
                + f"- validation_error: {validation.reason}\n"
                + "- Rewrite the SQL to satisfy the validator.\n"
                + "- Do not ignore the user's requested table or grouping requirement.\n"
                + "- If the question asks date aggregation, 반드시 CAST(timestamp_column AS DATE), GROUP BY, ORDER BY를 포함하세요.\n"
                + "- If the question mentions a non-existent table, do not silently substitute another table.\n"
            )
            
        # 9) 검증 통과 SQL만 실제 실행
        df = self.db.query(sql)
        
        # 10) 결과 미리보기 생성
        preview_csv = df.head(20).to_csv(index=False)

        # 11) 구조화 인사이트 생성
        insight_result = self.insight_engine.analyze(df)
        insight_context = insight_result.summary_text
        
        # 12) 빈 결과면 고정 문구, 아니면 LLM 요약
        if df.empty:
            summary = "조회 결과가 없습니다. 기간 조건이나 필터를 조정해서 다시 질문해 주세요."
        else:
            summary = self.analyst.summarize(
                question=question,
                result_csv=preview_csv,
                insight_context=insight_context,
            )

        # 13) SQL 품질 평가 및 저장
        evaluation = self.evaluator.evaluate(
            question=question,
            query_type=plan.query_type,
            sql=sql,
            row_count=len(df),
            sql_execution_success=True,
        )

        evaluation_path = self.evaluator.save(evaluation)
        evaluation_summary = (
            f"alignment={evaluation.query_type_alignment}, "
            f"empty_result={evaluation.is_empty_result}, "
            f"row_count={evaluation.row_count}, "
            f"notes={evaluation.notes}"
        )

        # 14) 최종 결과 반환
        return QueryResult(
            question=question,
            sql=sql,
            summary=summary,
            row_count=len(df),
            preview=preview_csv,
            validation_reason=validation_reason,
            retrieved_context=retrieved_context,
            plan_context=plan_context,
            query_type=plan.query_type,
            insight_context=insight_context,
            evaluation_summary=evaluation_summary,
            evaluation_path=evaluation_path,
        )