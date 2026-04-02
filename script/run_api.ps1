# run_api.ps1

<#
목적
    - FastAPI 서버 실행 스크립트

기능
    - uvicorn 기반 API 서버 실행
    - 코드 변경 시 자동 reload 지원

핵심 옵션
    --reload
        - 코드 변경 시 서버 자동 재시작

    --reload-dir
        - 감시 대상 디렉토리 지정
        - copilot 내부 코드 변경 시만 reload

주의
    - Windows 환경에서는 절대경로 지정 필요
    - API 실행 후: http://127.0.0.1:8000 접속 가능

사용 방법
    PS> ./run_api.ps1
#>

# src 경로를 Python import path로 설정
$env:PYTHONPATH="src"

# FastAPI 서버 실행
python -m uvicorn copilot.interfaces.api.app:app `
    --reload `
    --reload-dir C:\Users\jina\line\ai-data-insight-copilot\src\copilot