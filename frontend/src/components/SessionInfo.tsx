import React from 'react';
import { Database, Trash2, Info } from 'lucide-react';
import type { SessionInfo as SessionInfoType, CacheInfo } from '../types';

interface SessionInfoProps {
  sessionInfo: SessionInfoType | null;
  cacheInfo: CacheInfo | null;
  onClearCache: () => void;
  onLoadCacheInfo: () => void;
}

const SessionInfo: React.FC<SessionInfoProps> = ({ 
  sessionInfo, 
  cacheInfo, 
  onClearCache, 
  onLoadCacheInfo 
}) => {
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-blue-100 rounded-lg">
            <Database className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">💾 세션 정보</h3>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={onLoadCacheInfo}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Info className="w-4 h-4" />
            <span>캐시 정보</span>
          </button>
          <button
            onClick={onClearCache}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>캐시 삭제</span>
          </button>
        </div>
      </div>

      {sessionInfo && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="text-lg font-semibold text-green-800 mb-3">현재 세션</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-green-600 mb-1">세션 ID</div>
              <div className="font-mono text-sm bg-white p-2 rounded border">
                {sessionInfo.session_id}
              </div>
            </div>
            <div>
              <div className="text-sm text-green-600 mb-1">캐시 크기</div>
              <div className="font-semibold text-green-800">
                {formatBytes(sessionInfo.cache_size)}
              </div>
            </div>
            <div>
              <div className="text-sm text-green-600 mb-1">상태</div>
              <div className="text-green-800 font-medium">활성</div>
            </div>
            <div>
              <div className="text-sm text-green-600 mb-1">총 세션 수</div>
              <div className="text-green-800 font-medium">{sessionInfo.total_sessions}</div>
            </div>
          </div>
        </div>
      )}

      {cacheInfo && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h4 className="text-lg font-semibold text-gray-800 mb-3">캐시 정보</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-white p-3 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">총 세션 수</div>
              <div className="text-xl font-bold text-gray-900">{cacheInfo.total_sessions}</div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">총 캐시 크기</div>
              <div className="text-xl font-bold text-gray-900">
                {cacheInfo.total_cache_size_mb.toFixed(2)} MB
              </div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">평균 세션 크기</div>
              <div className="text-xl font-bold text-gray-900">
                {cacheInfo.total_sessions > 0 
                  ? (cacheInfo.total_cache_size_mb / cacheInfo.total_sessions).toFixed(2)
                  : '0.00'
                } MB
              </div>
            </div>
          </div>
          
          {cacheInfo.sessions.length > 0 && (
            <div>
              <div className="text-sm text-gray-600 mb-2">활성 세션 목록</div>
              <div className="bg-white p-3 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {cacheInfo.sessions.map((sessionId) => (
                    <div key={sessionId} className="font-mono text-xs bg-gray-100 p-2 rounded truncate">
                      {sessionId}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {!sessionInfo && !cacheInfo && (
        <div className="text-center py-8 text-gray-500">
          <Database className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p>세션 정보가 없습니다.</p>
          <p className="text-sm">CSV 파일을 업로드하면 세션 정보가 표시됩니다.</p>
        </div>
      )}
    </div>
  );
};

export default SessionInfo;
