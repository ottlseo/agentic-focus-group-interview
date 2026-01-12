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
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom()
    }
  }, [messages])

  const startFGI = async () => {
    setMessages([])
    setStatus('connecting')

    // CloudFront를 통해 백엔드 연결
    const isCloudFront = window.location.hostname.includes('cloudfront.net')
    const backendUrl = isCloudFront
      ? window.location.origin + '/proxy/8000/api/fgi/stream'  // SSE 스트리밍
      : 'http://localhost:8000/api/fgi/stream'  // SSE 스트리밍

    console.log('Connecting to backend:', backendUrl)

    try {
      setStatus('running')

      const eventSource = new EventSource(backendUrl)

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'complete') {
            setStatus('completed')
            eventSource.close()
          } else if (data.type === 'error') {
            setStatus('error')
            eventSource.close()
          } else {
            setMessages(prev => [...prev, data])
          }
        } catch (err) {
          console.error('Parse error:', err)
        }
      }

      eventSource.onerror = (err) => {
        console.error('SSE Error:', err)
        setStatus('error')
        setMessages(prev => [...prev, {
          type: 'error',
          content: '연결 오류가 발생했습니다. 백엔드 서버가 실행 중인지 확인해주세요.'
        }])
        eventSource.close()
      }

      // 3분 후 자동 종료
      setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close()
          setStatus('error')
          setMessages(prev => [...prev, {
            type: 'error',
            content: '요청 시간이 초과되었습니다.'
          }])
        }
      }, 180000)

    } catch (err) {
      console.error('Request Error:', err)
      setStatus('error')
      setMessages([{
        type: 'error',
        content: '연결 오류가 발생했습니다.'
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
            {status === 'idle' ? '인터뷰 시작' : status === 'running' ? '진행 중...' : '인터뷰 재시작'}
          </button>
        </div>
      </header>

      <main className="chat-container">
        {messages.length === 0 && status === 'idle' && (
          <div className="empty-state">
            <p>👆 "인터뷰 시작" 버튼을 눌러 인터뷰를 시작하세요</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '12px' }}>
              실시간 스트리밍으로 대화가 진행됩니다 (약 1-2분 소요)
            </p>
            <div className="participants-info">
              <h3>참가자</h3>
              <div className="participants-grid">
                <div className="participant-card moderator-card">
                  <div className="participant-header">
                    <div className="participant-avatar">🎤</div>
                    <div className="participant-name">Moderator</div>
                  </div>
                  <div className="participant-desc">인터뷰 진행자</div>
                </div>
                
                <div className="participant-card">
                  <div className="participant-header">
                    <div className="participant-avatar">👩‍💻</div>
                    <div className="participant-name">윤서</div>
                  </div>
                  <div className="participant-desc">28세 여성, IT 스타트업 UX 디자이너</div>
                </div>
                
                <div className="participant-card">
                  <div className="participant-header">
                    <div className="participant-avatar">👨‍💼</div>
                    <div className="participant-name">도형</div>
                  </div>
                  <div className="participant-desc">32세 남성, 제조업 영업팀 과장</div>
                </div>
                
                <div className="participant-card">
                  <div className="participant-header">
                    <div className="participant-avatar">👩‍💼</div>
                    <div className="participant-name">지연</div>
                  </div>
                  <div className="participant-desc">37세 여성, 프리랜서 마케팅 컨설턴트</div>
                </div>
                
                <div className="participant-card">
                  <div className="participant-header">
                    <div className="participant-avatar">👨‍🏢</div>
                    <div className="participant-name">석원</div>
                  </div>
                  <div className="participant-desc">42세 남성, 금융회사 팀장</div>
                </div>
                
                <div className="participant-card">
                  <div className="participant-header">
                    <div className="participant-avatar">👨‍🎓</div>
                    <div className="participant-name">신철</div>
                  </div>
                  <div className="participant-desc">26세 남성, 대학원생</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message message-${msg.type}`}>
            {msg.type === 'system' && (
              <div className="bubble bubble-system">
                <span className="message-icon">ℹ️</span> {msg.content}
              </div>
            )}

            {msg.type === 'moderator' && (
              <>
                <div className="avatar avatar-moderator">🎤</div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-sender">Moderator</span>
                  </div>
                  <div className="bubble bubble-moderator">
                    {msg.content}
                  </div>
                </div>
              </>
            )}

            {msg.type === 'participant' && (
              <>
                <div className="avatar avatar-participant">
                  {msg.name === '윤서' && '👩‍💻'}
                  {msg.name === '도형' && '👨‍💼'}
                  {msg.name === '지연' && '👩‍💼'}
                  {msg.name === '석원' && '👨‍🏢'}
                  {msg.name === '신철' && '👨‍🎓'}
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-sender">{msg.name}</span>
                  </div>
                  <div className="bubble bubble-participant">
                    {msg.content}
                  </div>
                </div>
              </>
            )}

            {msg.type === 'error' && (
              <div className="bubble bubble-error">
                <span className="message-icon">❌</span> {msg.content}
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
