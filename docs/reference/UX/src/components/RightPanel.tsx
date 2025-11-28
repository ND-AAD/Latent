import React, { useState } from 'react';
import { Monitor, Layers, AlertTriangle, MousePointer, Settings, ChevronRight, Pin, Edit2, Trash2 } from 'lucide-react';

type Theme = 'light' | 'dark';
type RightTab = 'viewport' | 'regions' | 'constraints' | 'selection' | 'parameters';

interface RightPanelProps {
  theme: Theme;
}

export function RightPanel({ theme }: RightPanelProps) {
  const [activeTab, setActiveTab] = useState<RightTab>('viewport');
  const isDark = theme === 'dark';

  return (
    <div className={`w-[320px] flex border-l ${
      isDark ? 'bg-gray-850 border-gray-700' : 'bg-gray-50 border-gray-300'
    }`}
    style={{ minWidth: '240px', maxWidth: '450px' }}>
      {/* Vertical Tab Bar */}
      <div className={`w-12 flex flex-col border-r ${
        isDark ? 'bg-gray-800 border-gray-700' : 'bg-gray-100 border-gray-200'
      }`}>
        <TabButton
          icon={<Monitor size={18} />}
          label="Viewport"
          active={activeTab === 'viewport'}
          onClick={() => setActiveTab('viewport')}
          isDark={isDark}
        />
        <TabButton
          icon={<Layers size={18} />}
          label="Regions"
          active={activeTab === 'regions'}
          onClick={() => setActiveTab('regions')}
          isDark={isDark}
        />
        <TabButton
          icon={<AlertTriangle size={18} />}
          label="Constraints"
          active={activeTab === 'constraints'}
          onClick={() => setActiveTab('constraints')}
          isDark={isDark}
        />
        <TabButton
          icon={<MousePointer size={18} />}
          label="Selection"
          active={activeTab === 'selection'}
          onClick={() => setActiveTab('selection')}
          isDark={isDark}
        />
        <TabButton
          icon={<Settings size={18} />}
          label="Parameters"
          active={activeTab === 'parameters'}
          onClick={() => setActiveTab('parameters')}
          isDark={isDark}
        />
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'viewport' && <ViewportPanel theme={theme} />}
        {activeTab === 'regions' && <RegionsPanel theme={theme} />}
        {activeTab === 'constraints' && <ConstraintsPanel theme={theme} />}
        {activeTab === 'selection' && <SelectionPanel theme={theme} />}
        {activeTab === 'parameters' && <ParametersPanel theme={theme} />}
      </div>
    </div>
  );
}

