import os
from pathlib import Path
from strands import Agent, tool
from strands_tools import file_read, file_write
from src.prompts.template import apply_prompt_template

def product_researcher_node():
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="product_researcher", prompt_context={}),
        tools=[file_write]
    )

def persona_generator_node():
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="persona_generator", prompt_context={}),
        tools=[file_write]
    )

def interview_planner_node():
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="interview_planner", prompt_context={}),
        tools=[file_write]
    )

def analyst_node():
    """FGI 결과를 정성적으로 분석하여 리서치 보고서를 생성하는 노드"""

    # file_write 확인 프롬프트 비활성화
    os.environ['BYPASS_TOOL_CONSENT'] = 'true'

    print("=" * 80)
    print("📊 FGI 정성 분석 시작")
    print("=" * 80)
    print("\n분석 대상: artifacts/interview_results.txt")
    print("출력 파일: artifacts/final_report.md")
    print("-" * 80)

    # Analyst Agent 생성 (file_read와 file_write tool 제공)
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="analyst", prompt_context={}),
        tools=[file_read, file_write]
    )

    # 개발 모드 활성화
    os.environ["DEV"] = "true"

    # 초기 쿼리: FGI 분석 시작
    initial_query = """
안녕하세요, Analyst님.

Focus Group Interview 결과에 대한 정성적 분석을 시작해주세요.

프롬프트에 명시된 대로:
1. artifacts/interview_results.txt 파일을 읽어주세요 (file_read tool 사용)
2. 연구 맥락을 파악하고
3. 주제별 코딩 및 분석을 수행하고
4. 적절한 프레임워크를 적용하여
5. 인사이트를 도출한 후
6. artifacts/final_report.md 파일에 보고서를 작성해주세요 (file_write tool 사용)

전문적인 정성 연구 분석을 부탁드립니다.
"""

    print("\n🔍 [Analyst] 분석을 시작합니다...\n")

    # Agent 실행
    response = agent(initial_query)

    # Analyst의 최종 메시지 출력
    print(f"\n🔍 [Analyst] {response}\n")

    print("-" * 80)
    print("✅ 분석 완료")
    print("📄 보고서 위치: artifacts/final_report.md")
    print("=" * 80)

    return response
