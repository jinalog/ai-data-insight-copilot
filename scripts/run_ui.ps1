# run_ui.ps1

<#
목적
    - Streamlit 기반 UI 실행 스크립트

기능
    - 자연어 질문 → SQL → 결과 → 인사이트 UI 제공

전제 조건
    - FastAPI 서버가 먼저 실행되어 있어야 함
      (기본: http://127.0.0.1:8000)

사용 방법
    1. API 실행
        PS> ./run_api.ps1

    2. UI 실행
        PS> ./run_ui.ps1
#>

# src 경로를 Python import path로 설정
$env:PYTHONPATH="src"

# Streamlit UI 실행
python -m streamlit run src/copilot/interfaces/web/streamlit_app.py