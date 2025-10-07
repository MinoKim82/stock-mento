// API 응답 타입 정의
export interface SessionInfo {
  session_id: string;
  message: string;
  cache_size: number;
  total_sessions: number;
}

export interface TotalAssets {
  cash_balance: number;
  stock_value: number;
  total_balance: number;
  account_count: number;
}

export interface StockPortfolio {
  total_investment: number;
  current_value: number;
  unrealized_gain_loss: number;
  return_rate: number;
  total_holdings: number;
  gain_holdings: number;
  loss_holdings: number;
}

export interface AssetAllocation {
  cash_ratio: number;
  stock_ratio: number;
}

export interface PortfolioSummary {
  total_assets: TotalAssets;
  stock_portfolio: StockPortfolio;
  asset_allocation: AssetAllocation;
}

export interface TopPerformer {
  security: string;
  account: string;
  shares: number;
  investment: number;
  current_value: number;
  gain_loss: number;
  return_rate: number;
}

export interface AccountPerformance {
  holdings_count: number;
  total_investment: number;
  total_value: number;
  total_gain_loss: number;
  return_rate: number;
}

export interface PortfolioPerformance {
  top_performers: TopPerformer[];
  bottom_performers: TopPerformer[];
  account_performance: Record<string, AccountPerformance>;
}

export interface RiskMetrics {
  total_holdings: number;
  gain_holdings_count: number;
  loss_holdings_count: number;
  win_rate: number;
}

export interface GainLossAnalysis {
  total_gain: number;
  total_loss: number;
  net_gain_loss: number;
}

export interface ExtremePerformer {
  security: string;
  account: string;
  gain_loss: number;
  return_rate: number;
}

export interface ConcentrationHolding {
  security: string;
  account: string;
  value: number;
  ratio: number;
}

export interface ConcentrationRisk {
  top5_concentration_ratio: number;
  top5_holdings: ConcentrationHolding[];
}

export interface PortfolioRisk {
  risk_metrics: RiskMetrics;
  gain_loss_analysis: GainLossAnalysis;
  extreme_performers: {
    max_gain: ExtremePerformer | null;
    max_loss: ExtremePerformer | null;
  };
  concentration_risk: ConcentrationRisk;
}

export interface CacheInfo {
  total_sessions: number;
  total_cache_size: number;
  total_cache_size_mb: number;
  sessions: string[];
}

export interface FilterOptions {
  owners: string[];
  brokers: string[];
  account_types: string[];
}

export interface Transaction {
  거래일: string;
  계좌명: string;
  거래구분: string;
  종목명: string;
  수량: number | string;
  단가: number | string;
  금액: number | string;
  비고: string;
}

export interface TransactionList {
  transactions: Transaction[];
  total_count: number;
}

export interface HoldingDetail {
  security: string;
  shares: number;
  avg_price: number;
  total_cost: number;
  current_price: number;
  current_value: number;
  unrealized_gain_loss: number;
  unrealized_gain_loss_rate: number;
}

export interface AccountDetail {
  account_name: string;
  full_account_name: string;
  owner: string;
  broker: string;
  balance: number;
  stock_value: number;
  total_balance: number;
  total_investment: number;
  total_gain_loss: number;
  holdings: HoldingDetail[];
}

export interface AccountsDetailed {
  accounts_by_owner_and_type: {
    [owner: string]: {
      [accountType: string]: AccountDetail[];
    };
  };
}
