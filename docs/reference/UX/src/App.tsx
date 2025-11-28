import React, { useState } from 'react';
import { TopBar } from './components/TopBar';
import { LeftSidebar } from './components/LeftSidebar';
import { RightPanel } from './components/RightPanel';
import { BottomPanel } from './components/BottomPanel';
import { Viewport } from './components/Viewport';

type Tab = 'file' | 'analyze' | 'edit' | 'validate' | 'fabricate' | 'view';
type Theme = 'light' | 'dark';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('file');
  const [theme, setTheme] = useState<Theme>('light');

  return (
    <div className={`h-screen w-screen flex flex-col overflow-hidden ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}>
      {/* Top Bar - Tab Navigation + Primary Actions */}
      <TopBar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        theme={theme}
        setTheme={setTheme}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Secondary Actions */}
        <LeftSidebar activeTab={activeTab} theme={theme} />

        {/* Center - 3D Viewport */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Viewport theme={theme} />
        </div>

        {/* Right Panel - Properties and Data */}
        <RightPanel theme={theme} />
      </div>

      {/* Bottom Panel - System Communication */}
      <BottomPanel theme={theme} />
    </div>
  );
}
