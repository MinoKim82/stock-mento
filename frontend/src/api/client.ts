import axios from 'axios';
import type { 
  SessionInfo, 
  PortfolioSummary, 
  PortfolioPerformance, 
  PortfolioRisk, 
  CacheInfo,
  FilterOptions,
  TransactionList,
  AccountsDetailed 
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
export const portfolioApi = {
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

  // 포트폴리오 요약
  getPortfolioSummary: async (sessionId: string): Promise<PortfolioSummary> => {
    const response = await apiClient.get(`/portfolio/summary/${sessionId}`);
    return response.data;
  },

  // 포트폴리오 성과 분석
  getPortfolioPerformance: async (sessionId: string): Promise<PortfolioPerformance> => {
    const response = await apiClient.get(`/portfolio/performance/${sessionId}`);
    return response.data;
  },

  // 포트폴리오 위험 분석
  getPortfolioRisk: async (sessionId: string): Promise<PortfolioRisk> => {
    const response = await apiClient.get(`/portfolio/risk/${sessionId}`);
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

  // 필터 옵션 조회
  getFilterOptions: async (sessionId: string): Promise<FilterOptions> => {
    const response = await apiClient.get(`/portfolio/filters/${sessionId}`);
    return response.data;
  },

  // 필터링된 포트폴리오 요약
  getFilteredPortfolioSummary: async (
    sessionId: string, 
    filters: { owner?: string; broker?: string; account_type?: string }
  ): Promise<PortfolioSummary> => {
    const params = new URLSearchParams();
    if (filters.owner) params.append('owner', filters.owner);
    if (filters.broker) params.append('broker', filters.broker);
    if (filters.account_type) params.append('account_type', filters.account_type);
    
    const response = await apiClient.get(`/portfolio/summary-filtered/${sessionId}?${params.toString()}`);
    return response.data;
  },

  // 필터링된 포트폴리오 성과 분석
  getFilteredPortfolioPerformance: async (
    sessionId: string, 
    filters: { owner?: string; broker?: string; account_type?: string }
  ): Promise<PortfolioPerformance> => {
    const params = new URLSearchParams();
    if (filters.owner) params.append('owner', filters.owner);
    if (filters.broker) params.append('broker', filters.broker);
    if (filters.account_type) params.append('account_type', filters.account_type);
    
    const response = await apiClient.get(`/portfolio/performance-filtered/${sessionId}?${params.toString()}`);
    return response.data;
  },

  // 전체 거래 내역 조회
  getAllTransactions: async (sessionId: string): Promise<TransactionList> => {
    const response = await apiClient.get(`/transactions/${sessionId}`);
    return response.data;
  },

  // 계좌별 상세 정보 조회
  getAccountsDetailed: async (sessionId: string): Promise<AccountsDetailed> => {
    const response = await apiClient.get(`/portfolio/accounts-detailed/${sessionId}`);
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
