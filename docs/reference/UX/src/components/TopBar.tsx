import React, { useState } from 'react';
import { Sun, Moon, Settings } from 'lucide-react';

type Tab = 'file' | 'analyze' | 'edit' | 'validate' | 'fabricate' | 'view';
type Theme = 'light' | 'dark';

interface TopBarProps {
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const tabs: { id: Tab; label: string; shortcut: string }[] = [
  { id: 'file', label: 'FILE', shortcut: 'F1' },
  { id: 'analyze', label: 'ANALYZE', shortcut: 'F2' },
  { id: 'edit', label: 'EDIT', shortcut: 'F3' },
  { id: 'validate', label: 'VALIDATE', shortcut: 'F4' },
  { id: 'fabricate', label: 'FABRICATE', shortcut: 'F5' },
  { id: 'view', label: 'VIEW', shortcut: 'F6' },
];

export function TopBar({ activeTab, setActiveTab, theme, setTheme }: TopBarProps) {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [lengthUnits, setLengthUnits] = useState('mm');
  const [massUnits, setMassUnits] = useState('kg');
  const [volumeUnits, setVolumeUnits] = useState('ml');
  const [tolerance, setTolerance] = useState('0.001');
  const isDark = theme === 'dark';
  
  return (
    <div className={`flex flex-col border-b ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-300'}`}>
      {/* Tab Navigation */}
      <div className={`flex items-center px-2 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex items-center gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 transition-colors ${
                activeTab === tab.id
                  ? isDark 
                    ? 'bg-gray-700 text-white border-b-2 border-blue-500'
                    : 'bg-gray-100 text-gray-900 border-b-2 border-blue-500'
                  : isDark
                    ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-750'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <span className="text-xs tracking-wide">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Settings Button */}
        <div className="ml-auto pr-2 relative">
          <button
            onClick={() => setSettingsOpen(!settingsOpen)}
            className={`p-2 rounded transition-colors ${
              settingsOpen
                ? isDark ? 'bg-gray-700 text-blue-400' : 'bg-gray-200 text-blue-600'
                : isDark ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-600'
            }`}
            title="Program Settings"
          >
            <Settings size={16} />
          </button>

          {/* Settings Dropdown */}
          {settingsOpen && (
            <div className={`absolute right-0 top-full mt-1 w-72 rounded-lg shadow-lg border z-50 max-h-[80vh] overflow-y-auto ${
              isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-300'
            }`}>
              <div className={`px-4 py-3 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                <h3 className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Program Settings</h3>
              </div>

              <div className="p-3 space-y-3">
                {/* Theme Setting */}
                <div>
                  <label className={`text-xs block mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    View Mode
                  </label>
                  <div className={`flex gap-2 p-1 rounded ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}>
                    <button
                      onClick={() => setTheme('light')}
                      className={`flex-1 px-3 py-1.5 rounded text-xs transition-colors ${
                        theme === 'light'
                          ? 'bg-white text-gray-900 shadow'
                          : isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      <Sun size={14} className="inline mr-1" />
                      Light
                    </button>
                    <button
                      onClick={() => setTheme('dark')}
                      className={`flex-1 px-3 py-1.5 rounded text-xs transition-colors ${
                        theme === 'dark'
                          ? 'bg-gray-900 text-white shadow'
                          : isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      <Moon size={14} className="inline mr-1" />
                      Dark
                    </button>
                  </div>
                </div>

                {/* Length Units Setting */}
                <div>
                  <label className={`text-xs block mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Length Units
                  </label>
                  <select
                    value={lengthUnits}
                    onChange={(e) => setLengthUnits(e.target.value)}
                    className={`w-full text-xs px-3 py-1.5 rounded border ${
                      isDark 
                        ? 'bg-gray-700 border-gray-600 text-gray-200' 
                        : 'bg-white border-gray-300 text-gray-700'
                    }`}
                  >
                    <optgroup label="Metric">
                      <option value="mm">Millimeters (mm)</option>
                      <option value="cm">Centimeters (cm)</option>
                      <option value="m">Meters (m)</option>
                    </optgroup>
                    <optgroup label="Imperial">
                      <option value="fractional">Fractional Feet & Inches (5' 3 1/2")</option>
                      <option value="decimal-in">Decimal Inches (63.5")</option>
                      <option value="decimal-ft">Decimal Feet (5.29')</option>
                    </optgroup>
                  </select>
                </div>

                {/* Mass Units Setting */}
                <div>
                  <label className={`text-xs block mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Mass Units
                  </label>
                  <select
                    value={massUnits}
                    onChange={(e) => setMassUnits(e.target.value)}
                    className={`w-full text-xs px-3 py-1.5 rounded border ${
                      isDark 
                        ? 'bg-gray-700 border-gray-600 text-gray-200' 
                        : 'bg-white border-gray-300 text-gray-700'
                    }`}
                  >
                    <optgroup label="Metric">
                      <option value="mg">Milligrams (mg)</option>
                      <option value="g">Grams (g)</option>
                      <option value="kg">Kilograms (kg)</option>
                    </optgroup>
                    <optgroup label="Imperial">
                      <option value="oz">Ounces (oz)</option>
                      <option value="lb">Pounds (lb)</option>
                    </optgroup>
                  </select>
                </div>

                {/* Volume Units Setting */}
                <div>
                  <label className={`text-xs block mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Volume Units
                  </label>
                  <select
                    value={volumeUnits}
                    onChange={(e) => setVolumeUnits(e.target.value)}
                    className={`w-full text-xs px-3 py-1.5 rounded border ${
                      isDark 
                        ? 'bg-gray-700 border-gray-600 text-gray-200' 
                        : 'bg-white border-gray-300 text-gray-700'
                    }`}
                  >
                    <optgroup label="Metric">
                      <option value="ml">Milliliters (ml)</option>
                      <option value="l">Liters (L)</option>
                      <option value="m3">Cubic Meters (m³)</option>
                    </optgroup>
                    <optgroup label="Imperial">
                      <option value="floz">Fluid Ounces (fl oz)</option>
                      <option value="cup">Cups</option>
                      <option value="gal">Gallons (gal)</option>
                      <option value="ft3">Cubic Feet (ft³)</option>
                    </optgroup>
                  </select>
                </div>

                {/* Tolerance Setting */}
                <div>
                  <label className={`text-xs block mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Tolerance
                  </label>
                  <select
                    value={tolerance}
                    onChange={(e) => setTolerance(e.target.value)}
                    className={`w-full text-xs px-3 py-1.5 rounded border ${
                      isDark 
                        ? 'bg-gray-700 border-gray-600 text-gray-200' 
                        : 'bg-white border-gray-300 text-gray-700'
                    }`}
                  >
                    <option value="0.1">0.1 (coarse)</option>
                    <option value="0.01">0.01</option>
                    <option value="0.001">0.001 (standard)</option>
                    <option value="0.0001">0.0001</option>
                    <option value="0.00001">0.00001 (fine)</option>
                  </select>
                </div>

                {/* Close Button */}
                <button
                  onClick={() => setSettingsOpen(false)}
                  className={`w-full text-xs px-3 py-1.5 rounded border ${
                    isDark 
                      ? 'bg-gray-700 border-gray-600 text-gray-200 hover:bg-gray-600' 
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Primary Actions Area - Changes based on active tab */}
      <div className={`px-4 py-3 ${isDark ? 'bg-gray-800' : 'bg-gray-50'}`}>
        {activeTab === 'file' && <FileActions theme={theme} />}
        {activeTab === 'analyze' && <AnalyzeActions theme={theme} />}
        {activeTab === 'edit' && <EditActions theme={theme} />}
        {activeTab === 'validate' && <ValidateActions theme={theme} />}
        {activeTab === 'fabricate' && <FabricateActions theme={theme} />}
        {activeTab === 'view' && <ViewActions theme={theme} />}
      </div>
    </div>
  );
}

function FileActions({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <ActionButton isDark={isDark}>New Session</ActionButton>
      <ActionButton isDark={isDark}>Open Session</ActionButton>
      <ActionButton isDark={isDark}>Save Session</ActionButton>
      <ActionButton isDark={isDark}>Save As</ActionButton>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ActionButton isDark={isDark}>Import from Rhino</ActionButton>
      <ActionButton isDark={isDark}>Export to Rhino</ActionButton>
    </div>
  );
}

function AnalyzeActions({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <ActionButton isDark={isDark}>Curvature Analysis</ActionButton>
      <ActionButton isDark={isDark}>Spectral Analysis</ActionButton>
      <ActionButton isDark={isDark}>Flow Analysis</ActionButton>
      <ActionButton isDark={isDark}>Topological Analysis</ActionButton>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ActionButton isDark={isDark} primary>Analyze</ActionButton>
    </div>
  );
}

function EditActions({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <div className={`flex gap-1 p-1 rounded ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}>
        <ToggleButton isDark={isDark}>Solid</ToggleButton>
        <ToggleButton isDark={isDark}>Panel</ToggleButton>
        <ToggleButton isDark={isDark}>Edge</ToggleButton>
        <ToggleButton isDark={isDark}>Vertex</ToggleButton>
      </div>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ActionButton isDark={isDark}>Select All</ActionButton>
      <ActionButton isDark={isDark}>Clear Selection</ActionButton>
      <ActionButton isDark={isDark}>Invert Selection</ActionButton>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ActionButton isDark={isDark}>Pin/Unpin Region</ActionButton>
      <ActionButton isDark={isDark}>Delete Region</ActionButton>
    </div>
  );
}

function ValidateActions({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <ActionButton isDark={isDark} primary>Run Constraint Check</ActionButton>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ToggleButton isDark={isDark}>Show All Errors</ToggleButton>
      <ToggleButton isDark={isDark}>Show All Warnings</ToggleButton>
      <ToggleButton isDark={isDark}>Show Features</ToggleButton>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ActionButton isDark={isDark}>Clear Validation</ActionButton>
      <ActionButton isDark={isDark}>Re-validate All</ActionButton>
    </div>
  );
}

function FabricateActions({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <ActionButton isDark={isDark}>Generate Mold Shells</ActionButton>
      <ActionButton isDark={isDark}>Add Registration Keys</ActionButton>
      <ActionButton isDark={isDark}>Add Band Grooves</ActionButton>
      <ActionButton isDark={isDark}>Add Pour Spouts</ActionButton>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ActionButton isDark={isDark}>Calculate Slip Volume</ActionButton>
      <ActionButton isDark={isDark} primary>Export for 3D Printing</ActionButton>
    </div>
  );
}

function ViewActions({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <ActionButton isDark={isDark}>Reset All Views</ActionButton>
      <ActionButton isDark={isDark}>Reset Current View</ActionButton>
      <ActionButton isDark={isDark}>Frame All Geometry</ActionButton>
      <ActionButton isDark={isDark}>Frame Selected</ActionButton>
      <div className={`w-px h-6 ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />
      <ToggleButton isDark={isDark}>Show/Hide Axes</ToggleButton>
      <ToggleButton isDark={isDark}>Show/Hide Grid</ToggleButton>
    </div>
  );
}

function ActionButton({ children, isDark, primary = false }: { children: React.ReactNode; isDark: boolean; primary?: boolean }) {
  if (primary) {
    return (
      <button className="px-4 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors text-xs">
        {children}
      </button>
    );
  }
  return (
    <button className={`px-3 py-1.5 rounded transition-colors text-xs ${
      isDark 
        ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' 
        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
    }`}>
      {children}
    </button>
  );
}

function ToggleButton({ children, isDark }: { children: React.ReactNode; isDark: boolean }) {
  return (
    <button className={`px-3 py-1 rounded transition-colors text-xs ${
      isDark 
        ? 'text-gray-300 hover:bg-gray-600 hover:text-white' 
        : 'text-gray-700 hover:bg-white hover:text-gray-900'
    }`}>
      {children}
    </button>
  );
}
