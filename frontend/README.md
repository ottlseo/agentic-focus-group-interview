# FGI Simulator Frontend

Focus Group Interview Simulator의 웹 인터페이스입니다.

## 기술 스택

- React 18 + TypeScript
- Vite
- Server-Sent Events (SSE)

## 실행 방법

### 1. 백엔드 서버 실행

프로젝트 루트에서:

```bash
python server.py
```

서버가 http://localhost:8000 에서 실행됩니다.

### 2. 프론트엔드 실행

frontend 디렉토리에서:

```bash
npm install  # 처음 한 번만
npm run dev
```

브라우저에서 http://localhost:5173 으로 접속합니다.

## 기능

- **실시간 스트리밍**: SSE를 통한 FGI 진행 과정 실시간 표시
- **참가자별 메시지**: Moderator와 5명의 참가자 응답을 구분하여 표시
- **자동 스크롤**: 새 메시지가 추가되면 자동으로 스크롤
- **상태 관리**: 진행 중/완료/오류 상태 표시

## 화면 구성

- **System 메시지**: 세션 시작/종료 등 시스템 알림 (파란색)
- **Moderator 메시지**: 모더레이터의 질문 (주황색)
- **Participant 메시지**: 참가자 응답 (보라색)
- **Error 메시지**: 오류 발생 시 (빨간색)
