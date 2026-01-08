import os
from pathlib import Path
from strands import Agent
from strands_tools import file_write
import glob as glob_module

# file_write 확인 프롬프트 비활성화
os.environ['BYPASS_TOOL_CONSENT'] = 'true'

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent
PROMPTS_DIR = PROJECT_ROOT / "src" / "prompts"

def load_prompt(file_path: Path) -> str:
    """프롬프트 파일 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading prompt: {str(e)}"

def find_fgi_results() -> list:
    """FGI 결과 파일들 찾기"""
    pattern = str(PROJECT_ROOT / "fgi_results_*.md")
    files = glob_module.glob(pattern)
    return sorted(files)

def read_fgi_results(files: list) -> str:
    """FGI 결과 파일들을 읽어서 하나의 문자열로 반환"""
    content = ""
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content += f"\n\n{'='*80}\n"
                content += f"파일: {Path(file_path).name}\n"
                content += f"{'='*80}\n\n"
                content += f.read()
        except Exception as e:
            content += f"\n[Error reading {file_path}: {str(e)}]\n"
    return content

def create_analyzer_prompt(fgi_content: str) -> str:
    """Analyzer 시스템 프롬프트 생성"""
    analyzer_guide = load_prompt(PROMPTS_DIR / "analyzer.md")
    
    return f"""{analyzer_guide}

## FGI 결과 데이터

아래는 방금 완료된 FGI의 모든 결과입니다. 이 데이터를 분석하여 리포트를 생성하세요.

{fgi_content}

## 작업 지시

위 FGI 결과를 분석하여 다음 3개의 파일을 생성하세요:

1. **executive_summary.html** - 경영진용 HTML 리포트
   - 완전한 HTML 구조 (<!DOCTYPE html>부터 시작)
   - 인라인 CSS 스타일 포함
   - 표, 색상 코드로 시각화
   - 프린트 가능한 형식
   - 1-2페이지 분량

2. **quantified_insights.json** - 정량화된 데이터
   - 모든 지표를 JSON 형식으로
   - 구독 의향, 가격 민감도, Pain Point, 기능 중요도 등

3. **priority_matrix.md** - 실행 우선순위 매트릭스
   - P0/P1/P2 우선순위별 분류
   - 표 형식으로 깔끔하게 정리

각 파일은 file_write 도구를 사용하여 생성하세요.
파일명은 정확히 위에 명시된 이름을 사용하세요.

지금 시작하세요!
"""

if __name__ == "__main__":
    print("=" * 80)
    print("📊 FGI Results Analyzer 시작")
    print("=" * 80)
    print()

    # FGI 결과 파일 찾기
    print("🔍 FGI 결과 파일 검색 중...")
    fgi_files = find_fgi_results()
    
    if not fgi_files:
        print("❌ FGI 결과 파일을 찾을 수 없습니다.")
        print("   먼저 src/graph/interview.py를 실행하여 FGI를 진행하세요.")
        exit(1)
    
    print(f"✅ {len(fgi_files)}개 파일 발견:")
    for f in fgi_files:
        print(f"   - {Path(f).name}")
    print()

    # FGI 결과 읽기
    print("📖 FGI 결과 읽는 중...")
    fgi_content = read_fgi_results(fgi_files)
    print(f"✅ 총 {len(fgi_content)} 문자 로드됨")
    print()

    # Analyzer Agent 생성
    print("🤖 Analyzer Agent 초기화 중...")
    analyzer = Agent(
        system_prompt=create_analyzer_prompt(fgi_content),
        tools=[file_write],
    )
    print("✅ Agent 준비 완료")
    print()

    # 개발 모드 활성화
    os.environ["DEV"] = "true"

    # 분석 시작
    print("=" * 80)
    print("🔬 분석 시작...")
    print("=" * 80)
    print()

    query = """
FGI 결과 분석을 시작하세요.

위에 제공된 모든 FGI 데이터를 읽고 분석하여:
1. executive_summary.html (경영진용 HTML 리포트)
2. quantified_insights.json (정량화 데이터)
3. priority_matrix.md (우선순위 매트릭스)

3개의 파일을 생성해주세요.

HTML 리포트는 반드시:
- 완전한 HTML 문서 구조
- 인라인 CSS 스타일 포함
- 테이블과 색상으로 시각화
- 깔끔하고 전문적인 디자인

각 파일 생성 시 진행 상황을 알려주세요.
"""

    # Agent 실행
    response = analyzer(query)

    print()
    print("=" * 80)
    print("✅ 분석 완료!")
    print("=" * 80)
    print()
    print("📄 생성된 파일:")
    print("   - executive_summary.html (브라우저에서 열어보세요)")
    print("   - quantified_insights.json")
    print("   - priority_matrix.md")
    print()
    print(f"💬 Analyzer 메시지:")
    print(f"{response}")
    print()
