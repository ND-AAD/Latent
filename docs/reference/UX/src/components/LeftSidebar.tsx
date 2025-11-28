import React from 'react';
import { FileText, Activity, Edit3, CheckCircle, Package, Eye } from 'lucide-react';

type Tab = 'file' | 'analyze' | 'edit' | 'validate' | 'fabricate' | 'view';
type Theme = 'light' | 'dark';

interface LeftSidebarProps {
  activeTab: Tab;
  theme: Theme;
}

export function LeftSidebar({ activeTab, theme }: LeftSidebarProps) {
  const isDark = theme === 'dark';
  
  return (
    <div 
      className={`w-[220px] border-r overflow-y-auto ${
        isDark ? 'bg-gray-850 border-gray-700' : 'bg-gray-50 border-gray-300'
      }`}
      style={{ minWidth: '160px', maxWidth: '280px' }}
    >
      {/* Section Header */}
      <div className={`px-4 py-2 border-b ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-100'}`}>
        <div className="flex items-center gap-2">
          {activeTab === 'file' && <FileText size={16} className={isDark ? 'text-gray-400' : 'text-gray-600'} />}
          {activeTab === 'analyze' && <Activity size={16} className={isDark ? 'text-gray-400' : 'text-gray-600'} />}
          {activeTab === 'edit' && <Edit3 size={16} className={isDark ? 'text-gray-400' : 'text-gray-600'} />}
          {activeTab === 'validate' && <CheckCircle size={16} className={isDark ? 'text-gray-400' : 'text-gray-600'} />}
          {activeTab === 'fabricate' && <Package size={16} className={isDark ? 'text-gray-400' : 'text-gray-600'} />}
          {activeTab === 'view' && <Eye size={16} className={isDark ? 'text-gray-400' : 'text-gray-600'} />}
          <span className={`text-xs tracking-wide ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            ADVANCED TOOLS
          </span>
        </div>
      </div>

      {/* Tool List - Changes based on active tab */}
      <div className="p-2">
        {activeTab === 'file' && <FileTools theme={theme} />}
        {activeTab === 'analyze' && <AnalyzeTools theme={theme} />}
        {activeTab === 'edit' && <EditTools theme={theme} />}
        {activeTab === 'validate' && <ValidateTools theme={theme} />}
        {activeTab === 'fabricate' && <FabricateTools theme={theme} />}
        {activeTab === 'view' && <ViewTools theme={theme} />}
      </div>
    </div>
  );
}

function FileTools({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="space-y-1">
      <SidebarButton isDark={isDark}>Save Template</SidebarButton>
      <SidebarButton isDark={isDark}>Load Template</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Recent Files</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Export Analysis Report</SidebarButton>
      <SidebarButton isDark={isDark}>Export Validation Report</SidebarButton>
      <SidebarButton isDark={isDark}>Batch Export</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark} disabled>Auto-save Settings</SidebarButton>
      <SidebarButton isDark={isDark} disabled>Version History</SidebarButton>
      <SidebarButton isDark={isDark} disabled>Cloud Sync</SidebarButton>
    </div>
  );
}

function AnalyzeTools({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="space-y-1">
      <SidebarButton isDark={isDark}>Compare Analyses</SidebarButton>
      <SidebarButton isDark={isDark}>Differential Analysis</SidebarButton>
      <SidebarButton isDark={isDark}>Batch Analysis</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Analysis History Timeline</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Save Analysis Preset</SidebarButton>
      <SidebarButton isDark={isDark}>Load Analysis Preset</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark} disabled>Custom Analysis Scripts</SidebarButton>
      <SidebarButton isDark={isDark} disabled>ML-Based Region Suggestion</SidebarButton>
    </div>
  );
}

function EditTools({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="space-y-1">
      <SidebarButton isDark={isDark}>Grow Selection</SidebarButton>
      <SidebarButton isDark={isDark}>Shrink Selection</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Edit Boundary</SidebarButton>
      <SidebarButton isDark={isDark}>Export Selection to Region</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Merge Regions</SidebarButton>
      <SidebarButton isDark={isDark}>Split Regions</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Pin All Regions</SidebarButton>
      <SidebarButton isDark={isDark}>Unpin All Regions</SidebarButton>
      <SidebarButton isDark={isDark}>Batch Region Operations</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark} disabled>Selection Filters</SidebarButton>
    </div>
  );
}

function ValidateTools({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="space-y-1">
      <div className={`px-3 py-1 text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
        QUICK FIXES
      </div>
      <SidebarButton isDark={isDark}>Fix Undercuts</SidebarButton>
      <SidebarButton isDark={isDark}>Adjust Pull Direction</SidebarButton>
      <SidebarButton isDark={isDark}>Auto-Fix Draft Angles</SidebarButton>
      <SidebarButton isDark={isDark}>Adjust Wall Thickness</SidebarButton>
      <SidebarButton isDark={isDark}>Repair Seam Gaps</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <div className={`px-3 py-1 text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
        CONFIGURATION
      </div>
      <SidebarButton isDark={isDark}>Custom Constraint Editor</SidebarButton>
      <SidebarButton isDark={isDark}>Tolerance Overrides</SidebarButton>
      <SidebarButton isDark={isDark}>Exemption Manager</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark} disabled>Validation Profiles</SidebarButton>
    </div>
  );
}

function FabricateTools({ theme }: { theme: Theme }) {
  const [exportSettingsOpen, setExportSettingsOpen] = React.useState(false);
  const isDark = theme === 'dark';
  
  return (
    <div className="space-y-1">
      <SidebarButton isDark={isDark}>Custom Key Profiles</SidebarButton>
      <SidebarButton isDark={isDark}>Optimize Seam Placement</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Add Part Numbers/Labels</SidebarButton>
      <SidebarButton isDark={isDark}>Generate Assembly Diagram</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Multi-pour Strategy</SidebarButton>
      <SidebarButton isDark={isDark}>Drying Time Calculator</SidebarButton>
      <SidebarButton isDark={isDark}>Add Witness Marks</SidebarButton>
      <SidebarButton isDark={isDark}>Mold Weight Calculator</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Generate Casting Instructions</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      
      {/* Export Settings - Expandable */}
      <div>
        <button
          onClick={() => setExportSettingsOpen(!exportSettingsOpen)}
          className={`w-full text-left px-3 py-1.5 rounded text-xs transition-colors ${
            isDark
              ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
              : 'text-gray-700 hover:bg-gray-200 hover:text-gray-900'
          }`}
        >
          {exportSettingsOpen ? '▼' : '▶'} Export Settings
        </button>
        
        {exportSettingsOpen && (
          <div className={`mt-1 ml-4 space-y-2 p-2 rounded text-xs ${
            isDark ? 'bg-gray-800' : 'bg-gray-100'
          }`}>
            <div className={`mb-2 pb-2 border-b ${isDark ? 'border-gray-700' : 'border-gray-300'}`}>
              <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Export Destination
              </span>
            </div>
            
            <button
              className={`w-full px-2 py-1.5 rounded text-xs text-left ${
                isDark 
                  ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
              }`}
            >
              📄 Export G-Code
            </button>
            
            <button
              className={`w-full px-2 py-1.5 rounded text-xs text-left ${
                isDark 
                  ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
              }`}
            >
              🔄 Push to Rhino
            </button>
            
            <div className={`mt-3 pt-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-300'}`}>
              <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                Additional export options will be available here
              </span>
            </div>
          </div>
        )}
      </div>
      
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark} disabled>QC Checklist Generator</SidebarButton>
      <SidebarButton isDark={isDark} disabled>Kiln Schedule Generator</SidebarButton>
    </div>
  );
}

