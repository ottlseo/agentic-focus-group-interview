import os
from pathlib import Path
from strands import Agent, tool
from strands_tools import file_write

# file_write 확인 프롬프트 비활성화
os.environ['BYPASS_TOOL_CONSENT'] = 'true' 

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent
PROMPTS_DIR = PROJECT_ROOT / "src" / "prompts"
PARTICIPANTS_DIR = PROMPTS_DIR / "sample-participants"

def load_prompt(file_path: Path) -> str:
    """프롬프트 파일 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading prompt: {str(e)}"

# 각 참가자 프로필 로드
YOONSEO_PROFILE = load_prompt(PARTICIPANTS_DIR / "yoonseo.md")
DOHYUNG_PROFILE = load_prompt(PARTICIPANTS_DIR / "dohyung.md")
JIYEON_PROFILE = load_prompt(PARTICIPANTS_DIR / "jiyeon.md")
SUKWON_PROFILE = load_prompt(PARTICIPANTS_DIR / "sukwon.md")
SHINCHUL_PROFILE = load_prompt(PARTICIPANTS_DIR / "shinchul.md")
MODERATOR_GUIDE = load_prompt(PROMPTS_DIR / "interview_guide.md")

# 참가자별 시스템 프롬프트 생성
def create_participant_prompt(profile: str, name: str) -> str:
    return f"""당신은 Focus Group Interview에 참여하는 '{name}'입니다.

아래는 당신의 프로필입니다. 이 프로필에 충실하게 답변하세요:

{profile}

## 답변 시 주의사항:
1. **페르소나 유지**: 위 프로필의 성격, 가치관, 생활 방식에 맞게 답변하세요
2. **구체적 답변**: 추상적이지 않고 본인의 실제 경험과 상황을 바탕으로 구체적으로 답변하세요
3. **자연스러운 대화**: 너무 격식을 차리지 말고, 실제 대화처럼 자연스럽게 답변하세요
4. **솔직함**: 긍정적인 면과 부정적인 면을 모두 솔직하게 이야기하세요
5. **길이**: 답변은 2-4문장 정도로 간결하게 (너무 길지 않게)
6. **다른 참가자 의견에 반응**: 다른 참가자의 의견이 언급되면, 동의하거나 다른 관점을 제시할 수 있습니다

