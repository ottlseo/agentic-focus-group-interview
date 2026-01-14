import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from strands import Agent, tool
from strands_tools import file_write
import queue
import threading

# file_write 확인 프롬프트 비활성화
os.environ['BYPASS_TOOL_CONSENT'] = 'true'
os.environ["DEV"] = "true"

app = FastAPI()

# 전역 큐 (SSE 스트리밍용)
message_queue = queue.Queue()

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
PARTICIPANTS_DIR = PROJECT_ROOT / "artifacts" / "persona" # PROMPTS_DIR / "sample-participants"

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
print(f"[DEBUG] Loaded participant profiles: {list(PARTICIPANT_PROFILES.keys())}")
MODERATOR_GUIDE = load_prompt(PROMPTS_DIR / "interview_moderator.md") if (PROMPTS_DIR / "interview_moderator.md").exists() else "인터뷰 모더레이터 가이드"
ORCHESTRATOR_GUIDE = load_prompt(PROMPTS_DIR / "orchestrator.md") if (PROMPTS_DIR / "orchestrator.md").exists() else "FGI 오케스트레이터 가이드"

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
5. **길이**: 답변은 2-3문장 정도로 간결하게 (너무 길지 않게)
6. **다른 참가자 의견에 반응 가능**: 다른 참가자의 의견이 언급되면, 동의하거나 다른 관점을 제시할 수 있습니다

답변 예시:
- "저는 퇴근하면 너무 피곤해서 요리할 엄두가 안 나요. 그래서 배달음식을 자주 시키는데, 건강에는 안 좋은 것 같아서 고민이에요."
- "가격이 좀 부담되는 것 같아요. 한 끼에 만원 넘으면 그냥 배달시키는 게 나을 수도 있을 것 같은데..."
"""

# 전역 대화 히스토리
conversation_history = []

# 메시지 큐 유틸 함수들
def add_message_to_queue(msg_type: str, content: str, **kwargs):
    """메시지를 큐에 추가하는 유틸 함수"""
    message = {
        'type': msg_type,
        'content': content,
        'role': kwargs.get('role', msg_type),
        **kwargs
    }
    message_queue.put(message)

def add_moderator_message(content: str):
    """모더레이터 메시지 추가"""
    add_message_to_queue('moderator', content, role='moderator')

def add_participant_message(name: str, content: str, participant_id: str):
    """참가자 메시지 추가"""
    add_message_to_queue('participant', content, 
                        role='participant', 
                        name=name, 
                        participant_id=participant_id)

def add_system_message(content: str):
    """시스템 메시지 추가"""
    add_message_to_queue('system', content, role='system')

def add_error_message(content: str, **kwargs):
    """에러 메시지 추가"""
    add_message_to_queue('error', content, role='system', **kwargs)

# 대화 히스토리 관리
def add_to_history(speaker: str, content: str):
    """대화 히스토리에 발언 추가"""
    conversation_history.append(f"{speaker}: {content}")

def get_conversation_context() -> str:
    """현재까지의 대화 맥락 반환"""
    if not conversation_history:
        return "아직 대화가 시작되지 않았습니다."
    
    return "\n".join(conversation_history[-20:])  # 최근 20개 발언만 유지

# 참가자 도구들
def create_participant_tool(participant_id: str, participant_name: str):
    """참가자 도구 생성 - 대화 맥락을 포함하여 응답"""
    def participant_tool(query: str) -> str:
        try:
            # 전체 대화 맥락 + 현재 질문
            context = get_conversation_context()
            full_query = f"""
=== 지금까지의 대화 ===
{context}

=== 현재 질문 ===
{query}

