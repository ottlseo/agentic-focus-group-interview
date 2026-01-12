import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from strands import Agent
from strands_tools import file_write

# file_write 확인 프롬프트 비활성화
os.environ['BYPASS_TOOL_CONSENT'] = 'true'
os.environ["DEV"] = "true"

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서 모든 origin 허용
    allow_credentials=False,  # allow_origins=["*"]일 때는 False여야 함
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent
PROMPTS_DIR = PROJECT_ROOT / "src" / "prompts"
PARTICIPANTS_DIR = PROMPTS_DIR / "sample-participants"

def load_prompt(file_path: Path) -> str:
    """프롬프트 파일 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading prompt: {str(e)}"

# 참가자 프로필 로드
def load_participant_profiles():
    """모든 참가자 프로필을 로드"""
    participants = {}

    # sample-participants 디렉토리가 있는지 확인
    if PARTICIPANTS_DIR.exists():
        for file in PARTICIPANTS_DIR.glob("*.md"):
            name = file.stem
            participants[name] = load_prompt(file)
    else:
        # 기본 참가자 프로필 (디렉토리가 없는 경우)
        participants = {
            "yoonseo": "김윤서 (28세 여성, IT 스타트업 UX 디자이너, 1인 가구)",
            "dohyung": "김도형 (32세 남성, 제조업 영업팀 과장, 신혼부부)",
            "jiyeon": "이지연 (37세 여성, 프리랜서 마케팅 컨설턴트, 초등생 자녀 2명)",
            "sukwon": "이석원 (42세 남성, 금융회사 팀장, 4세 딸+맞벌이)",
            "shinchul": "방신철 (26세 남성, 대학원생, 룸메이트와 거주)"
        }

    return participants

PARTICIPANT_PROFILES = load_participant_profiles()
MODERATOR_GUIDE = load_prompt(PROMPTS_DIR / "interview_guide.md") if (PROMPTS_DIR / "interview_guide.md").exists() else "FGI 모더레이터 가이드"

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

# 참가자 에이전트 생성 함수
def get_participant_response(name: str, query: str) -> str:
    """참가자 응답 생성"""
    profile = PARTICIPANT_PROFILES.get(name, f"참가자 {name}")
    display_name = {
        "yoonseo": "윤서",
        "dohyung": "도형",
        "jiyeon": "지연",
        "sukwon": "석원",
        "shinchul": "신철"
    }.get(name, name)

    try:
        agent = Agent(
            system_prompt=create_participant_prompt(profile, display_name),
        )
        response = agent(query)
        return str(response)
    except Exception as e:
        return f"[오류] {str(e)}"

# Moderator 프롬프트
def create_moderator_prompt() -> str:
    return f"""{MODERATOR_GUIDE}

## Available Participants
당신은 다음 참가자들에게 질문할 수 있습니다:
- 윤서 (yoonseo): 28세 여성, IT 스타트업 UX 디자이너, 1인 가구
- 도형 (dohyung): 32세 남성, 제조업 영업팀 과장, 신혼부부
- 지연 (jiyeon): 37세 여성, 프리랜서 마케팅 컨설턴트, 초등생 자녀 2명
- 석원 (sukwon): 42세 남성, 금융회사 팀장, 4세 딸+맞벌이
- 신철 (shinchul): 26세 남성, 대학원생, 룸메이트와 거주