답변 예시:
- "저는 퇴근하면 너무 피곤해서 요리할 엄두가 안 나요. 그래서 배달음식을 자주 시키는데, 건강에는 안 좋은 것 같아서 고민이에요."
- "가격이 좀 부담되는 것 같아요. 한 끼에 만원 넘으면 그냥 배달시키는 게 나을 수도 있을 것 같은데..."
"""

@tool
def participant_yoonseo(query: str) -> str:
    """
    참가자 김윤서 (28세 여성, IT 스타트업 UX 디자이너, 1인 가구)

    Args:
        query: moderator가 하는 질문 또는 대화 맥락

    Returns:
        윤서의 페르소나를 적용한 답변
    """
    try:
        print(f"\n💬 [윤서에게 질문]")
        agent = Agent(
            system_prompt=create_participant_prompt(YOONSEO_PROFILE, "김윤서"),
        )
        response = agent(query)
        result = f"{response}"
        print(f"   [윤서] {result}\n")
        return f"[윤서] {result}"
    except Exception as e:
        return f"[윤서 오류] {str(e)}"


@tool
def participant_dohyung(query: str) -> str:
    """
    참가자 김도형 (32세 남성, 제조업 영업팀 과장, 신혼부부)

    Args:
        query: moderator가 하는 질문 또는 대화 맥락

    Returns:
        도형의 페르소나를 적용한 답변
    """
    try:
        print(f"\n💬 [도형에게 질문]")
        agent = Agent(
            system_prompt=create_participant_prompt(DOHYUNG_PROFILE, "김도형"),
        )
        response = agent(query)
        result = f"{response}"
        print(f"   [도형] {result}\n")
        return f"[도형] {result}"
    except Exception as e:
        return f"[도형 오류] {str(e)}"


@tool
def participant_jiyeon(query: str) -> str:
    """
    참가자 이지연 (37세 여성, 프리랜서 마케팅 컨설턴트, 초등생 자녀 2명)

    Args:
        query: moderator가 하는 질문 또는 대화 맥락

    Returns:
        지연의 페르소나를 적용한 답변
    """
    try:
        print(f"\n💬 [지연에게 질문]")
        agent = Agent(
            system_prompt=create_participant_prompt(JIYEON_PROFILE, "이지연"),
        )
        response = agent(query)
        result = f"{response}"
        print(f"   [지연] {result}\n")
        return f"[지연] {result}"
    except Exception as e:
        return f"[지연 오류] {str(e)}"


@tool
def participant_sukwon(query: str) -> str:
    """
    참가자 이석원 (42세 남성, 금융회사 팀장, 4세 딸+맞벌이)

    Args:
        query: moderator가 하는 질문 또는 대화 맥락

    Returns:
        석원의 페르소나를 적용한 답변
    """
    try:
        print(f"\n💬 [석원에게 질문]")
        agent = Agent(
            system_prompt=create_participant_prompt(SUKWON_PROFILE, "이석원"),
        )
        response = agent(query)
        result = f"{response}"
        print(f"   [석원] {result}\n")
        return f"[석원] {result}"
    except Exception as e:
        return f"[석원 오류] {str(e)}"


@tool
def participant_shinchul(query: str) -> str:
    """
    참가자 방신철 (26세 남성, 대학원생, 룸메이트와 거주)

    Args:
        query: moderator가 하는 질문 또는 대화 맥락

    Returns:
        신철의 페르소나를 적용한 답변
    """
    try:
        print(f"\n💬 [신철에게 질문]")
        agent = Agent(
            system_prompt=create_participant_prompt(SHINCHUL_PROFILE, "방신철"),
        )
        response = agent(query)
        result = f"{response}"
        print(f"   [신철] {result}\n")
        return f"[신철] {result}"
    except Exception as e:
        return f"[신철 오류] {str(e)}"


def create_moderator_prompt() -> str:
    """Moderator 시스템 프롬프트 생성"""
    return f"""{MODERATOR_GUIDE}"""

def interview_moderator_node():
    
    # Moderator Agent 생성
    moderator = Agent(
        system_prompt=create_moderator_prompt(),
        tools=[
            participant_yoonseo,
            participant_dohyung,
            participant_jiyeon,
            participant_sukwon,
            participant_shinchul,
            file_write,
        ],
    )

    # 개발 모드 활성화
    os.environ["DEV"] = "true"
    
    # 초기 쿼리: FGI 시작
    initial_query = """
안녕하세요, 모더레이터님. 

이제 구독형 밀키트 서비스에 대한 Focus Group Interview를 시작해주세요.

5명의 참가자(윤서, 도형, 지연, 석원, 신철)가 준비되어 있습니다.

1단계(도입)부터 시작하여, 각 참가자들에게 자기소개와 평소 식생활에 대해 물어보며 
편안한 분위기를 만들어주세요. 

가이드의 7단계를 순차적으로 진행하되, 자연스러운 대화 흐름을 유지하세요.
중요한 인사이트는 중간중간 파일로 저장해주세요.
"""

    print("=" * 80)
    print("🎯 Focus Group Interview 시작")
    print("=" * 80)
    print("\n주제: 구독형 밀키트 서비스")
    print("참가자: 윤서, 도형, 지연, 석원, 신철")
    print("-" * 80)

    # Moderator 실행
    print("\n🎤 [Moderator] FGI를 시작합니다...\n")

    # Agent 실행 (tool 호출 시 자동으로 print가 됨)
    response = moderator(initial_query)

    # Moderator의 최종 메시지 출력
    print(f"\n🎤 [Moderator] {response}\n")

    print("-" * 80)
    print("✅ 첫 세션 완료")
    print("=" * 80)
