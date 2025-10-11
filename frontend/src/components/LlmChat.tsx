import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Trash2, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import type { ChatMessage } from '../types';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

interface LlmChatProps {
  sessionId: string | null;
}

const LlmChat: React.FC<LlmChatProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: '안녕하세요! 포트폴리오 분석 도우미입니다. 궁금한 점이 있으시면 언제든 질문해주세요.',
      timestamp: new Date(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 세션 변경 시 히스토리 로드
  useEffect(() => {
    if (sessionId) {
      loadChatHistory();
    } else {
      // 세션이 없으면 초기 메시지만 표시
      setMessages([
        {
          id: '1',
          type: 'bot',
          content: '안녕하세요! 포트폴리오 분석 도우미입니다. CSV 파일을 업로드하면 AI 분석 기능을 사용할 수 있습니다.',
          timestamp: new Date(),
        }
      ]);
    }
  }, [sessionId]);

  const loadChatHistory = async () => {
    try {
      const { history } = await api.getChatHistory();
      
      if (history.length > 0) {
        // 백엔드에서 불러온 히스토리를 UI 형식으로 변환
        const loadedMessages: Message[] = history.map((msg, index) => ({
          id: `loaded-${index}`,
          type: msg.role === 'assistant' ? 'bot' : 'user',
          content: msg.content,
          timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
        }));
        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error('히스토리 로드 실패:', err);
      // 히스토리 로드 실패 시 초기 메시지 표시
      setMessages([
        {
          id: '1',
          type: 'bot',
          content: '안녕하세요! 포트폴리오 분석 도우미입니다. 궁금한 점이 있으시면 언제든 질문해주세요.',
          timestamp: new Date(),
        }
      ]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    const userMessageContent = inputMessage.trim();
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userMessageContent,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // 실제 AI API 호출
      const response = await api.sendChatMessage({
        message: userMessageContent,
        provider: 'gemini', // 또는 환경 변수에서 읽기
      });

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('채팅 오류:', err);
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      
      setError(errorMessage);
      
      // 에러 메시지를 봇 응답으로 표시
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: `죄송합니다. 오류가 발생했습니다: ${errorMessage}\n\n다시 시도해주세요.`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzePortfolio = async () => {
    if (!sessionId || isLoading) return;

    setIsLoading(true);
    setError(null);

    const requestMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: '포트폴리오 전체 분석 요청',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, requestMessage]);

    try {
      const response = await api.analyzePortfolio();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.analysis,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('분석 오류:', err);
      const errorMessage = err instanceof Error ? err.message : '분석 중 오류가 발생했습니다.';
      
      setError(errorMessage);
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: `죄송합니다. 분석 중 오류가 발생했습니다: ${errorMessage}`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('대화 내역을 모두 삭제하시겠습니까?')) return;

    try {
      await api.clearChatHistory();
      setMessages([
        {
          id: '1',
          type: 'bot',
          content: '대화 내역이 초기화되었습니다. 새로운 대화를 시작해주세요.',
          timestamp: new Date(),
        }
      ]);
    } catch (err) {
      console.error('히스토리 삭제 실패:', err);
      setError('대화 내역 삭제에 실패했습니다.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="h-full flex flex-col bg-white border border-gray-200 rounded-lg">
      {/* 채팅 헤더 */}
      <div className="p-3 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900 text-sm">포트폴리오 분석 도우미</h3>
            <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
              AI
            </span>
          </div>
          <div className="flex items-center space-x-1">
            {sessionId && (
              <>
                <button
                  onClick={handleAnalyzePortfolio}
                  disabled={isLoading}
                  className="p-1.5 hover:bg-white rounded-lg transition-colors disabled:opacity-50"
                  title="포트폴리오 전체 분석"
                >
                  <Sparkles className="w-4 h-4 text-purple-600" />
                </button>
                <button
                  onClick={handleClearHistory}
                  disabled={isLoading}
                  className="p-1.5 hover:bg-white rounded-lg transition-colors disabled:opacity-50"
                  title="대화 내역 삭제"
                >
                  <Trash2 className="w-4 h-4 text-gray-600" />
                </button>
              </>
            )}
          </div>
        </div>
        <p className="text-xs text-gray-600 mt-1">
          {sessionId ? 'AI와 함께 포트폴리오를 분석해보세요' : 'CSV 파일을 업로드하면 AI 분석 기능을 사용할 수 있습니다'}
        </p>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'bot' && (
                  <Bot className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                )}
                {message.type === 'user' && (
                  <User className="w-4 h-4 mt-0.5 text-blue-200 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p className="text-xs whitespace-pre-wrap">{message.content}</p>
                  <p className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-3 py-2">
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4 text-blue-600" />
                <Loader2 className="w-4 h-4 animate-spin text-gray-600" />
                <span className="text-xs text-gray-600">답변을 생성하고 있습니다...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="p-3 border-t border-gray-200 bg-gray-50">
        {error && (
          <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-xs text-red-600">{error}</p>
          </div>
        )}
        
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={sessionId ? "포트폴리오에 대해 질문해보세요... (예: 수익률이 괜찮나요?)" : "CSV 파일을 업로드한 후 사용할 수 있습니다."}
            disabled={!sessionId || isLoading}
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed bg-white"
            rows={3}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || !sessionId || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          {!sessionId ? (
            <p>CSV 파일을 업로드하면 AI 분석 기능을 사용할 수 있습니다.</p>
          ) : (
            <p>Enter로 전송 | Shift+Enter로 줄바꿈</p>
          )}
          {sessionId && (
            <button
              onClick={handleAnalyzePortfolio}
              disabled={isLoading}
              className="text-purple-600 hover:text-purple-700 font-medium disabled:opacity-50"
            >
              <Sparkles className="w-3 h-3 inline mr-1" />
              전체 분석
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default LlmChat;