function ViewTools({ theme }: { theme: Theme }) {
  const [cameraLocked, setCameraLocked] = React.useState(false);
  const [cameraPropsExpanded, setCameraPropsExpanded] = React.useState(false);
  const isDark = theme === 'dark';
  
  return (
    <div className="space-y-1">
      <SidebarButton isDark={isDark}>Save Named View</SidebarButton>
      <SidebarButton isDark={isDark}>Restore Named View</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      
      {/* Lock Camera - Toggle Button */}
      <button
        onClick={() => setCameraLocked(!cameraLocked)}
        className={`w-full text-left px-3 py-1.5 rounded text-xs transition-colors ${
          cameraLocked
            ? isDark
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-blue-500 text-white hover:bg-blue-600'
            : isDark
              ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
              : 'text-gray-700 hover:bg-gray-200 hover:text-gray-900'
        }`}
      >
        {cameraLocked ? '🔒 Camera Locked' : 'Lock Camera'}
      </button>
      
      {/* Camera Properties - Expandable */}
      <div>
        <button
          onClick={() => setCameraPropsExpanded(!cameraPropsExpanded)}
          className={`w-full text-left px-3 py-1.5 rounded text-xs transition-colors ${
            isDark
              ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
              : 'text-gray-700 hover:bg-gray-200 hover:text-gray-900'
          }`}
        >
          {cameraPropsExpanded ? '▼' : '▶'} Camera Properties
        </button>
        
        {cameraPropsExpanded && (
          <div className={`mt-1 ml-4 space-y-2 p-2 rounded text-xs ${
            isDark ? 'bg-gray-800' : 'bg-gray-100'
          }`}>
            <div>
              <label className={`block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                FOV (Field of View)
              </label>
              <input
                type="number"
                defaultValue="60"
                className={`w-full px-2 py-1 rounded border text-xs ${
                  isDark 
                    ? 'bg-gray-700 border-gray-600 text-gray-200' 
                    : 'bg-white border-gray-300 text-gray-700'
                }`}
              />
            </div>
            
            <div>
              <label className={`block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Near Clip
              </label>
              <input
                type="number"
                defaultValue="0.1"
                step="0.1"
                className={`w-full px-2 py-1 rounded border text-xs ${
                  isDark 
                    ? 'bg-gray-700 border-gray-600 text-gray-200' 
                    : 'bg-white border-gray-300 text-gray-700'
                }`}
              />
            </div>
            
            <div>
              <label className={`block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Far Clip
              </label>
              <input
                type="number"
                defaultValue="1000"
                step="10"
                className={`w-full px-2 py-1 rounded border text-xs ${
                  isDark 
                    ? 'bg-gray-700 border-gray-600 text-gray-200' 
                    : 'bg-white border-gray-300 text-gray-700'
                }`}
              />
            </div>
            
            <div>
              <label className={`block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Projection
              </label>
              <select
                className={`w-full px-2 py-1 rounded border text-xs ${
                  isDark 
                    ? 'bg-gray-700 border-gray-600 text-gray-200' 
                    : 'bg-white border-gray-300 text-gray-700'
                }`}
              >
                <option>Perspective</option>
                <option>Orthographic</option>
              </select>
            </div>
            
            <button
              className={`w-full px-2 py-1 rounded text-xs ${
                isDark 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              Apply Changes
            </button>
          </div>
        )}
      </div>
      
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark}>Reset Panel Layout</SidebarButton>
      <SidebarButton isDark={isDark}>Toggle Full Screen</SidebarButton>
      <div className={`my-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`} />
      <SidebarButton isDark={isDark} disabled>Section Planes</SidebarButton>
      <SidebarButton isDark={isDark} disabled>Display Modes</SidebarButton>
      <SidebarButton isDark={isDark} disabled>Turntable Animation</SidebarButton>
    </div>
  );
}

function SidebarButton({ children, isDark, disabled = false }: { children: React.ReactNode; isDark: boolean; disabled?: boolean }) {
  return (
    <button
      disabled={disabled}
      className={`w-full text-left px-3 py-1.5 rounded text-xs transition-colors ${
        disabled
          ? isDark 
            ? 'text-gray-600 cursor-not-allowed' 
            : 'text-gray-400 cursor-not-allowed'
          : isDark
            ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
            : 'text-gray-700 hover:bg-gray-200 hover:text-gray-900'
      }`}
    >
      {children}
    </button>
  );
}
