import React, { useState } from 'react';
import { TrendingUp, TrendingDown, DollarSign, BarChart3, ChevronDown, ChevronRight, Building2, User } from 'lucide-react';
import type { AccountsDetailed } from '../types';

interface AccountPortfolioProps {
  data: AccountsDetailed;
}

const AccountPortfolio: React.FC<AccountPortfolioProps> = ({ data }) => {
  const [expandedOwners, setExpandedOwners] = useState<Set<string>>(new Set(['혜란', '유신', '민호']));
  const [expandedTypes, setExpandedTypes] = useState<Set<string>>(new Set());
  const [expandedAccounts, setExpandedAccounts] = useState<Set<string>>(new Set());

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

  // 소유자 우선순위
  const getOwnerOrder = (owner: string): number => {
    const order = {
      '혜란': 1,
      '유신': 2,
      '민호': 3
    };
    return order[owner as keyof typeof order] || 999;
  };

  // 계좌타입 우선순위
  const getAccountTypeOrder = (type: string): number => {
    const order = {
      '연금저축': 1,
      'ISA': 2,
      '종합매매': 3,
      '종합매매 해외': 4
    };
    return order[type as keyof typeof order] || 999;
  };

  const toggleOwner = (owner: string) => {
    const newExpanded = new Set(expandedOwners);
    if (newExpanded.has(owner)) {
      newExpanded.delete(owner);
    } else {
      newExpanded.add(owner);
    }
    setExpandedOwners(newExpanded);
  };

  const toggleType = (ownerTypeKey: string) => {
    const newExpanded = new Set(expandedTypes);
    if (newExpanded.has(ownerTypeKey)) {
      newExpanded.delete(ownerTypeKey);
    } else {
      newExpanded.add(ownerTypeKey);
    }
    setExpandedTypes(newExpanded);
  };

  const toggleAccount = (accountName: string) => {
    const newExpanded = new Set(expandedAccounts);
    if (newExpanded.has(accountName)) {
      newExpanded.delete(accountName);
    } else {
      newExpanded.add(accountName);
    }
    setExpandedAccounts(newExpanded);
  };

  // 소유자별로 정렬
  const sortedOwners = Object.entries(data.accounts_by_owner_and_type).sort(
    ([a], [b]) => getOwnerOrder(a) - getOwnerOrder(b)
  );

  return (
    <div className="p-4 space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">계좌별 포트폴리오</h3>
        <p className="text-sm text-gray-600">소유자별, 계좌타입별 계좌 현황 및 보유 종목</p>
      </div>

      <div className="space-y-4">
        {sortedOwners.map(([owner, ownerAccounts]) => (
          <div key={owner} className="border border-gray-200 rounded-lg bg-white">
            {/* 소유자 헤더 */}
            <div
              className="p-3 bg-gray-50 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
              onClick={() => toggleOwner(owner)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-blue-600" />
                  <h4 className="font-semibold text-gray-900">{owner}</h4>
                  <span className="text-sm text-gray-600">
                    ({Object.values(ownerAccounts).flat().length}개 계좌)
                  </span>
                </div>
                {expandedOwners.has(owner) ? (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                )}
              </div>
            </div>

            {/* 계좌타입별 목록 */}
            {expandedOwners.has(owner) && (
              <div className="p-3 space-y-4">
                {Object.entries(ownerAccounts)
                  .sort(([a], [b]) => getAccountTypeOrder(a) - getAccountTypeOrder(b))
                  .map(([accountType, accounts]) => {
                    const ownerTypeKey = `${owner}-${accountType}`;
                    return (
                      <div key={ownerTypeKey} className="border border-gray-200 rounded-lg bg-gray-50">
                        {/* 계좌타입 헤더 */}
                        <div
                          className="p-3 bg-white border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                          onClick={() => toggleType(ownerTypeKey)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <Building2 className="w-4 h-4 text-green-600" />
                              <h5 className="font-medium text-gray-900">{accountType}</h5>
                              <span className="text-sm text-gray-600">({accounts.length}개 계좌)</span>
                            </div>
                            {expandedTypes.has(ownerTypeKey) ? (
                              <ChevronDown className="w-4 h-4 text-gray-500" />
                            ) : (
                              <ChevronRight className="w-4 h-4 text-gray-500" />
                            )}
                          </div>
                        </div>

                        {/* 계좌 목록 */}
                        {expandedTypes.has(ownerTypeKey) && (
                          <div className="p-3 space-y-3">
                            {accounts.map((account) => (
                              <div key={account.full_account_name} className="border border-gray-200 rounded-lg bg-white">
                                {/* 계좌 헤더 */}
                                <div
                                  className="p-3 bg-gray-50 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                                  onClick={() => toggleAccount(account.full_account_name)}
                                >
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                      <div className="font-medium text-gray-900">{account.account_name}</div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${getColorClass(account.total_gain_loss)}`}>
                                        {formatCurrency(account.total_gain_loss)}
                                      </div>
                                      {expandedAccounts.has(account.full_account_name) ? (
                                        <ChevronDown className="w-4 h-4 text-gray-500" />
                                      ) : (
                                        <ChevronRight className="w-4 h-4 text-gray-500" />
                                      )}
                                    </div>
                                  </div>
                                </div>

                                {/* 계좌 상세 정보 */}
                                {expandedAccounts.has(account.full_account_name) && (
                                  <div className="p-3 space-y-4">
                                    {/* 계좌 기본 정보 */}
                                    <div className="grid grid-cols-4 gap-3 text-sm">
                                      <div className="bg-blue-50 rounded-lg p-3">
                                        <div className="flex items-center space-x-2 mb-1">
                                          <DollarSign className="w-4 h-4 text-blue-600" />
                                          <span className="text-blue-800 font-medium">잔액</span>
                                        </div>
                                        <div className="text-blue-900 font-semibold">
                                          {formatCurrency(account.balance)}
                                        </div>
                                      </div>

                                      <div className="bg-green-50 rounded-lg p-3">
                                        <div className="flex items-center space-x-2 mb-1">
                                          <TrendingUp className="w-4 h-4 text-green-600" />
                                          <span className="text-green-800 font-medium">투자금</span>
                                        </div>
                                        <div className="text-green-900 font-semibold">
                                          {formatCurrency(account.total_investment)}
                                        </div>
                                      </div>

                                      <div className="bg-purple-50 rounded-lg p-3">
                                        <div className="flex items-center space-x-2 mb-1">
                                          <BarChart3 className="w-4 h-4 text-purple-600" />
                                          <span className="text-purple-800 font-medium">현재가치</span>
                                        </div>
                                        <div className="text-purple-900 font-semibold">
                                          {formatCurrency(account.stock_value)}
                                        </div>
                                      </div>

                                      <div className="bg-orange-50 rounded-lg p-3">
                                        <div className="flex items-center space-x-2 mb-1">
                                          <TrendingDown className="w-4 h-4 text-orange-600" />
                                          <span className="text-orange-800 font-medium">손익</span>
                                        </div>
                                        <div className={`font-semibold ${getColorClass(account.total_gain_loss)}`}>
                                          {formatCurrency(account.total_gain_loss)}
                                        </div>
                                      </div>
                                    </div>

                                    {/* 보유 종목 목록 */}
                                    {account.holdings.length > 0 && (
                                      <div>
                                        <h6 className="text-sm font-medium text-gray-700 mb-3">보유 종목</h6>
                                        <div className="overflow-x-auto">
                                          <table className="min-w-full divide-y divide-gray-200">
                                            <thead className="bg-gray-50">
                                              <tr>
                                                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">종목명</th>
                                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">보유수량</th>
                                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">평단가</th>
                                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">현재가</th>
                                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">투자금</th>
                                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">현재가치</th>
                                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">손익</th>
                                              </tr>
                                            </thead>
                                            <tbody className="bg-white divide-y divide-gray-200">
                                              {account.holdings.map((holding, index) => (
                                                <tr key={index} className="hover:bg-gray-50">
                                                  <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                                                    {holding.security}
                                                  </td>
                                                  <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 text-right">
                                                    {holding.shares.toLocaleString()}
                                                  </td>
                                                  <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 text-right">
                                                    {formatCurrency(holding.avg_price)}
                                                  </td>
                                                  <td className="px-3 py-2 whitespace-nowrap text-sm font-semibold text-blue-600 text-right">
                                                    {holding.current_price > 0 ? formatCurrency(holding.current_price) : '-'}
                                                  </td>
                                                  <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 text-right">
                                                    {formatCurrency(holding.total_cost)}
                                                  </td>
                                                  <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 text-right">
                                                    {formatCurrency(holding.current_value)}
                                                  </td>
                                                  <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-right">
                                                    <span className={getColorClass(holding.unrealized_gain_loss)}>
                                                      {formatCurrency(holding.unrealized_gain_loss)}
                                                    </span>
                                                    <div className={`text-xs ${getColorClass(holding.unrealized_gain_loss_rate)}`}>
                                                      ({formatPercentage(holding.unrealized_gain_loss_rate)})
                                                    </div>
                                                  </td>
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        </div>
                                      </div>
                                    )}

                                    {account.holdings.length === 0 && (
                                      <div className="text-center py-4 text-gray-500 text-sm">
                                        보유 종목이 없습니다.
                                      </div>
                                    )}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
              </div>
            )}
          </div>
        ))}
      </div>

      {sortedOwners.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p>계좌별 포트폴리오 데이터가 없습니다.</p>
        </div>
      )}
    </div>
  );
};

export default AccountPortfolio;