위 대화 맥락을 참고해서 답변해주세요. 다른 참가자들의 의견에 동의하거나 다른 관점을 제시할 수 있습니다.
"""

            profile = PARTICIPANT_PROFILES.get(participant_id, f"{participant_name} 프로필")
            agent = Agent(
                system_prompt=create_participant_prompt(profile, participant_name)
            )
            response = str(agent(full_query))

            # 대화 히스토리에 추가
            add_to_history(participant_name, response)

            # 메시지 큐에 추가
            add_participant_message(participant_name, response, participant_id)

            return response
        except Exception as e:
            error_msg = f"[오류] {str(e)}"
            add_error_message(f"{participant_name} 응답 생성 중 오류: {error_msg}",
                            participant_name=participant_name)
            return error_msg

    # 도구 메타데이터 설정
    participant_tool.__name__ = f"participant_{participant_id}"
    participant_tool.__doc__ = f"참가자 {participant_name}에게 질문하고 응답을 받습니다. query 파라미터에 질문 내용을 전달하세요."

    return tool(participant_tool)

# 참가자 도구들 생성
participant_yoonseo = create_participant_tool("yoonseo", "윤서")
participant_dohyung = create_participant_tool("dohyung", "도형")
participant_jiyeon = create_participant_tool("jiyeon", "지연")
participant_sukwon = create_participant_tool("sukwon", "석원")
participant_shinchul = create_participant_tool("shinchul", "신철")

# Moderator 도구 - 단순 발언 tool
@tool
def moderator(message: str) -> str:
    """
    모더레이터가 참가자들에게 발언합니다.
    인사, 질문, 주제 전환, 의견 요청 등 모더레이터의 모든 발언에 사용됩니다.

    Args:
        message: 모더레이터가 참가자들에게 전달할 메시지

    Returns:
        확인 메시지
    """
    try:
        print(f"[MODERATOR] {message}")

        # 대화 히스토리에 추가
        add_to_history("Moderator", message)

        # 메시지 큐에 추가
        add_moderator_message(message)

        return f"✓ 모더레이터 발언 완료"
    except Exception as e:
        error_msg = f"모더레이터 발언 오류: {str(e)}"
        add_error_message(error_msg)
        return error_msg

# Orchestrator Agent 생성
def create_orchestrator_agent():
    """
    Orchestrator Agent - 전체 FGI 워크플로우를 관리
    모든 tool을 직접 가지고 유연하게 인터뷰를 진행
    """
    return Agent(
        system_prompt=ORCHESTRATOR_GUIDE,
        tools=[
            moderator,
            participant_yoonseo,
            participant_dohyung,
            participant_jiyeon,
            participant_sukwon,
            participant_shinchul,
            file_write,
        ],
    )

async def fgi_stream():
    """FGI 진행 과정을 SSE로 스트리밍"""
    try:
        # 큐 초기화
        while not message_queue.empty():
            message_queue.get()

        # 대화 히스토리 초기화
        conversation_history.clear()

        # 시작 메시지
        yield f"data: {json.dumps({'type': 'system', 'content': '인터뷰 세션을 시작합니다...', 'role': 'system'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)

        # 참가자 소개
        yield f"data: {json.dumps({'type': 'system', 'content': '참가자: 윤서, 도형, 지연, 석원, 신철', 'role': 'system'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)

        # Orchestrator 생성
        orchestrator = create_orchestrator_agent()

        # Orchestrator 쿼리
        ORCHESTRATOR_QUERY = """
구독형 밀키트 서비스에 대한 Focus Group Interview를 진행해주세요.

5명의 참가자(윤서, 도형, 지연, 석원, 신철)가 준비되어 있습니다.
각 단계를 순차적으로 진행하며, 자연스러운 대화 흐름을 유지해주세요.
"""

        # Orchestrator를 별도 스레드에서 실행
        def run_orchestrator():
            try:
                print("[DEBUG] Orchestrator 시작")

                response = str(orchestrator(ORCHESTRATOR_QUERY))

                print(f"[DEBUG] Orchestrator 완료")
                print("=" * 50)
                print(response)
                print("=" * 50)

                add_message_to_queue('complete', '', role='system')
            except Exception as e:
                print(f"[DEBUG] Orchestrator 오류: {str(e)}")
                add_error_message(f"Orchestrator 오류: {str(e)}")

        orchestrator_thread = threading.Thread(target=run_orchestrator)
        orchestrator_thread.start()

        # 큐에서 메시지를 읽어서 스트리밍
        while True:
            try:
                # 1초마다 큐 확인
                message = message_queue.get(timeout=1.0)

                if message['type'] == 'complete':
                    yield f"data: {json.dumps({'type': 'system', 'content': '인터뷰 세션이 종료되었습니다.'}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'complete'}, ensure_ascii=False)}\n\n"
                    break
                else:
                    yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"

            except queue.Empty:
                continue
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': f'스트리밍 오류: {str(e)}'}, ensure_ascii=False)}\n\n"
                break

        # 스레드 종료 대기
        orchestrator_thread.join(timeout=60)

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

@app.get("/api/participants")
async def get_participants():
    """모든 참가자 프로필 반환"""
    return {
        "participants": [
            {"id": "yoonseo", "name": "윤서", "profile": PARTICIPANT_PROFILES.get("yoonseo", "")},
            {"id": "dohyung", "name": "도형", "profile": PARTICIPANT_PROFILES.get("dohyung", "")},
            {"id": "jiyeon", "name": "지연", "profile": PARTICIPANT_PROFILES.get("jiyeon", "")},
            {"id": "sukwon", "name": "석원", "profile": PARTICIPANT_PROFILES.get("sukwon", "")},
            {"id": "shinchul", "name": "신철", "profile": PARTICIPANT_PROFILES.get("shinchul", "")},
        ]
    }

@app.get("/api/participants/{participant_id}")
async def get_participant_profile(participant_id: str):
    """특정 참가자의 프로필 반환"""
    print(f"[DEBUG] Requested participant_id: {participant_id}")
    print(f"[DEBUG] Available profiles: {list(PARTICIPANT_PROFILES.keys())}")

    profile = PARTICIPANT_PROFILES.get(participant_id)
    if not profile:
        print(f"[DEBUG] Profile not found for {participant_id}")
        raise HTTPException(status_code=404, detail="Participant not found")

    print(f"[DEBUG] Returning profile for {participant_id}, length: {len(profile)}")
    return {"id": participant_id, "profile": profile}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
