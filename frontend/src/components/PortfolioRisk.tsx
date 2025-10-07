import React from 'react';
import { AlertTriangle, Target, TrendingUp, TrendingDown, Shield } from 'lucide-react';
import type { PortfolioRisk as PortfolioRiskType } from '../types';

interface PortfolioRiskProps {
  data: PortfolioRiskType;
}

const PortfolioRisk: React.FC<PortfolioRiskProps> = ({ data }) => {
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

  const getRiskLevel = (ratio: number) => {
    if (ratio >= 70) return { level: 'HIGH', color: 'text-red-600 bg-red-100' };
    if (ratio >= 50) return { level: 'MEDIUM', color: 'text-yellow-600 bg-yellow-100' };
    return { level: 'LOW', color: 'text-green-600 bg-green-100' };
  };

  const concentrationRisk = getRiskLevel(data.concentration_risk.top5_concentration_ratio);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          ⚠️ 포트폴리오 위험 분석
        </h2>
        <p className="text-gray-600">
          위험 지표 및 집중도 분석을 통한 포트폴리오 리스크 평가
        </p>
      </div>

      {/* 위험 지표 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-orange-100 rounded-lg">
            <Shield className="w-6 h-6 text-orange-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">🛡️ 위험 지표</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {data.risk_metrics.total_holdings}
            </div>
            <div className="text-sm text-gray-600">총 보유 종목</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {data.risk_metrics.gain_holdings_count}
            </div>
            <div className="text-sm text-green-600">수익 종목</div>
          </div>
          
          <div className="bg-red-50 rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">
              {data.risk_metrics.loss_holdings_count}
            </div>
            <div className="text-sm text-red-600">손실 종목</div>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {data.risk_metrics.win_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-blue-600">승률</div>
          </div>
        </div>
      </div>

      {/* 손익 분석 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-purple-100 rounded-lg">
            <Target className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">🎯 손익 분석</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-green-50 rounded-lg p-6 text-center">
            <div className="text-2xl font-bold text-green-600 mb-2">
              {formatCurrency(data.gain_loss_analysis.total_gain)}
            </div>
            <div className="text-sm text-green-600">총 수익</div>
          </div>
          
          <div className="bg-red-50 rounded-lg p-6 text-center">
            <div className="text-2xl font-bold text-red-600 mb-2">
              {formatCurrency(Math.abs(data.gain_loss_analysis.total_loss))}
            </div>
            <div className="text-sm text-red-600">총 손실</div>
          </div>
          
          <div className={`rounded-lg p-6 text-center ${getColorClass(data.gain_loss_analysis.net_gain_loss)}`}>
            <div className={`text-2xl font-bold mb-2 ${getColorClass(data.gain_loss_analysis.net_gain_loss)}`}>
              {formatCurrency(data.gain_loss_analysis.net_gain_loss)}
            </div>
            <div className={`text-sm ${getColorClass(data.gain_loss_analysis.net_gain_loss)}`}>
              순 손익
            </div>
          </div>
        </div>
      </div>

      {/* 극값 성과 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-yellow-100 rounded-lg">
            <AlertTriangle className="w-6 h-6 text-yellow-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">⚡ 극값 성과</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 최대 수익 */}
          <div className="bg-green-50 rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-4">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h4 className="text-lg font-semibold text-green-700">최대 수익</h4>
            </div>
            
            {data.extreme_performers.max_gain ? (
              <div className="space-y-2">
                <div className="font-bold text-green-600">
                  {data.extreme_performers.max_gain.security}
                </div>
                <div className="text-sm text-gray-600">
                  {data.extreme_performers.max_gain.account}
                </div>
                <div className="text-xl font-bold text-green-600">
                  {formatCurrency(data.extreme_performers.max_gain.gain_loss)}
                </div>
                <div className="text-sm text-green-600">
                  {formatPercentage(data.extreme_performers.max_gain.return_rate)}
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-center py-4">
                수익 종목이 없습니다.
              </div>
            )}
          </div>
          
          {/* 최대 손실 */}
          <div className="bg-red-50 rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-4">
              <TrendingDown className="w-5 h-5 text-red-600" />
              <h4 className="text-lg font-semibold text-red-700">최대 손실</h4>
            </div>
            
            {data.extreme_performers.max_loss ? (
              <div className="space-y-2">
                <div className="font-bold text-red-600">
                  {data.extreme_performers.max_loss.security}
                </div>
                <div className="text-sm text-gray-600">
                  {data.extreme_performers.max_loss.account}
                </div>
                <div className="text-xl font-bold text-red-600">
                  {formatCurrency(data.extreme_performers.max_loss.gain_loss)}
                </div>
                <div className="text-sm text-red-600">
                  {formatPercentage(data.extreme_performers.max_loss.return_rate)}
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-center py-4">
                손실 종목이 없습니다.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 집중도 위험 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-indigo-100 rounded-lg">
            <AlertTriangle className="w-6 h-6 text-indigo-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">🎯 집중도 위험</h3>
        </div>
        
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-lg font-medium text-gray-700">상위 5개 종목 집중도</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${concentrationRisk.color}`}>
              {concentrationRisk.level} ({data.concentration_risk.top5_concentration_ratio.toFixed(1)}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div 
              className={`h-4 rounded-full transition-all duration-300 ${
                concentrationRisk.level === 'HIGH' ? 'bg-red-500' :
                concentrationRisk.level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${data.concentration_risk.top5_concentration_ratio}%` }}
            ></div>
          </div>
        </div>
        
        <div className="space-y-3">
          <h4 className="text-lg font-semibold text-gray-900">상위 5개 보유 종목</h4>
          {data.concentration_risk.top5_holdings.map((holding, index) => (
            <div key={`${holding.security}-${holding.account}`} 
                 className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full text-sm font-bold">
                    {index + 1}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{holding.security}</div>
                    <div className="text-sm text-gray-500">{holding.account}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900">
                    {formatCurrency(holding.value)}
                  </div>
                  <div className="text-sm text-indigo-600">
                    {holding.ratio.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PortfolioRisk;
