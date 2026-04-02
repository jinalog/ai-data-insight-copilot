"""
streamlit_app.py

목적
    - AI Data Insight Copilot의 사용자 웹 인터페이스 제공
    - 자연어 질문 입력 → FastAPI 호출 → 결과 시각화

입력
    - 사용자 질문
    - FastAPI 주소

출력
    - 요약
    - 생성 SQL
    - 결과 미리보기 테이블
    - 플래너/검색/검증 등 디버그 정보
    - 평가 결과

핵심 로직
    - Streamlit 화면 구성
    - FastAPI /query 호출
    - 응답 결과를 탭 형태로 렌더링

설계 의도
    - 단순 데모가 아니라 SQL/디버그/평가까지 보여주는 운영자용 UI 성격 포함
"""

from __future__ import annotations

from io import StringIO

import pandas as pd
import requests
import streamlit as st


# 기본 API 엔드포인트
API_URL = "http://127.0.0.1:8000/query"


def render_preview_table(preview_csv: str) -> None:
    """
    CSV 문자열을 표 형태로 렌더링
    - 비어 있으면 안내 문구 출력
    - CSV 파싱 실패 시 원문 텍스트 그대로 표시
    """
    if not preview_csv.strip():
        st.info("조회 결과가 없습니다.")
        return

    try:
        df = pd.read_csv(StringIO(preview_csv))
        st.dataframe(df, use_container_width=True)
    except Exception:
        st.code(preview_csv, language="text")


def main() -> None:
    # Streamlit 페이지 설정
    st.set_page_config(
        page_title="AI Data Insight Copilot",
        page_icon="📊",
        layout="wide",
    )

    # 상단 제목/설명
    st.title("AI Data Insight Copilot")
    st.caption("자연어 질문 → SQL 생성 → 데이터 조회 → 인사이트 요약")

    # 사이드바 설정 영역
    with st.sidebar:
        st.subheader("설정")
        api_url = st.text_input("FastAPI 주소", value=API_URL)
        st.markdown("---")
        st.markdown("### 예시 질문")
        st.markdown("- 최근 7일 매출 추이")
        st.markdown("- 카테고리별 매출 상위 5개")
        st.markdown("- 최근 14일 구매 건수 추이")
        st.markdown("- 최근 30일 카테고리별 매출 합계")

    # 질문 입력창
    question = st.text_area(
        "질문 입력",
        placeholder="예: 최근 7일 매출 추이",
        height=120,
    )

    # 실행 / 초기화 버튼
    col1, col2 = st.columns([1, 5])
    with col1:
        run_button = st.button("실행", use_container_width=True)
    with col2:
        clear_button = st.button("초기화", use_container_width=True)

    # 초기화 버튼 클릭 시 화면 리로드
    if clear_button:
        st.rerun()

    if run_button:
        question = question.strip()

        # 입력 검증
        if not question:
            st.warning("질문을 입력해주세요.")
            st.stop()

        if len(question) < 3:
            st.warning("질문이 너무 짧습니다.")
            st.stop()

        # API 호출
        with st.spinner("질문을 분석하고 있습니다..."):
            try:
                response = requests.post(
                    api_url,
                    json={"question": question},
                    timeout=120,
                )
            except requests.RequestException as e:
                st.error(f"API 호출 실패: {e}")
                st.stop()

        # API 응답 실패 처리
        if response.status_code != 200:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            st.error(f"요청 실패 ({response.status_code}): {detail}")
            st.stop()

        # JSON 응답 파싱
        result = response.json()

        st.success("분석 완료")

        # 결과 탭 구성
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["요약", "SQL", "결과 미리보기", "디버그 정보", "평가"]
        )

        # 1) 최종 요약
        with tab1:
            st.subheader("최종 요약")
            st.write(result["summary"])

            st.markdown("---")
            st.subheader("구조화 인사이트")
            st.code(result["insight_context"], language="text")

        # 2) 생성 SQL
        with tab2:
            st.subheader("생성 SQL")
            st.code(result["sql"], language="sql")

        # 3) 결과 테이블 미리보기
        with tab3:
            st.subheader("결과 미리보기")
            render_preview_table(result["preview"])
            st.caption(f"행 수: {result['row_count']}")

        # 4) 디버그 정보
        with tab4:
            st.subheader("플래너 결과")
            st.code(result["plan_context"], language="text")

            st.subheader("검색된 컨텍스트")
            if result["retrieved_context"].strip():
                st.code(result["retrieved_context"], language="text")
            else:
                st.info("검색된 컨텍스트가 없습니다.")

            st.subheader("검증 결과")
            st.write(result["validation_reason"])

            st.subheader("Query Type")
            st.write(result["query_type"])

        # 5) 평가 결과
        with tab5:
            st.subheader("평가 결과")
            st.write(result["evaluation_summary"])

            st.subheader("평가 로그 파일")
            st.code(result["evaluation_path"], language="text")


if __name__ == "__main__":
    main()