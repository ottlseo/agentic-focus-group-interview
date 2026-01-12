import { useState, useEffect, useRef } from 'react'
import './App.css'

interface Message {
  type: 'system' | 'moderator' | 'participant' | 'error' | 'complete'
  content?: string
  name?: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [status, setStatus] = useState<'idle' | 'connecting' | 'running' | 'completed' | 'error'>('idle')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startFGI = async () => {
    setMessages([])
    setStatus('connecting')

    // CloudFront를 통해 백엔드 연결
    const isCloudFront = window.location.hostname.includes('cloudfront.net')
    const backendUrl = isCloudFront
      ? window.location.origin + '/proxy/8000/api/fgi/run'  // 실제 LLM 호출
      : 'http://localhost:8000/api/fgi/run'  // 실제 LLM 호출

    console.log('Connecting to backend:', backendUrl)

    try {
      setStatus('running')

      // 로딩 메시지 표시
      const loadingMsg = 'AI 참가자들이 응답을 생성 중입니다... (약 1-2분 소요)'

      setMessages([{
        type: 'system',
        content: loadingMsg
      }])

      // 3분 타임아웃 (순차 처리로 인해 시간이 더 필요)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 180000)

      const response = await fetch(backendUrl, {
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      const allMessages = data.messages || []

      // 로딩 메시지 제거 후 실제 메시지 표시
      setMessages([])

      // 메시지를 하나씩 천천히 표시 (애니메이션 효과)
      for (let i = 0; i < allMessages.length; i++) {
        setMessages(prev => [...prev, allMessages[i]])
        // 메시지 타입에 따라 다른 지연 시간
        const delay = allMessages[i].type === 'system' ? 300 : 800
        await new Promise(resolve => setTimeout(resolve, delay))
      }

      setStatus('completed')
    } catch (err) {
      console.error('Request Error:', err)
      setStatus('error')

      const error = err as Error
      const errorMessage = error.name === 'AbortError'
        ? '요청 시간이 초과되었습니다. 다시 시도해주세요.'
        : '연결 오류가 발생했습니다. 백엔드 서버가 실행 중인지 확인해주세요.'

      setMessages([{
        type: 'error',
        content: errorMessage
      }])
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎯 Focus Group Interview Simulator</h1>
        <div className="status-bar">
          <span className={`status-badge status-${status}`}>
            {status === 'idle' && '대기 중'}
            {status === 'connecting' && '연결 중...'}
            {status === 'running' && '진행 중'}
            {status === 'completed' && '완료'}
            {status === 'error' && '오류'}
          </span>
          <button
            onClick={startFGI}
            disabled={status === 'running' || status === 'connecting'}
            className="start-button"
          >
            {status === 'idle' ? 'FGI 시작' : status === 'running' ? '진행 중...' : 'FGI 재시작'}
          </button>
        </div>
      </header>

      <main className="messages-container">
        {messages.length === 0 && status === 'idle' && (
          <div className="empty-state">
            <p>👆 "FGI 시작" 버튼을 눌러 인터뷰를 시작하세요</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '12px' }}>
              실시간 스트리밍으로 대화가 진행됩니다 (약 1-2분 소요)
            </p>
            <div className="participants-info">
              <h3>참가자</h3>
              <ul>
                <li>윤서 (28세 여성, IT 스타트업 UX 디자이너)</li>
                <li>도형 (32세 남성, 제조업 영업팀 과장)</li>
                <li>지연 (37세 여성, 프리랜서 마케팅 컨설턴트)</li>
                <li>석원 (42세 남성, 금융회사 팀장)</li>
                <li>신철 (26세 남성, 대학원생)</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message message-${msg.type}`}>
            {msg.type === 'system' && (
              <div className="message-content">
                <span className="message-icon">ℹ️</span>
                <span className="message-text">{msg.content}</span>
              </div>
            )}

            {msg.type === 'moderator' && (
              <div className="message-content">
                <div className="message-header">
                  <span className="message-icon">🎤</span>
                  <span className="message-sender">Moderator</span>
                </div>
                <div className="message-text">{msg.content}</div>
              </div>
            )}

            {msg.type === 'participant' && (
              <div className="message-content">
                <div className="message-header">
                  <span className="message-icon">👤</span>
                  <span className="message-sender">{msg.name}</span>
                </div>
                <div className="message-text">{msg.content}</div>
              </div>
            )}

            {msg.type === 'error' && (
              <div className="message-content">
                <span className="message-icon">❌</span>
                <span className="message-text">{msg.content}</span>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>
    </div>
  )
}

export default App
