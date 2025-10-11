/**
 * 포맷팅 유틸리티
 */

/**
 * 숫자를 통화 형식으로 포맷
 */
export const formatCurrency = (value: number, currency: string = 'KRW'): string => {
  if (currency === 'KRW' || currency === 'KR' || currency === 'krw') {
    return `₩${Math.round(value).toLocaleString('ko-KR')}`;
  }
  
  if (currency === 'USD' || currency === 'US' || currency === 'usd') {
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  
  return `${value.toLocaleString()}`;
};

/**
 * 백분율 포맷
 */
export const formatPercent = (value: number, decimals: number = 2): string => {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
};

/**
 * 수익/손실 색상 클래스 반환
 */
export const getProfitColorClass = (value: number): string => {
  if (value > 0) return 'text-green-600';
  if (value < 0) return 'text-red-600';
  return 'text-gray-600';
};

/**
 * 수익/손실 배경 색상 클래스 반환
 */
export const getProfitBgClass = (value: number): string => {
  if (value > 0) return 'bg-green-50';
  if (value < 0) return 'bg-red-50';
  return 'bg-gray-50';
};

/**
 * 날짜 포맷
 */
export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  } catch {
    return dateString;
  }
};

/**
 * 날짜와 시간 포맷
 */
export const formatDateTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
};

/**
 * 큰 숫자를 축약형으로 포맷 (예: 1,000,000 -> 100만)
 */
export const formatLargeNumber = (value: number): string => {
  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  
  if (absValue >= 100000000) {
    return `${sign}${(absValue / 100000000).toFixed(1)}억`;
  }
  if (absValue >= 10000) {
    return `${sign}${(absValue / 10000).toFixed(1)}만`;
  }
  return `${sign}${absValue.toLocaleString()}`;
};

/**
 * 파일 크기 포맷
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * 계좌 이름에서 축약형 표시명 생성
 */
export const getAccountShortName = (accountName: string): string => {
  const parts = accountName.split(' ');
  if (parts.length >= 2) {
    return `${parts[0]} ${parts[1]}`;
  }
  return accountName;
};

/**
 * 숫자를 압축 형태로 표시 (K, M, B 사용)
 */
export const formatCompactNumber = (value: number): string => {
  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  
  if (absValue >= 1000000000) {
    return `${sign}${(absValue / 1000000000).toFixed(1)}B`;
  }
  if (absValue >= 1000000) {
    return `${sign}${(absValue / 1000000).toFixed(1)}M`;
  }
  if (absValue >= 1000) {
    return `${sign}${(absValue / 1000).toFixed(1)}K`;
  }
  return `${sign}${absValue}`;
};

