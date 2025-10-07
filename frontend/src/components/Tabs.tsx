import React, { useState } from 'react';
import { BarChart3, PieChart, TrendingUp } from 'lucide-react';

interface TabsProps {
  children: React.ReactNode;
}

interface TabProps {
  label: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

const Tab: React.FC<TabProps> = ({ children }) => {
  return <div className="h-full">{children}</div>;
};

const Tabs: React.FC<TabsProps> = ({ children }) => {
  const [activeTab, setActiveTab] = useState(0);
  
  const tabs = React.Children.toArray(children) as React.ReactElement<TabProps>[];

  return (
    <div className="h-full flex flex-col">
      {/* 탭 헤더 */}
      <div className="flex border-b border-gray-200 bg-white">
        {tabs.map((tab, index) => (
          <button
            key={index}
            onClick={() => setActiveTab(index)}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === index
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            {tab.props.icon}
            <span>{tab.props.label}</span>
          </button>
        ))}
      </div>
      
      {/* 탭 컨텐츠 */}
      <div className="flex-1 overflow-y-auto">
        {tabs[activeTab]}
      </div>
    </div>
  );
};

export { Tabs, Tab };
