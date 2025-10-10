import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, PieChart, Wallet, User, Building2 } from 'lucide-react';
import { api } from '../api/client';
import type { PortfolioSummary as PortfolioSummaryType, AccountsDetailed } from '../types';

interface CompactPortfolioSummaryProps {
  data: PortfolioSummaryType;
}

const CompactPortfolioSummary: React.FC<CompactPortfolioSummaryProps> = ({ data }) => {
  const [accountsData, setAccountsData] = useState<AccountsDetailed | null>(null);

  useEffect(() => {
    // 계좌별 상세 정보 로드
    const loadAccountsData = async () => {
      try {
        const accounts = await api.getAccountsDetailed('current');
        setAccountsData(accounts);
      } catch (error) {
        console.error('계좌 데이터 로드 실패:', error);
      }
    };
    loadAccountsData();
  }, []);
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

  // 소유자 우선순위
  const getOwnerOrder = (owner: string): number => {
    const order: { [key: string]: number } = {
      '혜란': 1,
      '유신': 2,
      '민호': 3
    };
    return order[owner] || 999;
  };

  // 계좌타입 우선순위
  const getAccountTypeOrder = (type: string): number => {
    const order: { [key: string]: number } = {
      '연금저축': 1,
      'ISA': 2,
      '종합매매': 3,
      '종합매매 해외': 4
    };
    return order[type] || 999;
  };

  // 사람별/계좌타입별 데이터 계산
  const calculateOwnerSummary = () => {
    if (!accountsData) return [];

    const ownerSummary: {
      [owner: string]: {
        [accountType: string]: {
          cash_balance: number;
          stock_value: number;
          total_balance: number;
          total_investment: number;
          total_gain_loss: number;
          account_count: number;
        };
      };
    } = {};

    Object.entries(accountsData.accounts_by_owner_and_type).forEach(([owner, accountTypes]) => {
      if (!ownerSummary[owner]) {
        ownerSummary[owner] = {};
      }

      Object.entries(accountTypes).forEach(([accountType, accounts]) => {
        const summary = accounts.reduce((acc, account) => ({
          cash_balance: acc.cash_balance + account.balance,
          stock_value: acc.stock_value + account.stock_value,
          total_balance: acc.total_balance + account.total_balance,
          total_investment: acc.total_investment + account.total_investment,
          total_gain_loss: acc.total_gain_loss + account.total_gain_loss,
          account_count: acc.account_count + 1,
        }), {
          cash_balance: 0,
          stock_value: 0,
          total_balance: 0,
          total_investment: 0,
          total_gain_loss: 0,
          account_count: 0,
        });

        ownerSummary[owner][accountType] = summary;
      });
    });

    return Object.entries(ownerSummary)
      .sort(([a], [b]) => getOwnerOrder(a) - getOwnerOrder(b))
      .map(([owner, accountTypes]) => ({
        owner,
        accountTypes: Object.entries(accountTypes)
          .sort(([a], [b]) => getAccountTypeOrder(a) - getAccountTypeOrder(b))
          .map(([accountType, summary]) => ({
            accountType,
            ...summary,
          })),
      }));
  };

  const ownerSummary = calculateOwnerSummary();

  return (
    <div className="p-4 space-y-4 overflow-auto h-full">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">포트폴리오 요약</h3>
        <p className="text-sm text-gray-600">소유자별, 계좌타입별 포트폴리오 현황</p>
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

      {/* 소유자별/계좌타입별 포트폴리오 */}
      {ownerSummary.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2 mt-6 mb-2">
            <User className="w-5 h-5 text-blue-600" />
            <h4 className="font-semibold text-gray-900">소유자별 포트폴리오</h4>
          </div>

          {ownerSummary.map(({ owner, accountTypes }) => {
            // 소유자별 합계 계산
            const ownerTotal = accountTypes.reduce((acc, at) => ({
              cash_balance: acc.cash_balance + at.cash_balance,
              stock_value: acc.stock_value + at.stock_value,
              total_balance: acc.total_balance + at.total_balance,
              total_investment: acc.total_investment + at.total_investment,
              total_gain_loss: acc.total_gain_loss + at.total_gain_loss,
            }), { cash_balance: 0, stock_value: 0, total_balance: 0, total_investment: 0, total_gain_loss: 0 });

            return (
              <div key={owner} className="bg-white border border-gray-200 rounded-lg">
                {/* 소유자 헤더 */}
                <div className="p-3 bg-gray-50 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <User className="w-4 h-4 text-blue-600" />
                      <span className="font-semibold text-gray-900">{owner}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-blue-600">{formatCurrency(ownerTotal.total_balance)}</div>
                      <div className={`text-xs ${getColorClass(ownerTotal.total_gain_loss)}`}>
                        {formatCurrency(ownerTotal.total_gain_loss)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* 계좌타입별 상세 */}
                <div className="p-3 space-y-2">
                  {accountTypes.map((accountType) => {
                    const returnRate = accountType.total_investment > 0 
                      ? (accountType.total_gain_loss / accountType.total_investment) * 100 
                      : 0;

                    return (
                      <div key={accountType.accountType} className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center space-x-2 mb-2">
                          <Building2 className="w-3 h-3 text-green-600" />
                          <span className="text-sm font-medium text-gray-900">{accountType.accountType}</span>
                          <span className="text-xs text-gray-500">({accountType.account_count}개)</span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <div className="text-gray-600">현금</div>
                            <div className="font-medium">{formatCurrency(accountType.cash_balance)}</div>
                          </div>
                          <div>
                            <div className="text-gray-600">주식</div>
                            <div className="font-medium">{formatCurrency(accountType.stock_value)}</div>
                          </div>
                          <div>
                            <div className="text-gray-600">투자금</div>
                            <div className="font-medium">{formatCurrency(accountType.total_investment)}</div>
                          </div>
                          <div>
                            <div className="text-gray-600">손익</div>
                            <div className={`font-bold ${getColorClass(accountType.total_gain_loss)}`}>
                              {formatCurrency(accountType.total_gain_loss)}
                              <span className="ml-1">
                                ({formatPercentage(returnRate)})
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CompactPortfolioSummary;