function TabButton({ icon, label, active, onClick, isDark }: { 
  icon: React.ReactNode; 
  label: string; 
  active: boolean; 
  onClick: () => void; 
  isDark: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full h-12 flex items-center justify-center border-b transition-colors ${
        active
          ? isDark
            ? 'bg-gray-850 text-blue-400 border-l-2 border-l-blue-500'
            : 'bg-gray-50 text-blue-600 border-l-2 border-l-blue-500'
          : isDark
            ? 'text-gray-500 hover:text-gray-300 hover:bg-gray-750 border-gray-700'
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50 border-gray-200'
      }`}
      title={label}
    >
      {icon}
    </button>
  );
}

function ViewportPanel({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  return (
    <div className="p-4">
      <PanelSection title="Layout" isDark={isDark}>
        <select className={`w-full text-xs px-2 py-1 rounded border ${
          isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
        }`}>
          <option>Single Viewport</option>
          <option>Two Horizontal</option>
          <option>Two Vertical</option>
          <option>Four Grid</option>
        </select>
      </PanelSection>

      <PanelSection title="Shading Mode" isDark={isDark}>
        <select className={`w-full text-xs px-2 py-1 rounded border ${
          isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
        }`}>
          <option>Wireframe</option>
          <option>Shaded</option>
          <option>Rendered</option>
        </select>
      </PanelSection>

      <PanelSection title="Display Options" isDark={isDark}>
        <Checkbox label="Edge Display" isDark={isDark} />
        <Checkbox label="Show Grid" isDark={isDark} defaultChecked />
        <Checkbox label="Grid Snap" isDark={isDark} />
        <Checkbox label="Material Preview" isDark={isDark} />
      </PanelSection>

      <PanelSection title="Camera" isDark={isDark}>
        <Checkbox label="Sync All Cameras" isDark={isDark} defaultChecked />
      </PanelSection>

      <PanelSection title="Background" isDark={isDark}>
        <div className="flex items-center gap-2">
          <input type="color" className="w-8 h-6 rounded" defaultValue="#1a1a1a" />
          <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Color</span>
        </div>
      </PanelSection>
    </div>
  );
}

function RegionsPanel({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  
  const regions = [
    { name: 'Base Region', unity: 'Curvature Unity', strength: 0.92, pinned: true, color: 'green' },
    { name: 'Handle Region', unity: 'Flow Unity', strength: 0.87, pinned: false, color: 'yellow' },
    { name: 'Rim Region', unity: 'Topological Unity', strength: 0.74, pinned: true, color: 'orange' },
  ];

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-3">
        <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
          Regions: {regions.length} ({regions.filter(r => r.pinned).length} pinned)
        </div>
      </div>

      <input 
        type="text" 
        placeholder="Search regions..."
        className={`w-full text-xs px-3 py-1.5 rounded border mb-2 ${
          isDark ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-500' : 'bg-white border-gray-300 text-gray-700'
        }`}
      />

      <select className={`w-full text-xs px-2 py-1 rounded border mb-3 ${
        isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
      }`}>
        <option>Sort by Name</option>
        <option>Sort by Unity</option>
        <option>Pinned First</option>
      </select>

      <div className="space-y-2">
        {regions.map((region, idx) => (
          <RegionItem key={idx} region={region} isDark={isDark} />
        ))}
      </div>

      <PanelSection title="Selected Region Properties" isDark={isDark} collapsible>
        <PropertyRow label="Name" value="Base Region" isDark={isDark} />
        <PropertyRow label="Unity Principle" value="Curvature Unity" isDark={isDark} />
        <PropertyRow label="Face Count" value="1,247" isDark={isDark} />
        <div className="mt-2">
          <div className={`text-xs mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Unity Strength</div>
          <div className="w-full bg-gray-600 rounded-full h-2">
            <div className="bg-green-500 h-2 rounded-full" style={{ width: '92%' }} />
          </div>
          <div className={`text-xs mt-1 text-right ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>0.92</div>
        </div>
      </PanelSection>
    </div>
  );
}

function RegionItem({ region, isDark }: { region: any; isDark: boolean }) {
  const colorMap: Record<string, string> = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
  };

  return (
    <div className={`p-2 rounded border ${
      isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
    }`}>
      <div className="flex items-start gap-2">
        <div className={`w-3 h-3 rounded ${colorMap[region.color]} mt-0.5`} />
        <div className="flex-1 min-w-0">
          <div className={`text-xs ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>{region.name}</div>
          <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{region.unity}</div>
        </div>
        <div className="flex gap-1">
          {region.pinned && <Pin size={12} className={isDark ? 'text-blue-400' : 'text-blue-600'} />}
          <button className={`p-0.5 rounded ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}>
            <Edit2 size={12} className={isDark ? 'text-gray-500' : 'text-gray-600'} />
          </button>
          <button className={`p-0.5 rounded ${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}>
            <Trash2 size={12} className={isDark ? 'text-gray-500' : 'text-gray-600'} />
          </button>
        </div>
      </div>
    </div>
  );
}

function ConstraintsPanel({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  
  return (
    <div className="p-4">
      <div className={`p-3 rounded mb-4 ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
        <div className={`text-xs mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Overall Status</div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className={`${isDark ? 'text-gray-200' : 'text-gray-900'}`}>2 Errors, 3 Warnings</div>
        </div>
      </div>

      <PanelSection title="Errors (2)" isDark={isDark} collapsible defaultExpanded badge="red">
        <ConstraintItem 
          title="Undercut violation"
          description="Region 1: Base - faces 45-67"
          severity={0.85}
          isDark={isDark}
          type="error"
        />
        <ConstraintItem 
          title="Trapped volume detected"
          description="Region 2: Handle - cavity inaccessible"
          severity={0.72}
          isDark={isDark}
          type="error"
        />
      </PanelSection>

      <PanelSection title="Warnings (3)" isDark={isDark} collapsible badge="yellow">
        <ConstraintItem 
          title="Insufficient draft angle"
          description="Region 1: Base - 2.5° (min 3°)"
          severity={0.45}
          isDark={isDark}
          type="warning"
        />
        <ConstraintItem 
          title="Wall thickness issue"
          description="Region 3: Rim - 1.8mm (min 2.0mm)"
          severity={0.38}
          isDark={isDark}
          type="warning"
        />
        <ConstraintItem 
          title="Seam gap detected"
          description="Between Region 1 & 2 - 0.3mm gap"
          severity={0.28}
          isDark={isDark}
          type="warning"
        />
      </PanelSection>

      <PanelSection title="Features (0)" isDark={isDark} collapsible badge="blue">
        <div className={`text-xs text-center py-4 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
          No manual edits or overrides
        </div>
      </PanelSection>
    </div>
  );
}

function ConstraintItem({ title, description, severity, isDark, type }: { 
  title: string; 
  description: string; 
  severity: number; 
  isDark: boolean;
  type: 'error' | 'warning';
}) {
  return (
    <div className={`p-2 rounded border mb-2 ${
      isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
    }`}>
      <div className={`text-xs mb-1 ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>{title}</div>
      <div className={`text-xs mb-2 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{description}</div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Severity:</div>
          <div className={`text-xs ${type === 'error' ? 'text-red-500' : 'text-yellow-500'}`}>
            {severity.toFixed(2)}
          </div>
        </div>
        <button className={`text-xs px-2 py-1 rounded ${
          isDark ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}>
          Quick Fix
        </button>
      </div>
    </div>
  );
}

function SelectionPanel({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  
  return (
    <div className="p-4">
      <PanelSection title="Current Mode" isDark={isDark}>
        <div className="flex items-center gap-2">
          <div className={`px-3 py-1 rounded ${isDark ? 'bg-blue-600' : 'bg-blue-500'} text-white text-xs`}>
            Solid Mode
          </div>
        </div>
      </PanelSection>

      <PanelSection title="Selection Count" isDark={isDark}>
        <PropertyRow label="Faces" value="23" isDark={isDark} />
        <PropertyRow label="Edges" value="0" isDark={isDark} />
        <PropertyRow label="Vertices" value="0" isDark={isDark} />
      </PanelSection>

      <PanelSection title="Statistics" isDark={isDark}>
        <PropertyRow label="Total Area" value="145.2 mm²" isDark={isDark} />
        <PropertyRow label="Bounding Box" value="45×32×18 mm" isDark={isDark} />
      </PanelSection>

      <PanelSection title="Selected Indices" isDark={isDark} collapsible>
        <div className={`p-2 rounded text-xs font-mono max-h-32 overflow-y-auto ${
          isDark ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-700'
        }`}>
          [0, 1, 2, 5, 8, 12, 15, 18, 23, 27, 31, 34, 38, 42, 45, 49, 53, 57, 61, 65, 69, 73, 77]
        </div>
        <button className={`mt-2 w-full text-xs px-3 py-1.5 rounded border ${
          isDark ? 'bg-gray-700 border-gray-600 text-gray-200 hover:bg-gray-600' : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
        }`}>
          Copy Indices
        </button>
      </PanelSection>
    </div>
  );
}

function ParametersPanel({ theme }: { theme: Theme }) {
  const isDark = theme === 'dark';
  
  return (
    <div className="p-4">
      <PanelSection title="Analysis Settings" isDark={isDark}>
        <div className="mb-3">
          <label className={`text-xs block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Resolution</label>
          <select className={`w-full text-xs px-2 py-1 rounded border ${
            isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
          }`}>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Ultra</option>
          </select>
        </div>

        <div className="mb-3">
          <label className={`text-xs block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Min Region Size</label>
          <select className={`w-full text-xs px-2 py-1 rounded border ${
            isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
          }`}>
            <option>Tiny</option>
            <option>Small</option>
            <option>Medium</option>
            <option>Large</option>
          </select>
        </div>

        <div className="mb-3">
          <label className={`text-xs block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Colormap</label>
          <select className={`w-full text-xs px-2 py-1 rounded border ${
            isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
          }`}>
            <option>Viridis</option>
            <option>Plasma</option>
            <option>Jet</option>
            <option>Rainbow</option>
          </select>
        </div>

        <Checkbox label="Auto-range" isDark={isDark} defaultChecked />
      </PanelSection>

      <PanelSection title="Value Range" isDark={isDark}>
        <div className="mb-3">
          <label className={`text-xs block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Min Value</label>
          <input 
            type="number" 
            defaultValue="0.0"
            step="0.1"
            className={`w-full text-xs px-2 py-1 rounded border ${
              isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
            }`}
          />
        </div>
        <div className="mb-3">
          <label className={`text-xs block mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Max Value</label>
          <input 
            type="number" 
            defaultValue="1.0"
            step="0.1"
            className={`w-full text-xs px-2 py-1 rounded border ${
              isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-700'
            }`}
          />
        </div>
      </PanelSection>

      <PanelSection title="Histogram" isDark={isDark}>
        <div className={`w-full h-24 rounded border flex items-center justify-center ${
          isDark ? 'bg-gray-800 border-gray-700' : 'bg-gray-100 border-gray-300'
        }`}>
          <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Histogram Display</span>
        </div>
      </PanelSection>
    </div>
  );
}

function PanelSection({ 
  title, 
  children, 
  isDark, 
  collapsible = false, 
  defaultExpanded = false,
  badge
}: { 
  title: string; 
  children: React.ReactNode; 
  isDark: boolean; 
  collapsible?: boolean;
  defaultExpanded?: boolean;
  badge?: 'red' | 'yellow' | 'blue';
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const badgeColors = {
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    blue: 'bg-blue-500',
  };

  return (
    <div className={`mb-4 pb-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'} last:border-0`}>
      <div 
        className={`flex items-center justify-between mb-2 ${collapsible ? 'cursor-pointer' : ''}`}
        onClick={() => collapsible && setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <h3 className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{title}</h3>
          {badge && <div className={`w-2 h-2 rounded-full ${badgeColors[badge]}`} />}
        </div>
        {collapsible && (
          <ChevronRight 
            size={14} 
            className={`transition-transform ${expanded ? 'rotate-90' : ''} ${isDark ? 'text-gray-500' : 'text-gray-400'}`}
          />
        )}
      </div>
      {(!collapsible || expanded) && <div>{children}</div>}
    </div>
  );
}

function PropertyRow({ label, value, isDark }: { label: string; value: string; isDark: boolean }) {
  return (
    <div className="flex justify-between items-center mb-2">
      <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{label}</span>
      <span className={`text-xs ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>{value}</span>
    </div>
  );
}

function Checkbox({ label, isDark, defaultChecked = false }: { label: string; isDark: boolean; defaultChecked?: boolean }) {
  return (
    <label className="flex items-center gap-2 mb-2 cursor-pointer">
      <input 
        type="checkbox" 
        defaultChecked={defaultChecked}
        className="rounded"
      />
      <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{label}</span>
    </label>
  );
}
