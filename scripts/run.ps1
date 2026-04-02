<#
목적
    - CLI 기반 Copilot 실행 스크립트
    - Python 모듈 실행 전 PYTHONPATH 설정

기능
    - src 디렉토리를 Python import 경로로 추가
    - copilot.main 모듈 실행

왜 필요한가
    - 프로젝트가 src 구조이기 때문에
      기본 상태에서는 import 오류 발생 가능

사용 방법
    PS> ./run.ps1
#>

# src를 PYTHONPATH로 설정 (모듈 import 가능하게)
$env:PYTHONPATH="src"

# CLI 엔트리 실행
python -m copilot.main