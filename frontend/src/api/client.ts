import axios from 'axios';
import type { 
  SessionInfo, 
  CacheInfo,
  TransactionList,
  ParsedData
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
};

// 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response?.status === 404) {
      throw new Error('세션을 찾을 수 없습니다. CSV 파일을 다시 업로드해주세요.');
    }
    
    if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || '잘못된 요청입니다.');
    }
    
    if (error.code === 'ECONNREFUSED') {
      throw new Error('서버에 연결할 수 없습니다. Backend 서버가 실행 중인지 확인해주세요.');
    }
    
    throw new Error(error.response?.data?.detail || error.message || '알 수 없는 오류가 발생했습니다.');
  }
);
