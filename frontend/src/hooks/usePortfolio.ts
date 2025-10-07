import { useState, useCallback, useEffect } from 'react';
import { portfolioApi } from '../api/client';
import type { 
  SessionInfo, 
  PortfolioSummary, 
  PortfolioPerformance, 
  PortfolioRisk, 
  CacheInfo,
  TransactionList,
  AccountsDetailed 
} from '../types';

export const usePortfolio = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);
  const [portfolioPerformance, setPortfolioPerformance] = useState<PortfolioPerformance | null>(null);
  const [portfolioRisk, setPortfolioRisk] = useState<PortfolioRisk | null>(null);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);
  const [transactionList, setTransactionList] = useState<TransactionList | null>(null);
  const [accountsDetailed, setAccountsDetailed] = useState<AccountsDetailed | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialCheckDone, setInitialCheckDone] = useState(false);

  const uploadCsv = useCallback(async (file: File) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await portfolioApi.uploadCsv(file);
      
      // 백엔드가 단일 파서를 사용하므로 더미 세션 ID 생성
      const dummySessionId = 'current';
      setSessionId(dummySessionId);
      setSessionInfo({
        session_id: dummySessionId,
        message: response.message || 'CSV 파일이 업로드되었습니다.',
        cache_size: response.file_size || 0,
        total_sessions: 1
      });
      
      // 업로드 후 자동으로 포트폴리오 데이터 로드
      await loadPortfolioData(dummySessionId);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'CSV 업로드 중 오류가 발생했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadPortfolioData = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 병렬로 모든 데이터 로드
      const [summary, performance, risk] = await Promise.all([
        portfolioApi.getPortfolioSummary(sessionId),
        portfolioApi.getPortfolioPerformance(sessionId),
        portfolioApi.getPortfolioRisk(sessionId),
      ]);
      
      setPortfolioSummary(summary);
      setPortfolioPerformance(performance);
      setPortfolioRisk(risk);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '포트폴리오 데이터 로드 중 오류가 발생했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // 앱 시작 시 기존 CSV 파일이 있는지 확인
  useEffect(() => {
    if (!initialCheckDone) {
      const checkExistingData = async () => {
        try {
          const dummySessionId = 'current';
          const summary = await portfolioApi.getPortfolioSummary(dummySessionId);
          
          if (summary) {
            // 기존 데이터가 있으면 자동으로 세션 설정
            setSessionId(dummySessionId);
            setSessionInfo({
              session_id: dummySessionId,
              message: '기존 CSV 파일이 로드되었습니다.',
              cache_size: 0,
              total_sessions: 1
            });
            
            // 모든 데이터 로드
            await loadPortfolioData(dummySessionId);
          }
        } catch (err) {
          // 기존 데이터 없음 - 사용자에게 업로드 대기
          console.log('No existing CSV file found. Please upload a CSV file.');
        } finally {
          setInitialCheckDone(true);
        }
      };
      
      checkExistingData();
    }
  }, [initialCheckDone, loadPortfolioData]);

  const loadFilteredPortfolioData = useCallback(async (
    sessionId: string, 
    filters: { owner?: string; broker?: string; account_type?: string }
  ) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 필터가 적용된 경우 필터링된 데이터 로드, 그렇지 않으면 일반 데이터 로드
      const hasFilters = filters.owner || filters.broker || filters.account_type;
      
      const [summary, performance] = await Promise.all([
        hasFilters 
          ? portfolioApi.getFilteredPortfolioSummary(sessionId, filters)
          : portfolioApi.getPortfolioSummary(sessionId),
        hasFilters 
          ? portfolioApi.getFilteredPortfolioPerformance(sessionId, filters)
          : portfolioApi.getPortfolioPerformance(sessionId),
      ]);
      
      setPortfolioSummary(summary);
      setPortfolioPerformance(performance);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '필터링된 포트폴리오 데이터 로드 중 오류가 발생했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadTransactionList = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const transactions = await portfolioApi.getAllTransactions(sessionId);
      setTransactionList(transactions);
    } catch (err) {
      setError(err instanceof Error ? err.message : '거래 내역 로드 중 오류가 발생했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadAccountsDetailed = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const accounts = await portfolioApi.getAccountsDetailed(sessionId);
      setAccountsDetailed(accounts);
    } catch (err) {
      setError(err instanceof Error ? err.message : '계좌별 상세 정보 로드 중 오류가 발생했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadCacheInfo = useCallback(async () => {
    try {
      const info = await portfolioApi.getCacheInfo();
      setCacheInfo(info);
    } catch (err) {
      setError(err instanceof Error ? err.message : '캐시 정보 로드 중 오류가 발생했습니다.');
    }
  }, []);

  const clearCache = useCallback(async (targetSessionId?: string) => {
    try {
      await portfolioApi.clearCache(targetSessionId);
      
      if (targetSessionId === sessionId || !targetSessionId) {
        // 현재 세션의 캐시를 삭제한 경우 상태 초기화
        setSessionId(null);
        setSessionInfo(null);
        setPortfolioSummary(null);
        setPortfolioPerformance(null);
        setPortfolioRisk(null);
      }
      
      // 캐시 정보 새로고침
      await loadCacheInfo();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '캐시 삭제 중 오류가 발생했습니다.');
    }
  }, [sessionId, loadCacheInfo]);

  const refreshData = useCallback(async () => {
    if (sessionId) {
      await loadPortfolioData(sessionId);
    }
  }, [sessionId, loadPortfolioData]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // 상태
    sessionId,
    sessionInfo,
    portfolioSummary,
    portfolioPerformance,
    portfolioRisk,
    cacheInfo,
    transactionList,
    accountsDetailed,
    isLoading,
    error,
    
    // 액션
    uploadCsv,
    loadPortfolioData,
    loadFilteredPortfolioData,
    loadTransactionList,
    loadAccountsDetailed,
    loadCacheInfo,
    clearCache,
    refreshData,
    clearError,
  };
};
