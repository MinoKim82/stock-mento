import { useEffect } from 'react';
import { usePortfolio } from './hooks/usePortfolio';
import FileUpload from './components/FileUpload';
import { Tabs, Tab } from './components/Tabs';
import CompactPortfolioSummary from './components/CompactPortfolioSummary';
import AccountPortfolio from './components/AccountPortfolio';
import YearlyReturns from './components/YearlyReturns';
import TransactionHistory from './components/TransactionHistory';
import LlmChat from './components/LlmChat';
import { AlertCircle, RefreshCw, BarChart3, PieChart, TrendingUp, FileText } from 'lucide-react';

function App() {
  const {
    sessionId,
    portfolioSummary,
    portfolioPerformance,
    accountsDetailed,
    isLoading,
    error,
    uploadCsv,
    clearCache,
    refreshData,
    clearError,
    loadTransactionList,
    loadAccountsDetailed,
  } = usePortfolio();


  const handleFileUpload = async (file: File) => {
    try {
      await uploadCsv(file);
    } catch (err) {
      console.error('File upload error:', err);
    }
  };

  const handleRefreshData = async () => {
    try {
      await refreshData();
    } catch (err) {
      console.error('Refresh error:', err);
    }
  };

  // 세션 변경 시 거래 내역과 계좌 상세 정보 로드
  useEffect(() => {
    if (sessionId) {
      loadTransactionList(sessionId);
      loadAccountsDetailed(sessionId);
    }
  }, [sessionId, loadTransactionList, loadAccountsDetailed]);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">
                📊 포트폴리오 분석 대시보드
              </h1>
              {sessionId && (
                <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                  세션 활성
                </span>
              )}
            </div>
            
            {sessionId && (
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleRefreshData}
                  disabled={isLoading}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  <span>새로고침</span>
                </button>
                <button
                  onClick={() => clearCache()}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  새로운 CSV 업로드
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="h-[calc(100vh-64px)] flex">
        {/* 에러 메시지 */}
        {error && (
          <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-96 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between shadow-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-red-700 text-sm">{error}</span>
            </div>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700 font-medium text-sm"
            >
              닫기
            </button>
          </div>
        )}

        {/* 파일 업로드 섹션 */}
        {!sessionId && (
          <div className="w-full flex items-center justify-center">
            <FileUpload onFileUpload={handleFileUpload} isLoading={isLoading} />
          </div>
        )}

        {/* 대시보드 레이아웃 */}
        {sessionId && (
          <div className="w-full flex">
            {/* 메인 포트폴리오 영역 (70%) */}
            <div className="w-[70%] border-r border-gray-200 bg-white">
              <Tabs>
                <Tab 
                  label="포트폴리오 요약" 
                  icon={<PieChart className="w-4 h-4" />}
                >
                  {portfolioSummary && (
                    <CompactPortfolioSummary data={portfolioSummary} />
                  )}
                </Tab>
                
                <Tab 
                  label="계좌별 포트폴리오" 
                  icon={<BarChart3 className="w-4 h-4" />}
                >
                  {accountsDetailed && (
                    <AccountPortfolio data={accountsDetailed} />
                  )}
                </Tab>
                
                <Tab 
                  label="수익" 
                  icon={<TrendingUp className="w-4 h-4" />}
                >
                  {portfolioSummary && portfolioPerformance && (
                    <YearlyReturns 
                      portfolioSummary={portfolioSummary}
                      portfolioPerformance={portfolioPerformance}
                      sessionId={sessionId}
                    />
                  )}
                </Tab>
                
                <Tab 
                  label="전체 거래 내역" 
                  icon={<FileText className="w-4 h-4" />}
                >
                  <TransactionHistory sessionId={sessionId} />
                </Tab>
              </Tabs>
            </div>

            {/* 우측 사이드바 (30%) */}
            <div className="w-[30%] bg-white">
              {/* LLM 채팅 */}
              <div className="h-full p-4">
                <LlmChat sessionId={sessionId} />
              </div>
            </div>
          </div>
        )}

        {/* 로딩 상태 */}
        {isLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="text-lg text-gray-900">데이터를 처리하는 중...</span>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
