# Agentic "Focus Group Interview"

AI 기반 Focus Group Interview(FGI) 시뮬레이션 시스템

## 개요

이 프로젝트는 제품이나 서비스에 대한 정성적 리서치(Focus Group Interview)를 자동화하는 멀티 에이전트 시스템입니다. Strands 프레임워크를 기반으로 여러 AI 에이전트들이 협력하여 FGI 기획부터 진행, 분석까지 전 과정을 자동으로 수행합니다.

## 시스템 아키텍처

시스템은 5개의 핵심 노드로 구성된 순차적 파이프라인으로 동작합니다:

```
Product Researcher → Persona Generator → Interview Planner → Interview Moderator → Analyst
```

### 1. Product Researcher (제품 조사)
- **역할**: 연구 대상 제품/서비스에 대한 심층 조사
- **출력**: 제품 특성, 시장 현황, 경쟁 제품 분석 등
- **목적**: FGI의 기반이 되는 제품 이해도 확보

### 2. Persona Generator (페르소나 생성)
- **역할**: FGI 참가자 페르소나 생성
- **출력**: 다양한 배경을 가진 가상 참가자 프로필
- **특징**: 연령, 직업, 가족 구성, 라이프스타일 등을 포함한 상세한 페르소나 설계
- **예시**:
  - 김윤서 (28세, IT 스타트업 UX 디자이너, 1인 가구)
  - 김도형 (32세, 제조업 영업팀 과장, 신혼부부)
  - 이지연 (37세, 프리랜서 마케팅 컨설턴트, 초등생 자녀 2명)
  - 이석원 (42세, 금융회사 팀장, 4세 딸+맞벌이)
  - 방신철 (26세, 대학원생, 룸메이트와 거주)

### 3. Interview Planner (인터뷰 기획)
- **역할**: FGI 진행 가이드 및 질문지 작성
- **출력**: 단계별 인터뷰 가이드, 핵심 질문, 탐색 주제
- **목적**: 체계적인 FGI 진행을 위한 구조화된 플랜 제공

### 4. Interview Moderator (인터뷰 진행)
- **역할**: 실제 FGI 세션 진행 및 모더레이팅
- **동작 방식**:
  - 각 참가자를 개별 AI 에이전트로 구현
  - Moderator가 질문하면 각 참가자 툴을 호출하여 페르소나에 맞는 답변 수집
  - 자연스러운 대화 흐름 유지 및 후속 질문 진행
  - 중요한 인사이트를 실시간으로 기록
- **출력**: 전체 인터뷰 녹취록 (`artifacts/interview_results.txt`)

### 5. Analyst (분석 및 보고서 작성)
- **역할**: FGI 결과에 대한 정성적 분석 수행
- **분석 방법**:
  - 주제 분석(Thematic Analysis)을 통한 패턴 식별
  - 참가자 발언의 맥락과 뉘앙스 해석
  - 정성적 발견과 정량적 데이터 통합 분석
  - 실행 가능한 인사이트 도출
- **출력**: 종합 리서치 보고서 (`artifacts/final_report.md`)

## 주요 특징

### 참가자 시뮬레이션
각 참가자는 독립적인 AI 에이전트로 구현되며, 다음과 같은 특징을 가집니다:
- 페르소나에 충실한 답변 생성
- 구체적인 경험과 상황 기반 응답
- 자연스러운 대화체 유지
- 다른 참가자 의견에 대한 반응 및 상호작용

### 도구 통합
시스템은 다양한 도구를 활용합니다:
- `file_read`: 데이터 및 프롬프트 로드
- `file_write`: 중간 결과물 및 최종 보고서 저장
- 참가자 툴: 각 페르소나와의 상호작용

## 프로젝트 구조

```
focus-group-interview-agents/
├── src/
│   ├── graph/
│   │   ├── builder.py              # 그래프 구조 정의
│   │   ├── interview_node.py       # Moderator 및 참가자 구현
│   │   └── nodes.py                # 나머지 노드 구현
│   └── prompts/
│       ├── template.py             # 프롬프트 템플릿 로더
│       ├── product_researcher.md   # Product Researcher 시스템 프롬프트
│       ├── persona_generator.md    # Persona Generator 시스템 프롬프트
│       ├── interview_planner.md    # Interview Planner 시스템 프롬프트
│       ├── interview_moderator.md  # Interview Moderator 시스템 프롬프트
│       ├── analyst.md              # Analyst 시스템 프롬프트
│       └── sample-participants/    # 샘플 참가자 프로필
├── artifacts/                       # 생성된 데이터 및 결과물
│   ├── interview_results.txt       # FGI 녹취록
│   └── final_report.md             # 최종 분석 보고서
└── main.py                          # 실행 엔트리포인트
```

## 데이터 흐름

```
1. 제품 정보 입력
   ↓
2. Product Researcher: 제품 조사
   ↓
3. Persona Generator: 참가자 페르소나 생성
   ↓
4. Interview Planner: FGI 가이드 작성
   ↓
5. Interview Moderator: FGI 진행
   - Moderator가 질문 → 각 참가자 에이전트 응답 → 대화 기록
   ↓
6. interview_results.txt 저장
   ↓
7. Analyst: 정성적 분석 수행
   ↓
8. final_report.md 보고서 생성
```

## 사용 사례

- 신제품 출시 전 사용자 반응 시뮬레이션
- 서비스 개선을 위한 사용자 니즈 탐색
- 마케팅 메시지 테스트
- 다양한 사용자 세그먼트의 의견 수렴
- 정성 리서치 프로토타이핑

## 실행 방법

### 웹 UI 실행 (권장)

1. **백엔드 서버 시작**:
```bash
python server.py
```

2. **프론트엔드 시작** (새 터미널):
```bash
cd frontend
npm install  # 처음 한 번만
npm run dev
```

3. 브라우저에서 http://localhost:5173 접속

4. "FGI 시작" 버튼 클릭하여 실시간으로 인터뷰 진행 과정 확인

### CLI 실행

```bash
python main.py
```

## 기술 스택

- **백엔드**:
  - Python 3.12+
  - FastAPI (REST API & SSE 스트리밍)
  - Strands (멀티 에이전트 오케스트레이션)
  - Claude (Anthropic AI 모델)
- **프론트엔드**:
  - React 18 + TypeScript
  - Vite
  - Server-Sent Events (SSE)
- **도구**: strands_tools (file_read, file_write)
