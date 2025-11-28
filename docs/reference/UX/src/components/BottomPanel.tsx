import React, { useState } from 'react';
import { Terminal, X, ChevronUp, ChevronDown, Circle, Wifi, WifiOff, Activity } from 'lucide-react';

type Theme = 'light' | 'dark';

interface BottomPanelProps {
  theme: Theme;
}

export function BottomPanel({ theme }: BottomPanelProps) {
  const [debugExpanded, setDebugExpanded] = useState(false);
  const [connected, setConnected] = useState(true);
  const isDark = theme === 'dark';

  const commandHistory = [
    { command: 'analyze.run("curvature", resolution="high")', status: 'success', time: '14:32:15' },
    { command: 'regions.create_from_analysis(min_size="medium")', status: 'success', time: '14:32:18' },
    { command: 'validate.check_constraints()', status: 'warning', time: '14:32:22' },
  ];

  return (
    <div className={`flex flex-col border-t ${
      isDark ? 'bg-gray-850 border-gray-700' : 'bg-gray-50 border-gray-300'
    }`}>
      {/* Debug Console (Collapsible) */}
      {debugExpanded && (
        <div className={`h-40 border-b overflow-hidden ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className={`h-full flex flex-col ${isDark ? 'bg-gray-900' : 'bg-gray-800'}`}>
            {/* Debug Header */}
            <div className={`flex items-center justify-between px-3 py-1.5 border-b ${
              isDark ? 'border-gray-700 bg-gray-850' : 'border-gray-700 bg-gray-750'
            }`}>
              <div className="flex items-center gap-2">
                <Terminal size={14} className={isDark ? 'text-gray-400' : 'text-gray-300'} />
                <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-200'}`}>Debug Console</span>
              </div>
              <div className="flex items-center gap-2">
                <button className={`text-xs px-2 py-0.5 rounded ${
                  isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-600 text-gray-300'
                }`}>
                  Clear
                </button>
                <button className={`text-xs px-2 py-0.5 rounded ${
                  isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-600 text-gray-300'
                }`}>
                  Export
                </button>
                <button 
                  onClick={() => setDebugExpanded(false)}
                  className={`p-0.5 rounded ${isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-600 text-gray-300'}`}
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Debug Content */}
            <div className={`flex-1 overflow-y-auto p-3 font-mono text-xs ${
              isDark ? 'text-gray-300' : 'text-gray-200'
            }`}>
              <div className="text-blue-400">[14:32:10] INFO: Application initialized</div>
              <div className="text-green-400">[14:32:15] SUCCESS: Curvature analysis completed</div>
              <div className="text-green-400">[14:32:18] SUCCESS: Created 3 regions from analysis</div>
              <div className="text-yellow-400">[14:32:22] WARNING: 2 constraint violations detected</div>
              <div className="text-gray-500">[14:32:25] DEBUG: Memory usage: 245 MB</div>
            </div>
          </div>
        </div>
      )}

      {/* Main Bottom Panel */}
      <div className="flex items-stretch h-10" style={{ minHeight: '100px', maxHeight: '160px' }}>
        {/* Connection Status */}
        <div className={`w-40 flex flex-col justify-center px-3 border-r ${isDark ? 'border-gray-700' : 'border-gray-300'}`}>
          <div className="flex items-center gap-2 mb-1">
            {connected ? (
              <>
                <Circle size={8} className="text-green-500" fill="currentColor" />
                <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Rhino</span>
              </>
            ) : (
              <>
                <Circle size={8} className="text-red-500" fill="currentColor" />
                <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Disconnected</span>
              </>
            )}
          </div>
          <button 
            onClick={() => setConnected(!connected)}
            className={`text-xs px-2 py-0.5 rounded border ${
              isDark 
                ? 'border-gray-600 text-gray-400 hover:bg-gray-700' 
                : 'border-gray-300 text-gray-600 hover:bg-gray-100'
            }`}
          >
            {connected ? 'Disconnect' : 'Reconnect'}
          </button>
        </div>

        {/* Command Input - Centered and Maximized */}
        <div className={`flex-1 flex items-center px-4 border-r ${isDark ? 'border-gray-700' : 'border-gray-300'}`}>
          <div className={`mr-3 text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>&gt;</div>
          <input
            type="text"
            placeholder="Type command or press Tab to autocomplete..."
            className={`flex-1 text-xs bg-transparent border-none outline-none ${
              isDark ? 'text-gray-200 placeholder-gray-600' : 'text-gray-700 placeholder-gray-400'
            }`}
          />
        </div>

        {/* System Status */}
        <div className={`w-32 flex flex-col justify-center px-3 border-r ${isDark ? 'border-gray-700' : 'border-gray-300'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Activity size={12} className={isDark ? 'text-gray-400' : 'text-gray-600'} />
            <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Idle</span>
          </div>
          <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>245 MB</div>
        </div>

        {/* Debug Toggle */}
        <div className={`w-12 flex items-center justify-center border-l ${isDark ? 'border-gray-700' : 'border-gray-300'}`}>
          <button
            onClick={() => setDebugExpanded(!debugExpanded)}
            className={`p-2 rounded transition-colors ${
              debugExpanded
                ? isDark ? 'bg-gray-700 text-blue-400' : 'bg-gray-200 text-blue-600'
                : isDark ? 'hover:bg-gray-700 text-gray-500' : 'hover:bg-gray-200 text-gray-500'
            }`}
            title="Toggle Debug Console"
          >
            {debugExpanded ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
          </button>
        </div>
      </div>
    </div>
  );
}
