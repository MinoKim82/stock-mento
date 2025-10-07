import React from 'react';
import { DollarSign, TrendingUp, PieChart, Wallet } from 'lucide-react';
import type { PortfolioSummary as PortfolioSummaryType } from '../types';

interface PortfolioSummaryProps {
  data: PortfolioSummaryType;
}

const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ data }) => {
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

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          📊 포트폴리오 요약
        </h2>
        <p className="text-gray-600">
          실시간 포트폴리오 현황 및 자산 배분
        </p>
      </div>

      {/* 총 자산 현황 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-blue-100 rounded-lg">
            <Wallet className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">총 자산 현황</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-sm text-gray-600 mb-2">현금 잔고</div>
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(data.total_assets.cash_balance)}
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-sm text-gray-600 mb-2">주식 가치</div>
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(data.total_assets.stock_value)}
            </div>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-6 text-center">
            <div className="text-sm text-blue-600 mb-2">총 자산</div>
            <div className="text-2xl font-bold text-blue-700">
              {formatCurrency(data.total_assets.total_balance)}
            </div>
          </div>
        </div>
        
        <div className="mt-4 text-center text-sm text-gray-500">
          총 {data.total_assets.account_count}개 계좌
        </div>
      </div>

      {/* 주식 포트폴리오 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-green-100 rounded-lg">
            <TrendingUp className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">주식 포트폴리오</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-sm text-gray-600 mb-2">총 투자금</div>
            <div className="text-xl font-bold text-gray-900">
              {formatCurrency(data.stock_portfolio.total_investment)}
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-sm text-gray-600 mb-2">현재 가치</div>
            <div className="text-xl font-bold text-gray-900">
              {formatCurrency(data.stock_portfolio.current_value)}
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-sm text-gray-600 mb-2">미실현 손익</div>
            <div className={`text-xl font-bold ${getColorClass(data.stock_portfolio.unrealized_gain_loss)}`}>
              {formatCurrency(data.stock_portfolio.unrealized_gain_loss)}
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-sm text-gray-600 mb-2">수익률</div>
            <div className={`text-xl font-bold ${getColorClass(data.stock_portfolio.return_rate)}`}>
              {formatPercentage(data.stock_portfolio.return_rate)}
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {data.stock_portfolio.total_holdings}
            </div>
            <div className="text-sm text-gray-600">총 보유 종목</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {data.stock_portfolio.gain_holdings}
            </div>
            <div className="text-sm text-green-600">수익 종목</div>
          </div>
          
          <div className="bg-red-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-red-600">
              {data.stock_portfolio.loss_holdings}
            </div>
            <div className="text-sm text-red-600">손실 종목</div>
          </div>
        </div>
      </div>

      {/* 자산 배분 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-purple-100 rounded-lg">
            <PieChart className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">자산 배분</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <span className="text-lg font-medium text-gray-700">현금</span>
              <span className="text-lg font-bold text-gray-900">
                {data.asset_allocation.cash_ratio.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${data.asset_allocation.cash_ratio}%` }}
              ></div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <span className="text-lg font-medium text-gray-700">주식</span>
              <span className="text-lg font-bold text-gray-900">
                {data.asset_allocation.stock_ratio.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-green-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${data.asset_allocation.stock_ratio}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioSummary;
