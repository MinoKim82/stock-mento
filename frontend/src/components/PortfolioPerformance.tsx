import React from 'react';
import { TrendingUp, TrendingDown, Award, BarChart3 } from 'lucide-react';
import type { PortfolioPerformance as PortfolioPerformanceType } from '../types';

interface PortfolioPerformanceProps {
  data: PortfolioPerformanceType;
}

const PortfolioPerformance: React.FC<PortfolioPerformanceProps> = ({ data }) => {
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
    if (value > 0) return 'bg-green-50';
    if (value < 0) return 'bg-red-50';
    return 'bg-gray-50';
  };

  const renderTopPerformers = () => {
    if (data.top_performers.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          상위 성과 종목이 없습니다.
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {data.top_performers.map((performer, index) => (
          <div key={`${performer.security}-${performer.account}`} 
               className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-8 h-8 bg-green-100 text-green-600 rounded-full text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{performer.security}</div>
                  <div className="text-sm text-gray-500">{performer.account}</div>
                </div>
              </div>
              <div className="text-right">
                <div className={`font-bold ${getColorClass(performer.gain_loss)}`}>
                  {formatCurrency(performer.gain_loss)}
                </div>
                <div className={`text-sm ${getColorClass(performer.return_rate)}`}>
                  {formatPercentage(performer.return_rate)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderBottomPerformers = () => {
    if (data.bottom_performers.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          하위 성과 종목이 없습니다.
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {data.bottom_performers.map((performer, index) => (
          <div key={`${performer.security}-${performer.account}`} 
               className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-8 h-8 bg-red-100 text-red-600 rounded-full text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{performer.security}</div>
                  <div className="text-sm text-gray-500">{performer.account}</div>
                </div>
              </div>
              <div className="text-right">
                <div className={`font-bold ${getColorClass(performer.gain_loss)}`}>
                  {formatCurrency(performer.gain_loss)}
                </div>
                <div className={`text-sm ${getColorClass(performer.return_rate)}`}>
                  {formatPercentage(performer.return_rate)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderAccountPerformance = () => {
    const accounts = Object.entries(data.account_performance);
    
    if (accounts.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          계좌 성과 데이터가 없습니다.
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {accounts.map(([account, performance]) => (
          <div key={account} className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-900">{account}</h4>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getBgColorClass(performance.return_rate)} ${getColorClass(performance.return_rate)}`}>
                {formatPercentage(performance.return_rate)}
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{performance.holdings_count}</div>
                <div className="text-sm text-gray-600">보유 종목</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {formatCurrency(performance.total_investment)}
                </div>
                <div className="text-sm text-gray-600">총 투자금</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {formatCurrency(performance.total_value)}
                </div>
                <div className="text-sm text-gray-600">현재 가치</div>
              </div>
              <div className="text-center">
                <div className={`text-lg font-semibold ${getColorClass(performance.total_gain_loss)}`}>
                  {formatCurrency(performance.total_gain_loss)}
                </div>
                <div className="text-sm text-gray-600">손익</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          📈 포트폴리오 성과 분석
        </h2>
        <p className="text-gray-600">
          상위/하위 성과 종목 및 계좌별 성과 분석
        </p>
      </div>

      {/* 상위 성과 종목 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-green-100 rounded-lg">
            <Award className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">🏆 상위 성과 종목</h3>
        </div>
        {renderTopPerformers()}
      </div>

      {/* 하위 성과 종목 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-red-100 rounded-lg">
            <TrendingDown className="w-6 h-6 text-red-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">📉 하위 성과 종목</h3>
        </div>
        {renderBottomPerformers()}
      </div>

      {/* 계좌별 성과 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-blue-100 rounded-lg">
            <BarChart3 className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">📊 계좌별 성과 분석</h3>
        </div>
        {renderAccountPerformance()}
      </div>
    </div>
  );
};

export default PortfolioPerformance;