참가자들에게 질문할 때는 직접 응답하지 말고, 시스템이 자동으로 각 참가자의 응답을 수집합니다.
"""

async def fgi_stream():
    """FGI 진행 과정을 SSE로 스트리밍"""

    try:
        # 시작 메시지
        yield f"data: {json.dumps({'type': 'system', 'content': 'FGI 세션을 시작합니다...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)

        # 참가자 소개
        yield f"data: {json.dumps({'type': 'system', 'content': '참가자: 윤서, 도형, 지연, 석원, 신철'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)

        # 모더레이터 인사
        yield f"data: {json.dumps({'type': 'moderator', 'content': '안녕하세요 여러분! 오늘 구독형 밀키트 서비스에 대한 이야기를 나눠보겠습니다. 먼저 간단히 자기소개와 함께 평소 식사 준비는 어떻게 하시는지 말씀해주시겠어요?'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(1)

        # 참가자들 응답
        participants = [
            ("yoonseo", "윤서"),
            ("dohyung", "도형"),
            ("jiyeon", "지연"),
            ("sukwon", "석원"),
            ("shinchul", "신철")
        ]

        question1 = "자기소개와 함께 평소 식사 준비는 어떻게 하시는지 말씀해주세요."

        # 순차적으로 응답 생성 (대화처럼 보이도록)
        for participant_id, participant_name in participants:
            response = get_participant_response(participant_id, question1)
            yield f"data: {json.dumps({'type': 'participant', 'name': participant_name, 'content': response}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1.5)

        # # 병렬 처리 버전 (속도 개선용, 필요시 위 코드와 교체)
        # tasks = [
        #     asyncio.to_thread(get_participant_response, participant_id, question1)
        #     for participant_id, _ in participants
        # ]
        # responses = await asyncio.gather(*tasks)
        # for (participant_id, participant_name), response in zip(participants, responses):
        #     yield f"data: {json.dumps({'type': 'participant', 'name': participant_name, 'content': response}, ensure_ascii=False)}\n\n"
        #     await asyncio.sleep(0.5)

        # 추가 질문
        yield f"data: {json.dumps({'type': 'moderator', 'content': '밀키트를 사용해보신 경험이 있으신가요? 있으시다면 어떠셨는지, 없으시다면 왜 사용하지 않으셨는지 말씀해주세요.'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(1)

        question2 = "밀키트를 사용해보신 경험이 있으신가요? 있으시다면 어떠셨는지, 없으시다면 왜 사용하지 않으셨는지 말씀해주세요."

        # 순차적으로 응답 생성 (대화처럼 보이도록)
        for participant_id, participant_name in participants:
            response = get_participant_response(participant_id, question2)
            yield f"data: {json.dumps({'type': 'participant', 'name': participant_name, 'content': response}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1.5)

        # # 병렬 처리 버전 (속도 개선용, 필요시 위 코드와 교체)
        # tasks = [
        #     asyncio.to_thread(get_participant_response, participant_id, question2)
        #     for participant_id, _ in participants
        # ]
        # responses = await asyncio.gather(*tasks)
        # for (participant_id, participant_name), response in zip(participants, responses):
        #     yield f"data: {json.dumps({'type': 'participant', 'name': participant_name, 'content': response}, ensure_ascii=False)}\n\n"
        #     await asyncio.sleep(0.5)

        # 마무리
        yield f"data: {json.dumps({'type': 'moderator', 'content': '좋은 의견 감사합니다. 오늘 논의된 내용을 바탕으로 더 나은 서비스를 만들어나가겠습니다.'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)

        yield f"data: {json.dumps({'type': 'system', 'content': 'FGI 세션이 종료되었습니다.'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'complete'}, ensure_ascii=False)}\n\n"

    except Exception as e:
        error_msg = f"오류가 발생했습니다: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg}, ensure_ascii=False)}\n\n"

@app.get("/")
async def root():
    return {"message": "FGI Backend API"}

@app.get("/api/fgi/stream")
async def stream_fgi():
    """FGI 스트리밍 엔드포인트"""
    return StreamingResponse(
        fgi_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/fgi/run")
async def run_fgi():
    """FGI 실행 (한 번에 모든 데이터 반환)"""
    messages = []

    async for event in fgi_stream():
        if event.startswith("data: "):
            try:
                data = json.loads(event[6:])
                if data.get('type') != 'complete':
                    messages.append(data)
            except:
                pass

    return {"messages": messages}

@app.get("/api/fgi/demo")
async def demo_fgi():
    """데모 FGI (미리 생성된 빠른 응답)"""
    # 간단한 데모 응답 (5명만)
    demo_messages = []

    demo_messages.append({"type": "system", "content": "FGI 세션을 시작합니다..."})
    await asyncio.sleep(0.3)

    demo_messages.append({"type": "system", "content": "참가자: 윤서, 도형, 지연, 석원, 신철"})
    await asyncio.sleep(0.3)

    demo_messages.append({"type": "moderator", "content": "안녕하세요! 오늘은 구독형 밀키트 서비스에 대해 이야기 나눠보겠습니다. 먼저 평소 식사 준비는 어떻게 하시나요?"})
    await asyncio.sleep(0.5)

    # 각 참가자 응답 (미리 작성된 샘플)
    participants_responses = [
        ("윤서", "저는 혼자 살다 보니 매일 요리하기가 부담스러워요. 주로 배달음식이나 간편식을 많이 먹는 편이에요."),
        ("도형", "신혼이라 아내와 번갈아가며 요리하는데, 레시피 찾고 장보는 게 생각보다 시간이 많이 걸리더라고요."),
        ("지연", "아이 둘 키우면서 매일 영양가 있는 식사 챙기려니 정말 힘들어요. 시간도 없고 메뉴 고민도 크고요."),
        ("석원", "맞벌이라 저녁 늦게 귀가하는 날이 많은데, 그럴 때마다 뭘 해먹을지 고민되더라고요."),
        ("신철", "대학원생이라 시간도 없고 요리 실력도 없어서, 주로 편의점이나 학식으로 때우고 있어요.")
    ]

    for name, response in participants_responses:
        demo_messages.append({"type": "participant", "name": name, "content": response})
        await asyncio.sleep(0.5)

    demo_messages.append({"type": "moderator", "content": "좋은 의견 감사합니다. 밀키트를 사용해보신 경험이 있으신가요?"})
    await asyncio.sleep(0.5)

    responses2 = [
        ("윤서", "네, 몇 번 써봤는데 재료가 딱 필요한 만큼만 와서 좋더라고요. 낭비가 없어요."),
        ("도형", "저도 써봤는데, 레시피대로 하면 실패 없이 만들 수 있어서 좋았어요."),
        ("지연", "가격이 좀 부담되긴 하지만, 시간 절약을 생각하면 나쁘지 않은 것 같아요."),
        ("석원", "아직 안 써봤는데, 구독형이면 매주 정기적으로 오는 건가요? 궁금하네요."),
        ("신철", "가격 때문에 망설여지네요. 학생 입장에서는 부담스러울 것 같아서요.")
    ]

    for name, response in responses2:
        demo_messages.append({"type": "participant", "name": name, "content": response})
        await asyncio.sleep(0.5)

    demo_messages.append({"type": "system", "content": "FGI 세션이 종료되었습니다."})

    return {"messages": demo_messages}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
