import { useState, useEffect, useRef } from 'react'
import { marked } from 'marked'
import './App.css'

interface Message {
  type: 'system' | 'moderator' | 'participant' | 'error' | 'complete'
  content?: string
  name?: string
}

interface ParticipantProfile {
  id: string
  name: string
  profile: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [status, setStatus] = useState<'idle' | 'connecting' | 'running' | 'completed' | 'error'>('idle')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [selectedProfile, setSelectedProfile] = useState<ParticipantProfile | null>(null)

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

  const fetchParticipantProfile = async (participantId: string, participantName: string) => {
    const isCloudFront = window.location.hostname.includes('cloudfront.net')
    const backendUrl = isCloudFront
      ? window.location.origin + `/proxy/8000/api/participants/${participantId}`
      : `http://localhost:8000/api/participants/${participantId}`

    try {
      const response = await fetch(backendUrl)
      const data = await response.json()
      setSelectedProfile({
        id: participantId,
        name: participantName,
        profile: data.profile
      })
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      setSelectedProfile({
        id: participantId,
        name: participantName,
        profile: '프로필을 불러올 수 없습니다.'
      })
    }
  }

  const closeModal = () => {
    setSelectedProfile(null)
  }

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
          
          console.log('받은 데이터:', data) // 디버깅용
          
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
        console.error('EventSource readyState:', eventSource.readyState)

        // readyState 2 = CLOSED (정상 종료 가능)
        if (eventSource.readyState === EventSource.CLOSED) {
          console.log('SSE connection closed normally')
          return
        }

        setStatus('error')
        setMessages(prev => [...prev, {
          type: 'error',
          content: '연결 오류가 발생했습니다. 백엔드 서버가 실행 중인지 확인해주세요.'
        }])
        eventSource.close()
      }

      // 10분 후 자동 종료 (충분한 대화 시간 확보)
      setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close()
          setStatus('error')
          setMessages(prev => [...prev, {
            type: 'error',
            content: '요청 시간이 초과되었습니다.'
          }])
        }
      }, 600000)  // 10분

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
            <div className="interview-info">
              <div className="info-header">
                <span className="info-icon">🎯</span>
                <h2>구독형 밀키트 서비스 FGI</h2>
              </div>
              <div className="info-content">
                <div className="info-section">
                  <h3>📋 인터뷰 목적</h3>
                  <p>구독형 밀키트 서비스의 고객 니즈와 페인 포인트를 파악하여, 서비스 기획 및 개선 방향을 도출합니다.</p>
                </div>
                <div className="info-section">
                  <h3>💬 주요 탐색 주제</h3>
                  <ul>
                    <li>현재 식생활 패턴 및 밀키트 사용 경험</li>
                    <li>구독형 서비스에 대한 기대와 우려</li>
                    <li>가격, 메뉴 구성, 배송 주기 등 선호사항</li>
                    <li>의사결정 요인 및 개선 아이디어</li>
                  </ul>
                </div>
                <div className="info-section">
                  <h3>⏱️ 예상 소요 시간</h3>
                  <p>약 5-10분 (AI 기반 자동 진행)</p>
                </div>
              </div>
              <div className="start-prompt">
                <p>👆 "인터뷰 시작" 버튼을 눌러 시작하세요</p>
              </div>
            </div>
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
                
                <div className="participant-card" onClick={() => fetchParticipantProfile('yoonseo', '윤서')}>
                  <div className="participant-header">
                    <div className="participant-avatar">👩‍💻</div>
                    <div className="participant-name">윤서</div>
                  </div>
                  <div className="participant-desc">28세 여성, IT 스타트업 UX 디자이너</div>
                </div>

                <div className="participant-card" onClick={() => fetchParticipantProfile('dohyung', '도형')}>
                  <div className="participant-header">
                    <div className="participant-avatar">👨‍💼</div>
                    <div className="participant-name">도형</div>
                  </div>
                  <div className="participant-desc">32세 남성, 제조업 영업팀 과장</div>
                </div>

                <div className="participant-card" onClick={() => fetchParticipantProfile('jiyeon', '지연')}>
                  <div className="participant-header">
                    <div className="participant-avatar">👩‍💼</div>
                    <div className="participant-name">지연</div>
                  </div>
                  <div className="participant-desc">37세 여성, 프리랜서 마케팅 컨설턴트</div>
                </div>

                <div className="participant-card" onClick={() => fetchParticipantProfile('sukwon', '석원')}>
                  <div className="participant-header">
                    <div className="participant-avatar">👨</div>
                    <div className="participant-name">석원</div>
                  </div>
                  <div className="participant-desc">42세 남성, 금융회사 팀장</div>
                </div>

                <div className="participant-card" onClick={() => fetchParticipantProfile('shinchul', '신철')}>
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
          <div key={index} className={`message message-${msg.role || msg.type}`}>
            {(msg.role === 'system' || msg.type === 'system') && (
              <div className="bubble bubble-system">
                <span className="message-icon">ℹ️</span> {msg.content}
              </div>
            )}

            {(msg.role === 'moderator' || msg.type === 'moderator') && (
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

            {(msg.role === 'participant' || msg.type === 'participant') && (
              <>
                <div className="avatar avatar-participant">
                  {msg.name === '윤서' && '👩‍💻'}
                  {msg.name === '도형' && '👨‍💼'}
                  {msg.name === '지연' && '👩‍💼'}
                  {msg.name === '석원' && '👨'}
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

            {(msg.role === 'system' && msg.type === 'error') && (
              <div className="bubble bubble-error">
                <span className="message-icon">❌</span> {msg.content}
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      {selectedProfile && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedProfile.name}의 프로필</h2>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>
            <div className="modal-body">
              <div
                className="markdown-content"
                dangerouslySetInnerHTML={{ __html: marked(selectedProfile.profile) }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
