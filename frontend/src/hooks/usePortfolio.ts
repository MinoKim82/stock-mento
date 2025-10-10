import { useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';
import type { 
  SessionInfo, 
  PortfolioSummary, 
  PortfolioPerformance, 
  PortfolioRisk, 
  CacheInfo,
  TransactionList,
  AccountsDetailed,
  YearlyReturnsDetail
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
  const [yearlyReturns, setYearlyReturns] = useState<YearlyReturnsDetail[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialCheckDone, setInitialCheckDone] = useState(false);

  const uploadCsv = useCallback(async (file: File) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.uploadCsv(file);
      
      // 백엔드가 단일 파서를 사용하므로 더미 세션 ID 생성
      const dummySessionId = 'current';
      setSessionId(dummySessionId);
      setSessionInfo({
        session_id: dummySessionId,
        message: response.message || 'CSV 파일이 업로드되었습니다.',
        cache_size: 0,
        total_sessions: 1
      });
      
      // 🚀 파싱된 JSON 데이터를 한 번에 로드
      const parsedData = await api.getParsedData();
      
      // 모든 데이터 즉시 설정
      if (parsedData.portfolio_summary) {
        setPortfolioSummary(parsedData.portfolio_summary);
      }
      if (parsedData.portfolio_performance) {
        setPortfolioPerformance(parsedData.portfolio_performance);
      }
      if (parsedData.portfolio_risk) {
        setPortfolioRisk(parsedData.portfolio_risk);
      }
      if (parsedData.accounts_detailed) {
        setAccountsDetailed(parsedData.accounts_detailed);
      }
      if (parsedData.yearly_returns) {
        setYearlyReturns(parsedData.yearly_returns);
      }
      
      // 거래 내역은 조금 나중에 로드
      setTimeout(() => {
        api.getAllTransactions(dummySessionId)
          .then(transactions => setTransactionList(transactions))
          .catch(err => console.error('거래 내역 로드 실패:', err));
      }, 100);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'CSV 업로드 중 오류가 발생했습니다.');
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
          // 먼저 캐시 정보를 확인하여 데이터가 있는지 체크
          const cacheInfo = await api.getCacheInfo();
          
          if (cacheInfo.has_data && cacheInfo.has_parsed_data) {
            const dummySessionId = 'current';
            
            // 즉시 세션 설정 (화면 전환)
            setSessionId(dummySessionId);
            setSessionInfo({
              session_id: dummySessionId,
              message: '기존 CSV 파일이 로드되었습니다.',
              cache_size: cacheInfo.total_cache_size,
              total_sessions: 1
            });
            
            // 초기 체크 완료 표시 (화면 전환 트리거)
            setInitialCheckDone(true);
            
            // 🚀 파싱된 JSON 데이터를 한 번에 로드
            const parsedData = await api.getParsedData();
            
            // 모든 데이터 즉시 설정
            if (parsedData.portfolio_summary) {
              setPortfolioSummary(parsedData.portfolio_summary);
            }
            if (parsedData.portfolio_performance) {
              setPortfolioPerformance(parsedData.portfolio_performance);
            }
            if (parsedData.portfolio_risk) {
              setPortfolioRisk(parsedData.portfolio_risk);
            }
            if (parsedData.accounts_detailed) {
              setAccountsDetailed(parsedData.accounts_detailed);
            }
            if (parsedData.yearly_returns) {
              setYearlyReturns(parsedData.yearly_returns);
            }
            
            // 거래 내역은 조금 나중에 로드 (덜 중요)
            setTimeout(() => {
              api.getAllTransactions(dummySessionId)
                .then(transactions => setTransactionList(transactions))
                .catch(err => console.error('거래 내역 로드 실패:', err));
            }, 100);
          } else {
            setInitialCheckDone(true);
          }
        } catch (err) {
          // 기존 데이터 없음 - 사용자에게 업로드 대기
          console.log('No existing CSV file found. Please upload a CSV file.');
          setInitialCheckDone(true);
        }
      };
      
      checkExistingData();
    }
  }, [initialCheckDone]);

  const loadCacheInfo = useCallback(async () => {
    try {
      const info = await api.getCacheInfo();
      setCacheInfo(info);
    } catch (err) {
      setError(err instanceof Error ? err.message : '캐시 정보 로드 중 오류가 발생했습니다.');
    }
  }, []);

  const clearCache = useCallback(async (targetSessionId?: string) => {
    try {
      await api.clearCache(targetSessionId);
      
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
      try {
        const parsedData = await api.getParsedData();
        
        if (parsedData.portfolio_summary) setPortfolioSummary(parsedData.portfolio_summary);
        if (parsedData.portfolio_performance) setPortfolioPerformance(parsedData.portfolio_performance);
        if (parsedData.portfolio_risk) setPortfolioRisk(parsedData.portfolio_risk);
        if (parsedData.accounts_detailed) setAccountsDetailed(parsedData.accounts_detailed);
        if (parsedData.yearly_returns) setYearlyReturns(parsedData.yearly_returns);
        
        setTimeout(() => {
          api.getAllTransactions(sessionId)
            .then(transactions => setTransactionList(transactions))
            .catch(err => console.error('거래 내역 로드 실패:', err));
        }, 100);
      } catch (err) {
        setError(err instanceof Error ? err.message : '데이터 새로고침 중 오류가 발생했습니다.');
      }
    }
  }, [sessionId]);

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
    yearlyReturns,
    isLoading,
    error,
    
    // 액션
    uploadCsv,
    loadCacheInfo,
    clearCache,
    refreshData,
    clearError,
  };
};
