import React from 'react';
import { Calendar, TrendingUp, TrendingDown, Target, BarChart3 } from 'lucide-react';
import type { PortfolioSummary as PortfolioSummaryType, PortfolioPerformance as PortfolioPerformanceType } from '../types';

interface YearlyReturnsProps {
  portfolioSummary: PortfolioSummaryType;
  portfolioPerformance: PortfolioPerformanceType;
}

const YearlyReturns: React.FC<YearlyReturnsProps> = ({ 
  portfolioSummary, 
  portfolioPerformance 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getColorClass = (value: number) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getBgColorClass = (value: number) => {
    if (value > 0) return 'bg-green-50 border-green-200';
    if (value < 0) return 'bg-red-50 border-red-200';
    return 'bg-gray-50 border-gray-200';
  };

  // 현재 연도 계산
  const currentYear = new Date().getFullYear();
  
  // 승률 계산
  const winRate = portfolioPerformance.account_performance ? 
    Object.values(portfolioPerformance.account_performance).reduce((acc, perf) => acc + (perf.return_rate > 0 ? 1 : 0), 0) / 
    Object.keys(portfolioPerformance.account_performance).length * 100 : 0;

  return (
    <div className="p-4 space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{currentYear}년 수익 현황</h3>
        <p className="text-sm text-gray-600">올해 투자 성과 분석</p>
      </div>

      {/* 전체 수익률 */}
      <div className={`border rounded-lg p-4 ${getBgColorClass(portfolioSummary.stock_portfolio.return_rate)}`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-gray-600" />
            <span className="font-medium text-gray-900">전체 수익률</span>
          </div>
          <div className={`text-xl font-bold ${getColorClass(portfolioSummary.stock_portfolio.return_rate)}`}>
            {formatPercentage(portfolioSummary.stock_portfolio.return_rate)}
          </div>
        </div>
        <div className="text-sm text-gray-600">
          {formatCurrency(portfolioSummary.stock_portfolio.unrealized_gain_loss)}
        </div>
      </div>

      {/* 투자 현황 */}
      <div className="grid grid-cols-1 gap-3">
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">총 투자금</span>
            </div>
            <span className="font-semibold text-gray-900">
              {formatCurrency(portfolioSummary.stock_portfolio.total_investment)}
            </span>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-gray-700">현재 가치</span>
            </div>
            <span className="font-semibold text-gray-900">
              {formatCurrency(portfolioSummary.stock_portfolio.current_value)}
            </span>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-gray-700">승률</span>
            </div>
            <span className="font-semibold text-gray-900">
              {winRate.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* 상위/하위 성과 */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900">주요 성과</h4>
        
        {portfolioPerformance.top_performers.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-800">최고 수익 종목</span>
            </div>
            <div className="text-sm">
              <div className="font-medium text-green-900">
                {portfolioPerformance.top_performers[0].security}
              </div>
              <div className="text-green-700">
                {formatPercentage(portfolioPerformance.top_performers[0].return_rate)}
              </div>
            </div>
          </div>
        )}

        {portfolioPerformance.bottom_performers.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingDown className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-800">최저 수익 종목</span>
            </div>
            <div className="text-sm">
              <div className="font-medium text-red-900">
                {portfolioPerformance.bottom_performers[0].security}
              </div>
              <div className="text-red-700">
                {formatPercentage(portfolioPerformance.bottom_performers[0].return_rate)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 자산 배분 */}
      <div className="space-y-2">
        <h4 className="font-medium text-gray-900">자산 배분</h4>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>현금</span>
            <span>{portfolioSummary.asset_allocation.cash_ratio.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${portfolioSummary.asset_allocation.cash_ratio}%` }}
            ></div>
          </div>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>주식</span>
            <span>{portfolioSummary.asset_allocation.stock_ratio.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full"
              style={{ width: `${portfolioSummary.asset_allocation.stock_ratio}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YearlyReturns;
