/**
 * Frontend 로깅 유틸리티
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  stack?: string;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // 최대 메모리 로그 수
  private isDevelopment = import.meta.env.DEV;

  private formatTimestamp(): string {
    const now = new Date();
    return now.toISOString();
  }

  private createLogEntry(level: LogLevel, message: string, data?: any, error?: Error): LogEntry {
    return {
      timestamp: this.formatTimestamp(),
      level,
      message,
      data,
      stack: error?.stack,
    };
  }

  private addLog(entry: LogEntry) {
    this.logs.push(entry);
    
    // 최대 로그 수 제한
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // 로컬 스토리지에 저장 (최근 100개만)
    try {
      const recentLogs = this.logs.slice(-100);
      localStorage.setItem('app_logs', JSON.stringify(recentLogs));
    } catch (e) {
      // 로컬 스토리지 실패 시 무시
    }
  }

  private logToConsole(level: LogLevel, message: string, data?: any) {
    const timestamp = new Date().toLocaleTimeString('ko-KR');
    const prefix = `[${timestamp}]`;

    switch (level) {
      case 'debug':
        if (this.isDevelopment) {
          console.log(`${prefix} 🔍`, message, data || '');
        }
        break;
      case 'info':
        console.log(`${prefix} ℹ️`, message, data || '');
        break;
      case 'warn':
        console.warn(`${prefix} ⚠️`, message, data || '');
        break;
      case 'error':
        console.error(`${prefix} ❌`, message, data || '');
        break;
    }
  }

  debug(message: string, data?: any) {
    const entry = this.createLogEntry('debug', message, data);
    this.addLog(entry);
    this.logToConsole('debug', message, data);
  }

  info(message: string, data?: any) {
    const entry = this.createLogEntry('info', message, data);
    this.addLog(entry);
    this.logToConsole('info', message, data);
  }

  warn(message: string, data?: any) {
    const entry = this.createLogEntry('warn', message, data);
    this.addLog(entry);
    this.logToConsole('warn', message, data);
  }

  error(message: string, error?: Error | any, data?: any) {
    const entry = this.createLogEntry('error', message, data, error);
    this.addLog(entry);
    this.logToConsole('error', message, { error, ...data });

    // 에러는 서버로 전송 (선택적)
    this.sendErrorToServer(entry);
  }

  private async sendErrorToServer(entry: LogEntry) {
    // 개발 환경에서는 서버로 전송하지 않음
    if (this.isDevelopment) return;

    try {
      // 실제 환경에서는 에러 로그를 서버로 전송할 수 있음
      // await fetch('/api/log-error', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(entry),
      // });
    } catch (e) {
      // 서버 전송 실패는 무시
    }
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  getRecentLogs(count: number = 50): LogEntry[] {
    return this.logs.slice(-count);
  }

  clearLogs() {
    this.logs = [];
    try {
      localStorage.removeItem('app_logs');
    } catch (e) {
      // 무시
    }
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  downloadLogs() {
    const logsJson = this.exportLogs();
    const blob = new Blob([logsJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `frontend-logs-${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

// 싱글톤 인스턴스
export const logger = new Logger();

// 전역 에러 핸들러
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    logger.error('Uncaught error', event.error, {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    logger.error('Unhandled promise rejection', event.reason, {
      promise: event.promise,
    });
  });
}

export default logger;

