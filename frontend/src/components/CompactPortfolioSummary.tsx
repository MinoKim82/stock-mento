import React from 'react';
import { DollarSign, TrendingUp, PieChart, Wallet } from 'lucide-react';
import type { PortfolioSummary as PortfolioSummaryType } from '../types';

interface CompactPortfolioSummaryProps {
  data: PortfolioSummaryType;
}

const CompactPortfolioSummary: React.FC<CompactPortfolioSummaryProps> = ({ data }) => {
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
    <div className="p-4 space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">포트폴리오 요약</h3>
        <p className="text-sm text-gray-600">실시간 포트폴리오 현황</p>
      </div>

      {/* 총 자산 현황 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <Wallet className="w-5 h-5 text-blue-600" />
          <h4 className="font-semibold text-gray-900">총 자산</h4>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">현금</span>
            <span className="font-medium">{formatCurrency(data.total_assets.cash_balance)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">주식</span>
            <span className="font-medium">{formatCurrency(data.total_assets.stock_value)}</span>
          </div>
          <div className="flex justify-between text-sm pt-2 border-t border-gray-200">
            <span className="font-medium text-gray-900">총 자산</span>
            <span className="font-bold text-blue-600">{formatCurrency(data.total_assets.total_balance)}</span>
          </div>
        </div>
      </div>

      {/* 주식 포트폴리오 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <TrendingUp className="w-5 h-5 text-green-600" />
          <h4 className="font-semibold text-gray-900">주식 포트폴리오</h4>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">투자금</span>
            <span className="font-medium">{formatCurrency(data.stock_portfolio.total_investment)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">현재가치</span>
            <span className="font-medium">{formatCurrency(data.stock_portfolio.current_value)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">손익</span>
            <span className={`font-medium ${getColorClass(data.stock_portfolio.unrealized_gain_loss)}`}>
              {formatCurrency(data.stock_portfolio.unrealized_gain_loss)}
            </span>
          </div>
          <div className="flex justify-between text-sm pt-2 border-t border-gray-200">
            <span className="font-medium text-gray-900">수익률</span>
            <span className={`font-bold ${getColorClass(data.stock_portfolio.return_rate)}`}>
              {formatPercentage(data.stock_portfolio.return_rate)}
            </span>
          </div>
        </div>
      </div>

      {/* 보유 종목 현황 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <PieChart className="w-5 h-5 text-purple-600" />
          <h4 className="font-semibold text-gray-900">보유 종목</h4>
        </div>
        
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-lg font-bold text-gray-900">{data.stock_portfolio.total_holdings}</div>
            <div className="text-xs text-gray-600">총 종목</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-lg font-bold text-green-600">{data.stock_portfolio.gain_holdings}</div>
            <div className="text-xs text-green-600">수익</div>
          </div>
          <div className="bg-red-50 rounded-lg p-3">
            <div className="text-lg font-bold text-red-600">{data.stock_portfolio.loss_holdings}</div>
            <div className="text-xs text-red-600">손실</div>
          </div>
        </div>
      </div>

      {/* 자산 배분 */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <PieChart className="w-5 h-5 text-indigo-600" />
          <h4 className="font-semibold text-gray-900">자산 배분</h4>
        </div>
        
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">현금</span>
              <span className="font-medium">{data.asset_allocation.cash_ratio.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${data.asset_allocation.cash_ratio}%` }}
              ></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">주식</span>
              <span className="font-medium">{data.asset_allocation.stock_ratio.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${data.asset_allocation.stock_ratio}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompactPortfolioSummary;
