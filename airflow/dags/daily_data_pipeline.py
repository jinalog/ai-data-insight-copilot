"""
daily_data_pipeline.py

목적
    - Airflow DAG을 통해 ETL 파이프라인 실행
    - 데이터 생성 → 품질 검증 → DuckDB 적재 순으로 수행

구성
    1. generate_synthetic_data
    2. data_quality_check
    3. build_duckdb

핵심 특징
    - BashOperator 기반 실행
    - 각 단계는 Python 스크립트를 직접 호출
    - 순차 의존성으로 안정적인 파이프라인 구성

중요 (경로 관련)
    - Airflow 컨테이너의 기본 working directory는 /opt/airflow
    - 따라서 반드시 cd /opt/project 로 이동 후 실행해야 함
    - docker-compose에서 아래처럼 마운트 되어 있어야 정상 동작:
        - ./:/opt/project

    → 이 cd가 없으면 scripts 경로 못 찾아서 실패함
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


# -----------------------------
# DAG 기본 설정
# -----------------------------
default_args = {
    "owner": "jina",  # DAG 소유자 (UI 표시용)
}


# -----------------------------
# DAG 정의
# -----------------------------
with DAG(
    dag_id="daily_data_pipeline",  # DAG 이름 (Airflow UI에 표시됨)
    default_args=default_args,
    description="Generate synthetic data and build DuckDB mart",

    # DAG 시작 기준 날짜
    # 과거 날짜로 설정하면 catchup=True일 때 과거 DAG 실행됨
    start_date=datetime(2026, 3, 1),

    # 실행 주기 (매일)
    schedule="@daily",

    # 과거 실행 방지
    catchup=False,

    # Airflow UI에서 필터링용 태그
    tags=["duckdb", "etl", "copilot"],
) as dag:

    # -----------------------------
    # Step 1: 데이터 생성
    # -----------------------------
    generate_synthetic_data = BashOperator(
        task_id="generate_synthetic_data",

        # 중요:
        # - /opt/project로 이동 후 실행해야 scripts 경로 정상 동작
        # - 절대경로 사용으로 경로 문제 방지
        bash_command="cd /opt/project && python /opt/project/scripts/generate_synthetic_data.py",

        # 환경변수 (.env 등) 전달
        append_env=True,
    )
    

    # -----------------------------
    # Step 2: 데이터 품질 검증
    # -----------------------------
    data_quality_check = BashOperator(
        task_id="data_quality_check",

        # 데이터 검증 스크립트 실행
        # - null 체크
        # - 이벤트 타입 검증
        # - 값 범위 검증
        bash_command="cd /opt/project && python /opt/project/scripts/data_quality_check.py",

        append_env=True,
    )


    # -----------------------------
    # Step 3: DuckDB 적재 및 마트 생성
    # -----------------------------
    build_duckdb = BashOperator(
        task_id="build_duckdb",

        # CSV → DuckDB 테이블 생성
        # mart_daily_revenue / mart_funnel_daily 생성
        bash_command="cd /opt/project && python /opt/project/scripts/build_duckdb.py",

        append_env=True,
    )


    # -----------------------------
    # Task 실행 순서 정의
    # -----------------------------
    # generate → validation → build 순서
    # upstream 실패 시 downstream 실행 안 됨
    generate_synthetic_data >> data_quality_check >> build_duckdb