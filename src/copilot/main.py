"""
main.py

목적
    - AI Data Insight Copilot의 CLI 실행 진입점
    - 사용자가 자연어 질문을 입력하면 전체 파이프라인 실행

실행 흐름
    1. 환경변수 로드 (.env)
    2. Orchestrator 초기화
    3. DuckDB 데이터 범위 출력
    4. 사용자 입력 루프
    5. 질문 → SQL → 결과 → 인사이트 → 평가 출력

특징
    - 디버깅용으로 모든 중간 결과 출력
    - 개발/로컬 테스트에 최적화된 인터페이스
"""

from __future__ import annotations

from dotenv import load_dotenv

from copilot.datastore.duckdb_client import DuckDBClient
from copilot.pipeline.orchestrator import Orchestrator


def main() -> None:
    # .env 파일에서 OPENAI_API_KEY 등 환경변수 로드
    load_dotenv()
    
    # DuckDB 파일 경로
    db_path = "data/processed/insight.duckdb"

    # 핵심 파이프라인 오케스트레이터 초기화
    app = Orchestrator(
        db_path=db_path,
        schema_path="metadata/schema/tables.json",
        kpi_path="metadata/business/kpi_definitions.json",
        sql_examples_path="metadata/business/sql_examples.json",
    )
    
    # DB 클라이언트 생성 (데이터 범위 확인용)
    db_client = DuckDBClient(db_path)
    
    # orders / events 테이블 날짜 범위 조회
    date_ranges = db_client.get_date_ranges()

    print("AI Data Insight Copilot")
    print("종료하려면 exit 입력\n")
    
    # 데이터 범위 출력 (사용자 참고용)
    print("[데이터 범위]")
    for table_name, (min_date, max_date) in date_ranges.items():
        print(f"{table_name:<7}: {min_date} ~ {max_date}")
    print()

    # 사용자 입력 루프
    while True:
        question = input("질문 > ").strip()
        
        # 빈 입력 방지
        if question == "":
            print("질문을 입력해주세요.\n")
            continue
        
        # 종료 조건
        if question.lower() in {"exit", "quit"}:
            break
        
        # 너무 짧은 질문 방지
        if len(question) < 3:
            print("질문이 너무 짧습니다.\n")
            continue

        try:
            # 전체 파이프라인 실행
            result = app.run(question)

            # -----------------------------
            # 디버그 + 결과 출력
            # -----------------------------
            print("\n[플래너 결과]")
            print(result.plan_context)
            
            print("\n[생성 SQL]")
            print(result.sql)

            print("\n[검증 결과]")
            print(result.validation_reason)

            print("\n[미리보기]")
            print(result.preview if result.preview.strip() else "(조회 결과 없음)")
            
            print("\n[구조화 인사이트]")
            print(result.insight_context)

            print("\n[요약]")
            print(result.summary)
            
            print("\n[평가 결과]")
            print(result.evaluation_summary)

            print("\n[평가 로그 파일]")
            print(result.evaluation_path)
            
            print(f"\n[행 수] {result.row_count}\n")

        except Exception as e:
            # 전체 파이프라인 에러 처리
            print(f"\n오류 발생: {e}\n")


if __name__ == "__main__":
    main()