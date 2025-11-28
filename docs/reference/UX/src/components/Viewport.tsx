import React, { useState, useRef } from 'react';
import { Maximize2, Grid3x3 } from 'lucide-react';

type Theme = 'light' | 'dark';
type ViewportLayout = 'single' | 'two-horizontal' | 'two-vertical' | 'four-grid';

interface ViewportProps {
  theme: Theme;
}

export function Viewport({ theme }: ViewportProps) {
  const [layout, setLayout] = useState<ViewportLayout>('four-grid');
  const [maximizedView, setMaximizedView] = useState<string | null>(null);
  const isDark = theme === 'dark';

  const handleViewDoubleClick = (viewLabel: string) => {
    if (maximizedView === viewLabel) {
      // Restore to four-grid
      setMaximizedView(null);
      setLayout('four-grid');
    } else {
      // Maximize this view
      setMaximizedView(viewLabel);
      setLayout('single');
    }
  };

  return (
    <div className={`flex-1 flex flex-col ${isDark ? 'bg-gray-900' : 'bg-gray-100'}`}>
      {/* Viewport Area - Maximized */}
      <div className="flex-1 p-2">
        {maximizedView ? (
          <SingleView theme={theme} viewLabel={maximizedView} onDoubleClick={handleViewDoubleClick} />
        ) : layout === 'single' ? (
          <SingleView theme={theme} onDoubleClick={handleViewDoubleClick} />
        ) : layout === 'two-horizontal' ? (
          <TwoHorizontalView theme={theme} onDoubleClick={handleViewDoubleClick} />
        ) : layout === 'two-vertical' ? (
          <TwoVerticalView theme={theme} onDoubleClick={handleViewDoubleClick} />
        ) : (
          <FourGridView theme={theme} onDoubleClick={handleViewDoubleClick} />
        )}
      </div>
    </div>
  );
}

function SingleView({ theme, viewLabel, onDoubleClick }: { theme: Theme; viewLabel?: string; onDoubleClick?: (label: string) => void }) {
  const label = viewLabel || "Perspective";
  return (
    <div className="w-full h-full">
      <ViewportPanel label={label} theme={theme} onDoubleClick={onDoubleClick} />
    </div>
  );
}

function TwoHorizontalView({ theme, onDoubleClick }: { theme: Theme; onDoubleClick?: (label: string) => void }) {
  const [topHeight, setTopHeight] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDark = theme === 'dark';

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    const startY = e.clientY;
    const startHeight = topHeight;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (!containerRef.current) return;
      const containerHeight = containerRef.current.clientHeight;
      const deltaY = moveEvent.clientY - startY;
      const deltaPercent = (deltaY / containerHeight) * 100;
      const newHeight = Math.min(Math.max(startHeight + deltaPercent, 10), 90);
      setTopHeight(newHeight);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div ref={containerRef} className="w-full h-full flex flex-col">
      <div style={{ height: `${topHeight}%` }}>
        <ViewportPanel label="Top View" theme={theme} onDoubleClick={onDoubleClick} />
      </div>
      <div
        onMouseDown={handleMouseDown}
        className={`h-0.5 cursor-row-resize relative ${isDark ? 'bg-gray-700 hover:bg-blue-500' : 'bg-gray-300 hover:bg-blue-500'} transition-colors`}
        style={{ marginTop: '-4px', marginBottom: '-4px', paddingTop: '4px', paddingBottom: '4px' }}
      />
      <div style={{ height: `${100 - topHeight}%` }}>
        <ViewportPanel label="Perspective" theme={theme} onDoubleClick={onDoubleClick} />
      </div>
    </div>
  );
}

function TwoVerticalView({ theme, onDoubleClick }: { theme: Theme; onDoubleClick?: (label: string) => void }) {
  const [leftWidth, setLeftWidth] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDark = theme === 'dark';

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = leftWidth;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (!containerRef.current) return;
      const containerWidth = containerRef.current.clientWidth;
      const deltaX = moveEvent.clientX - startX;
      const deltaPercent = (deltaX / containerWidth) * 100;
      const newWidth = Math.min(Math.max(startWidth + deltaPercent, 10), 90);
      setLeftWidth(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div ref={containerRef} className="w-full h-full flex">
      <div style={{ width: `${leftWidth}%` }}>
        <ViewportPanel label="Front View" theme={theme} onDoubleClick={onDoubleClick} />
      </div>
      <div
        onMouseDown={handleMouseDown}
        className={`w-0.5 cursor-col-resize relative ${isDark ? 'bg-gray-700 hover:bg-blue-500' : 'bg-gray-300 hover:bg-blue-500'} transition-colors`}
        style={{ marginLeft: '-4px', marginRight: '-4px', paddingLeft: '4px', paddingRight: '4px' }}
      />
      <div style={{ width: `${100 - leftWidth}%` }}>
        <ViewportPanel label="Perspective" theme={theme} onDoubleClick={onDoubleClick} />
      </div>
    </div>
  );
}

