# ===========================================================================
# [AI 사용 주석]
#  - AI 종류     : Claude (Anthropic, Claude Opus 5.5)
#  - 사용 목적   : main.py 를 실행 진입점으로 만드는 방향과 구간별 힌트 주석 받기
#                  → 실행 코드는 힌트를 보고 본인이 직접 작성
#  - 사용 프롬프트 : "main.py에 주석 달아서 구간별 작성할 코드 간략하게 알려줘"
#                    (선배 조언: "구현은 가능하면 폴더에 있는 main.py로 해보라")
#  - 사용한 사람 : 권순욱 (202611814)
#  - 날짜        : 2026-11-23
# ===========================================================================
"""프로그램 실행 진입점. 모듈2 기간에는 콘솔(TUI), 모듈3에서 GUI 로 교체한다."""

#from modules.health_gui import HealthGUI
# ↑ 모듈3(GUI) 때 다시 쓸 줄. 지금은 HealthGUI 가 없어서 주석 처리해 둠

from modules.health_logic import main as run_tui
# [1] import
#  - modules 패키지의 health_logic 에서 main 함수를 가져온다
#  - 이 파일에서도 main 이라는 이름을 쓸 수 있으니 as 로 별명을 붙이기 (예: run_tui)
#  - 'modules.' 으로 시작하는 이유: main.py 기준으로 modules 폴더가 패키지(__init__.py)이기 때문

if __name__ == "__main__":
    run_tui()
# [2] 실행
#  - if __name__ == "__main__": 블록 안에서 [1] 에서 가져온 함수를 호출
#  - 이 블록이 있어야 나중에 다른 파일이 main.py 를 import 해도 프로그램이 저절로 실행되지 않음
