import axios from 'axios';
import type { 
  SessionInfo, 
  CacheInfo,
  TransactionList,
  ParsedData,
  ChatRequest,
  ChatResponse,
  ChatSession,
  ChatSessionInfo
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

// Axios 인스턴스 생성
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API 함수들
export const api = {
  // CSV 업로드
  uploadCsv: async (file: File): Promise<SessionInfo> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // 캐시 정보
  getCacheInfo: async (): Promise<CacheInfo> => {
    const response = await apiClient.get('/cache/info');
    return response.data;
  },

  // 캐시 삭제
  clearCache: async (sessionId?: string): Promise<void> => {
    if (sessionId) {
      await apiClient.delete(`/cache/${sessionId}`);
    } else {
      await apiClient.delete('/cache/clear');
    }
  },

  // 전체 거래 내역 조회
  getAllTransactions: async (sessionId: string): Promise<TransactionList> => {
    const response = await apiClient.get(`/transactions/${sessionId}`);
    return response.data;
  },

  // 파싱된 전체 데이터 조회 (JSON 캐시)
  getParsedData: async (): Promise<ParsedData> => {
    const response = await apiClient.get('/data/parsed');
    return response.data;
  },

  // ============================================
  // AI Chat API
  // ============================================
  
  // 채팅 메시지 전송
  sendChatMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat', request, {
      timeout: 60000, // 60초 타임아웃 (AI 응답 대기)
    });
    return response.data;
  },

  // 스트리밍 채팅 (추후 구현)
  sendChatMessageStream: async (request: ChatRequest): Promise<ReadableStream> => {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('스트리밍 채팅 요청 실패');
    }

    if (!response.body) {
      throw new Error('응답 본문이 없습니다');
    }

    return response.body;
  },

  // 포트폴리오 전체 분석
  analyzePortfolio: async (): Promise<{ analysis: string; history: Array<{ role: string; content: string; timestamp?: string }> }> => {
    const response = await apiClient.post('/chat/analyze', {}, {
      timeout: 90000, // 90초 타임아웃 (분석은 시간이 더 걸릴 수 있음)
    });
    return response.data;
  },

  // 채팅 히스토리 조회
  getChatHistory: async (): Promise<{ history: ChatMessage[] }> => {
    const response = await apiClient.get('/chat/history');
    return response.data;
  },

  // 채팅 히스토리 초기화
  clearChatHistory: async (): Promise<{ message: string }> => {
    const response = await apiClient.delete('/chat/history');
    return response.data;
  },

  // 채팅 세션 목록 조회
  getChatSessions: async (): Promise<{ sessions: ChatSession[] }> => {
    const response = await apiClient.get('/chat/sessions');
    return response.data;
  },

  // 현재 세션 정보
  getCurrentChatSessionInfo: async (): Promise<ChatSessionInfo> => {
    const response = await apiClient.get('/chat/session/info');
    return response.data;
  },

  // 특정 세션 로드
  loadChatSession: async (sessionId: string, provider?: string): Promise<{
    message: string;
    session_info: ChatSessionInfo;
    history: ChatMessage[];
  }> => {
    const response = await apiClient.post('/chat/session/load', {
      session_id: sessionId,
      provider,
    });
    return response.data;
  },

  // 포트폴리오 데이터 업데이트 (CSV 업로드 후 자동 호출)
  updateChatPortfolio: async (): Promise<{ message: string }> => {
    const response = await apiClient.post('/chat/update-portfolio');
    return response.data;
  },
};

// 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    console.error('Error response:', error.response?.data);
    
    // 백엔드에서 제공하는 상세 에러 메시지 우선 사용
    const detailMessage = error.response?.data?.detail;
    
    if (detailMessage) {
      throw new Error(detailMessage);
    }
    
    // 상세 메시지가 없는 경우 상태 코드별 기본 메시지
    if (error.response?.status === 404) {
      throw new Error('요청한 리소스를 찾을 수 없습니다.');
    }
    
    if (error.response?.status === 400) {
      throw new Error('잘못된 요청입니다.');
    }
    
    if (error.response?.status === 503) {
      throw new Error('서비스를 사용할 수 없습니다. 서버 설정을 확인해주세요.');
    }
    
    if (error.code === 'ECONNREFUSED') {
      throw new Error('서버에 연결할 수 없습니다. Backend 서버가 실행 중인지 확인해주세요.');
    }
    
    throw new Error(error.message || '알 수 없는 오류가 발생했습니다.');
  }
);
