import { useState, useEffect } from 'react';
import { Calendar, TrendingUp, DollarSign, Coins, PiggyBank, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../api/client';
import type { YearlyReturnsDetail, PortfolioSummary, PortfolioPerformance } from '../types';

interface YearlyReturnsProps {
  sessionId: string;
  portfolioSummary?: PortfolioSummary;
  portfolioPerformance?: PortfolioPerformance;
}

const YearlyReturns: React.FC<YearlyReturnsProps> = ({ sessionId }) => {
  const [yearlyData, setYearlyData] = useState<YearlyReturnsDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedYears, setExpandedYears] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadYearlyReturns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const loadYearlyReturns = async () => {
    try {
      setLoading(true);
      const data = await api.getYearlyReturns(sessionId);
      setYearlyData(data.sort((a: YearlyReturnsDetail, b: YearlyReturnsDetail) => b.year - a.year)); // 최신 연도 먼저
    } catch (err) {
      setError(err instanceof Error ? err.message : '수익 내역을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(amount);
  };

  const toggleYear = (year: number) => {
    const newExpanded = new Set(expandedYears);
    if (newExpanded.has(year)) {
      newExpanded.delete(year);
    } else {
      newExpanded.add(year);
    }
    setExpandedYears(newExpanded);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  // 전체 수익 계산
  const totalReturns = yearlyData.reduce((sum, year) => ({
    dividend: sum.dividend + year.total_dividend,
    sell_profit: sum.sell_profit + year.total_sell_profit,
    interest: sum.interest + year.total_interest,
    total: sum.total + year.total_returns,
  }), { dividend: 0, sell_profit: 0, interest: 0, total: 0 });

  return (
    <div className="p-6 space-y-6 overflow-auto h-full">
      {/* 헤더 */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">수익 내역</h2>
        <p className="text-sm text-gray-600 mt-1">배당금, 매도 차익, 이자 수익</p>
      </div>

      {/* 전체 수익 요약 */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <DollarSign className="w-5 h-5 mr-2 text-blue-600" />
          전체 수익 요약
        </h3>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <PiggyBank className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-gray-700">배당금</span>
              </div>
            </div>
            <div className="text-xl font-bold text-green-600">
              {formatCurrency(totalReturns.dividend)}
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">매도 차익</span>
              </div>
            </div>
            <div className={`text-xl font-bold ${totalReturns.sell_profit >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
              {formatCurrency(totalReturns.sell_profit)}
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Coins className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-gray-700">이자 수익</span>
              </div>
            </div>
            <div className="text-xl font-bold text-purple-600">
              {formatCurrency(totalReturns.interest)}
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <DollarSign className="w-4 h-4 text-indigo-600" />
                <span className="text-sm font-medium text-gray-700">총 수익</span>
              </div>
            </div>
            <div className="text-xl font-bold text-indigo-600">
              {formatCurrency(totalReturns.total)}
            </div>
          </div>
        </div>
      </div>

      {/* 연도별 수익 내역 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Calendar className="w-5 h-5 mr-2 text-gray-600" />
          연도별 수익 내역
        </h3>

        <div className="space-y-3">
          {yearlyData.map((yearData) => (
            <div key={yearData.year} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              {/* 연도 헤더 */}
              <button
                onClick={() => toggleYear(yearData.year)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <Calendar className="w-5 h-5 text-gray-600" />
                  <span className="font-semibold text-gray-900">{yearData.year}년</span>
                  <span className="text-sm text-gray-600">
                    총 수익: <span className="font-medium text-indigo-600">{formatCurrency(yearData.total_returns)}</span>
                  </span>
                </div>
                {expandedYears.has(yearData.year) ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>

              {/* 연도별 상세 내역 */}
              {expandedYears.has(yearData.year) && (
                <div className="px-4 pb-4 border-t border-gray-100">
                  {/* 수익 요약 */}
                  <div className="grid grid-cols-3 gap-3 mt-3 mb-4">
                    <div className="bg-green-50 rounded-lg p-3">
                      <div className="text-xs text-gray-600 mb-1">배당금</div>
                      <div className="font-semibold text-green-700">
                        {formatCurrency(yearData.total_dividend)}
                      </div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3">
                      <div className="text-xs text-gray-600 mb-1">매도 차익</div>
                      <div className={`font-semibold ${yearData.total_sell_profit >= 0 ? 'text-blue-700' : 'text-red-700'}`}>
                        {formatCurrency(yearData.total_sell_profit)}
                      </div>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-3">
                      <div className="text-xs text-gray-600 mb-1">이자 수익</div>
                      <div className="font-semibold text-purple-700">
                        {formatCurrency(yearData.total_interest)}
                      </div>
                    </div>
                  </div>

                  {/* 소유자 및 계좌 타입별 종목 수익 */}
                  {Object.keys(yearData.by_owner_and_account).length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-3">계좌별 종목 수익</h4>
                      <div className="space-y-3">
                        {Object.entries(yearData.by_owner_and_account).map(([owner, accountTypes]) => (
                          <div key={owner} className="border border-gray-200 rounded-lg overflow-hidden">
                            {/* 소유자 헤더 */}
                            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-3 py-2 border-b border-gray-200">
                              <span className="font-semibold text-gray-900">👤 {owner}</span>
                            </div>
                            
                            {/* 계좌 타입별 */}
                            <div className="p-3 space-y-3">
                              {Object.entries(accountTypes).map(([accountType, accounts]) => {
                                // 계좌 타입 총합 계산
                                const accountTypeTotal = Object.values(accounts).reduce(
                                  (sum: number, acc: any) => sum + (acc.total || 0),
                                  0
                                );
                                
                                return (
                                  <div key={accountType} className="bg-white rounded-lg border border-gray-100">
                                    {/* 계좌 타입 헤더 */}
                                    <div className="bg-gray-50 px-3 py-2 border-b border-gray-100 flex items-center justify-between">
                                      <span className="text-sm font-medium text-gray-700">📁 {accountType}</span>
                                      <span className="text-sm font-semibold text-indigo-600">
                                        {formatCurrency(accountTypeTotal)}
                                      </span>
                                    </div>
                                    
                                    {/* 계좌별 수익 */}
                                    <div className="p-2 space-y-3">
                                      {Object.entries(accounts)
                                        .sort(([, a]: [string, any], [, b]: [string, any]) => (b.total || 0) - (a.total || 0))
                                        .map(([accountName, accountData]: [string, any]) => (
                                          <div key={accountName} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                                            {/* 계좌 헤더 */}
                                            <div className="flex items-center justify-between mb-2">
                                              <span className="text-sm font-semibold text-gray-900">{accountName}</span>
                                              <span className="text-sm font-bold text-indigo-600">
                                                {formatCurrency(accountData.total)}
                                              </span>
                                            </div>
                                            
                                            {/* 배당/매도/이자 요약 */}
                                            <div className="flex items-center space-x-3 text-xs text-gray-600 mb-2">
                                              {accountData.dividend > 0 && (
                                                <div className="flex items-center space-x-1">
                                                  <PiggyBank className="w-3 h-3 text-green-600" />
                                                  <span>배당: {formatCurrency(accountData.dividend)}</span>
                                                </div>
                                              )}
                                              {accountData.sell_profit !== 0 && (
                                                <div className="flex items-center space-x-1">
                                                  <TrendingUp className="w-3 h-3 text-blue-600" />
                                                  <span className={accountData.sell_profit >= 0 ? 'text-blue-600' : 'text-red-600'}>
                                                    매도: {formatCurrency(accountData.sell_profit)}
                                                  </span>
                                                </div>
                                              )}
                                              {accountData.interest > 0 && (
                                                <div className="flex items-center space-x-1">
                                                  <Coins className="w-3 h-3 text-purple-600" />
                                                  <span>이자: {formatCurrency(accountData.interest)}</span>
                                                </div>
                                              )}
                                            </div>
                                            
                                            {/* 종목별 상세 */}
                                            {accountData.securities && Object.keys(accountData.securities).length > 0 && (
                                              <div className="mt-2 pt-2 border-t border-gray-200 space-y-1">
                                                {Object.entries(accountData.securities)
                                                  .sort(([, a]: [string, any], [, b]: [string, any]) => 
                                                    (b.dividend + b.sell_profit) - (a.dividend + a.sell_profit)
                                                  )
                                                  .map(([security, secData]: [string, any]) => (
                                                    <div key={security} className="text-xs bg-white rounded p-2">
                                                      <div className="flex items-center justify-between mb-1">
                                                        <span className="font-medium text-gray-800">{security}</span>
                                                        <span className="font-semibold text-gray-900">
                                                          {formatCurrency(secData.dividend + secData.sell_profit)}
                                                        </span>
                                                      </div>
                                                      <div className="flex items-center space-x-2 text-xs text-gray-600">
                                                        {secData.dividend > 0 && (
                                                          <span className="text-green-600">
                                                            배당 {formatCurrency(secData.dividend)}
                                                          </span>
                                                        )}
                                                        {secData.sell_profit !== 0 && (
                                                          <span className={secData.sell_profit >= 0 ? 'text-blue-600' : 'text-red-600'}>
                                                            매도 {formatCurrency(secData.sell_profit)}
                                                            {secData.sell_shares > 0 && ` (${secData.sell_shares}주)`}
                                                          </span>
                                                        )}
                                                      </div>
                                                    </div>
                                                  ))}
                                              </div>
                                            )}
                                          </div>
                                        ))}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default YearlyReturns;