function FourGridView({ theme, onDoubleClick }: { theme: Theme; onDoubleClick?: (label: string) => void }) {
  const [horizontalSplit, setHorizontalSplit] = useState(50);
  const [verticalSplit, setVerticalSplit] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDark = theme === 'dark';

  const handleHorizontalMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const startWidth = horizontalSplit;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (!containerRef.current) return;
      const containerWidth = containerRef.current.clientWidth;
      const deltaX = moveEvent.clientX - startX;
      const deltaPercent = (deltaX / containerWidth) * 100;
      const newWidth = Math.min(Math.max(startWidth + deltaPercent, 10), 90);
      setHorizontalSplit(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleVerticalMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const startY = e.clientY;
    const startHeight = verticalSplit;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (!containerRef.current) return;
      const containerHeight = containerRef.current.clientHeight;
      const deltaY = moveEvent.clientY - startY;
      const deltaPercent = (deltaY / containerHeight) * 100;
      const newHeight = Math.min(Math.max(startHeight + deltaPercent, 10), 90);
      setVerticalSplit(newHeight);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleBothMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const startY = e.clientY;
    const startHorizontal = horizontalSplit;
    const startVertical = verticalSplit;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (!containerRef.current) return;
      const containerWidth = containerRef.current.clientWidth;
      const containerHeight = containerRef.current.clientHeight;
      
      const deltaX = moveEvent.clientX - startX;
      const deltaY = moveEvent.clientY - startY;
      const deltaPercentX = (deltaX / containerWidth) * 100;
      const deltaPercentY = (deltaY / containerHeight) * 100;
      
      const newHorizontal = Math.min(Math.max(startHorizontal + deltaPercentX, 10), 90);
      const newVertical = Math.min(Math.max(startVertical + deltaPercentY, 10), 90);
      
      setHorizontalSplit(newHorizontal);
      setVerticalSplit(newVertical);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div ref={containerRef} className="w-full h-full flex flex-col">
      <div style={{ height: `${verticalSplit}%` }} className="flex">
        <div style={{ width: `${horizontalSplit}%` }}>
          <ViewportPanel label="Top View" theme={theme} onDoubleClick={onDoubleClick} />
        </div>
        <div
          onMouseDown={handleHorizontalMouseDown}
          className={`w-0.5 cursor-col-resize relative ${isDark ? 'bg-gray-700 hover:bg-blue-500' : 'bg-gray-300 hover:bg-blue-500'} transition-colors`}
          style={{ marginLeft: '-4px', marginRight: '-4px', paddingLeft: '4px', paddingRight: '4px' }}
        />
        <div style={{ width: `${100 - horizontalSplit}%` }}>
          <ViewportPanel label="Perspective" theme={theme} onDoubleClick={onDoubleClick} />
        </div>
      </div>
      <div className="flex relative" style={{ marginTop: '-4px', marginBottom: '-4px' }}>
        <div
          onMouseDown={handleVerticalMouseDown}
          className={`h-0.5 cursor-row-resize relative ${isDark ? 'bg-gray-700 hover:bg-blue-500' : 'bg-gray-300 hover:bg-blue-500'} transition-colors`}
          style={{ width: `${horizontalSplit}%`, paddingTop: '4px', paddingBottom: '4px' }}
        />
        <div
          onMouseDown={handleBothMouseDown}
          className={`w-2 h-2 cursor-move absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 hover:opacity-100 rounded-sm ${isDark ? 'bg-gray-600 hover:bg-blue-500' : 'bg-gray-400 hover:bg-blue-500'} transition-all z-10`}
          title="Drag to move both dividers"
        />
        <div
          onMouseDown={handleVerticalMouseDown}
          className={`h-0.5 cursor-row-resize relative ${isDark ? 'bg-gray-700 hover:bg-blue-500' : 'bg-gray-300 hover:bg-blue-500'} transition-colors`}
          style={{ width: `${100 - horizontalSplit}%`, paddingTop: '4px', paddingBottom: '4px' }}
        />
      </div>
      <div style={{ height: `${100 - verticalSplit}%` }} className="flex">
        <div style={{ width: `${horizontalSplit}%` }}>
          <ViewportPanel label="Front View" theme={theme} onDoubleClick={onDoubleClick} />
        </div>
        <div
          onMouseDown={handleHorizontalMouseDown}
          className={`w-0.5 cursor-col-resize relative ${isDark ? 'bg-gray-700 hover:bg-blue-500' : 'bg-gray-300 hover:bg-blue-500'} transition-colors`}
          style={{ marginLeft: '-4px', marginRight: '-4px', paddingLeft: '4px', paddingRight: '4px' }}
        />
        <div style={{ width: `${100 - horizontalSplit}%` }}>
          <ViewportPanel label="Right View" theme={theme} onDoubleClick={onDoubleClick} />
        </div>
      </div>
    </div>
  );
}

function ViewportPanel({ label, theme, onDoubleClick }: { label: string; theme: Theme; onDoubleClick?: (label: string) => void }) {
  const isDark = theme === 'dark';
  
  return (
    <div 
      className={`relative w-full h-full rounded border ${
        isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-300'
      }`}
      onDoubleClick={() => onDoubleClick?.(label)}
    >
      {/* Viewport Label with Grey Background */}
      <div className={`absolute top-2 left-2 px-2 py-1 rounded border text-xs ${
        isDark ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-gray-300 border-gray-400 text-gray-800'
      }`}>
        {label}
      </div>

      {/* Grid representation */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className={`w-full h-full ${isDark ? 'opacity-10' : 'opacity-5'}`}
          style={{
            backgroundImage: `
              linear-gradient(${isDark ? '#fff' : '#000'} 1px, transparent 1px),
              linear-gradient(90deg, ${isDark ? '#fff' : '#000'} 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
            backgroundPosition: 'center center'
          }}
        />
      </div>

      {/* Axis indicator */}
      <div className="absolute bottom-4 left-4 flex flex-col gap-1">
        <div className="flex items-center gap-1">
          <div className="w-8 h-0.5 bg-red-500" />
          <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>X</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-8 h-0.5 bg-green-500" />
          <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Y</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-8 h-0.5 bg-blue-500" />
          <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Z</span>
        </div>
      </div>

      {/* Center placeholder */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className={`text-xs ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
          3D Viewport
        </div>
      </div>
    </div>
  );
}
