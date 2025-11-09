import { useState } from 'react';
import { Button } from './ui/button';
import { 
  RotateCcwIcon, 
  MaximizeIcon,
  RulerIcon,
  EyeIcon,
  BoxIcon,
  GridIcon,
  ScanIcon
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from './ui/dropdown-menu';
import type { Viewport as ViewportType, EditMode } from '../App';

interface ViewportProps {
  viewport: ViewportType;
  editMode: EditMode;
  selectedRegion: number | null;
  onRegionSelect: (region: number | null) => void;
  onViewportChange: (viewport: ViewportType) => void;
}

export function Viewport({ viewport, editMode, selectedRegion, onRegionSelect, onViewportChange }: ViewportProps) {
  const [hoveredRegion, setHoveredRegion] = useState<number | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<number | null>(null);
  const [hoveredVertex, setHoveredVertex] = useState<number | null>(null);
  
  const viewTypeLabels = {
    perspective: 'Perspective',
    top: 'Top',
    front: 'Front',
    right: 'Right',
    isometric: 'Isometric',
    axonometric: 'Axonometric'
  };

  // Mock regions for visualization
  const regions = [
    { id: 1, color: 'rgb(147, 197, 253)', path: 'M150,100 Q200,80 250,100 L250,250 Q200,270 150,250 Z', label: 'Region 1' },
    { id: 2, color: 'rgb(252, 165, 165)', path: 'M250,100 Q300,80 350,100 L350,250 Q300,270 250,250 Z', label: 'Region 2' },
    { id: 3, color: 'rgb(196, 181, 253)', path: 'M350,100 Q400,80 450,100 L450,250 Q400,270 350,250 Z', label: 'Region 3' },
    { id: 4, color: 'rgb(134, 239, 172)', path: 'M150,250 Q200,230 250,250 L250,400 Q200,420 150,400 Z', label: 'Region 4' },
    { id: 5, color: 'rgb(253, 224, 71)', path: 'M250,250 Q300,230 350,250 L350,400 Q300,420 250,400 Z', label: 'Region 5' },
  ];

  return (
    <div className="flex-1 bg-[#fafafa] dark:bg-[#1a1a1a] relative">
      {/* Viewport Controls Overlay */}
      <div className="absolute top-3 left-3 flex flex-col gap-2 z-10">
        <div className="bg-card border border-border rounded-lg shadow-sm p-1 flex flex-col gap-1">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
            <RotateCcwIcon className="size-3.5" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
            <MaximizeIcon className="size-3.5" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
            <RulerIcon className="size-3.5" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
            <EyeIcon className="size-3.5" />
          </Button>
        </div>
      </div>

      {/* View Type and Display Mode Controls */}
      <div className="absolute top-3 right-3 z-10 flex gap-2">
        {/* View Type Selector */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="h-7 bg-card shadow-sm">
              <span className="text-xs">{viewTypeLabels[viewport.viewType]}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onViewportChange({ ...viewport, viewType: 'perspective' })}>
              Perspective
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => onViewportChange({ ...viewport, viewType: 'top' })}>
              Top
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onViewportChange({ ...viewport, viewType: 'front' })}>
              Front
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onViewportChange({ ...viewport, viewType: 'right' })}>
              Right
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => onViewportChange({ ...viewport, viewType: 'isometric' })}>
              Isometric
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onViewportChange({ ...viewport, viewType: 'axonometric' })}>
              Axonometric
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Display Mode Selector */}
        <div className="bg-card border border-border rounded-lg shadow-sm p-0.5 flex gap-0.5">
          <Button 
            variant={viewport.displayMode === 'solid' ? 'secondary' : 'ghost'} 
            size="sm" 
            className="h-6 w-6 p-0"
            onClick={() => onViewportChange({ ...viewport, displayMode: 'solid' })}
          >
            <BoxIcon className="size-3.5" />
          </Button>
          <Button 
            variant={viewport.displayMode === 'wireframe' ? 'secondary' : 'ghost'} 
            size="sm" 
            className="h-6 w-6 p-0"
            onClick={() => onViewportChange({ ...viewport, displayMode: 'wireframe' })}
          >
            <GridIcon className="size-3.5" />
          </Button>
          <Button 
            variant={viewport.displayMode === 'xray' ? 'secondary' : 'ghost'} 
            size="sm" 
            className="h-6 w-6 p-0"
            onClick={() => onViewportChange({ ...viewport, displayMode: 'xray' })}
          >
            <ScanIcon className="size-3.5" />
          </Button>
        </div>
      </div>

      {/* 3D Visualization (Mock) */}
      <div className="w-full h-full flex items-center justify-center">
        <svg 
          viewBox="0 0 600 500" 
          className="w-full h-full max-w-3xl max-h-[700px]"
          style={{ filter: 'drop-shadow(0 10px 30px rgba(0, 0, 0, 0.15))' }}
        >
          {/* Seam lines / Edges (emphasized as per design philosophy) */}
          <g className="seam-lines">
            {[
              { id: 1, x1: 250, y1: 100, x2: 250, y2: 400 },
              { id: 2, x1: 350, y1: 100, x2: 350, y2: 400 },
              { id: 3, x1: 150, y1: 250, x2: 450, y2: 250 }
            ].map((edge) => (
              <line
                key={edge.id}
                x1={edge.x1}
                y1={edge.y1}
                x2={edge.x2}
                y2={edge.y2}
                stroke={
                  editMode === 'edge' && hoveredEdge === edge.id 
                    ? 'rgb(59, 130, 246)' 
                    : 'rgb(100, 116, 139)'
                }
                strokeWidth={
                  editMode === 'edge' && hoveredEdge === edge.id ? 4 : 2.5
                }
                strokeDasharray="5,5"
                opacity={editMode === 'edge' ? 0.8 : 0.6}
                className={editMode === 'edge' ? 'cursor-pointer transition-all' : ''}
                onMouseEnter={() => editMode === 'edge' && setHoveredEdge(edge.id)}
                onMouseLeave={() => editMode === 'edge' && setHoveredEdge(null)}
              />
            ))}
          </g>

          {/* Vertices (shown in vertex edit mode) */}
          {editMode === 'vertex' && (
            <g className="vertices">
              {[
                { id: 1, x: 250, y: 100 },
                { id: 2, x: 350, y: 100 },
                { id: 3, x: 450, y: 100 },
                { id: 4, x: 150, y: 250 },
                { id: 5, x: 250, y: 250 },
                { id: 6, x: 350, y: 250 },
                { id: 7, x: 450, y: 250 },
                { id: 8, x: 250, y: 400 },
                { id: 9, x: 350, y: 400 }
              ].map((vertex) => (
                <circle
                  key={vertex.id}
                  cx={vertex.x}
                  cy={vertex.y}
                  r={hoveredVertex === vertex.id ? 6 : 4}
                  fill={hoveredVertex === vertex.id ? 'rgb(59, 130, 246)' : 'rgb(100, 116, 139)'}
                  stroke="white"
                  strokeWidth="2"
                  className="cursor-pointer transition-all"
                  onMouseEnter={() => setHoveredVertex(vertex.id)}
                  onMouseLeave={() => setHoveredVertex(null)}
                />
              ))}
            </g>
          )}

          {/* Regions (panels) */}
          {(editMode === 'panel' || editMode === 'solid') && regions.map((region) => (
            <g key={region.id}>
              <path
                d={region.path}
                fill={region.color}
                opacity={
                  selectedRegion === region.id ? 0.9 :
                  hoveredRegion === region.id ? 0.7 :
                  0.5
                }
                stroke={selectedRegion === region.id ? 'rgb(59, 130, 246)' : 'white'}
                strokeWidth={selectedRegion === region.id ? 3 : 1}
                className={editMode === 'panel' ? 'cursor-pointer transition-all duration-200' : ''}
                onMouseEnter={() => editMode === 'panel' && setHoveredRegion(region.id)}
                onMouseLeave={() => editMode === 'panel' && setHoveredRegion(null)}
                onClick={() => editMode === 'panel' && onRegionSelect(region.id)}
              />
              {(hoveredRegion === region.id || selectedRegion === region.id) && editMode === 'panel' && (
                <text
                  x={region.id <= 3 ? 150 + (region.id - 1) * 100 + 50 : 150 + (region.id - 4) * 100 + 50}
                  y={region.id <= 3 ? 175 : 325}
                  textAnchor="middle"
                  fill="currentColor"
                  className="text-xs pointer-events-none"
                >
                  {region.label}
                </text>
              )}
            </g>
          ))}
        </svg>
      </div>

      {/* Grid Overlay for context */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-5"
        style={{
          backgroundImage: 'linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)',
          backgroundSize: '50px 50px'
        }}
      />

      {/* Edit Mode Context Actions */}
      {editMode !== 'solid' && (
        <div className="absolute bottom-3 left-3 bg-card border border-border rounded-lg shadow-sm p-2 flex gap-1">
          <Button variant="ghost" size="sm" className="h-7 text-xs">
            <RotateCcwIcon className="size-3 mr-1" />
            Reanalyze
          </Button>
          <Button variant="ghost" size="sm" className="h-7 text-xs">
            Subdivide
          </Button>
          <Button variant="ghost" size="sm" className="h-7 text-xs">
            Pin
          </Button>
          <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive">
            Delete
          </Button>
        </div>
      )}

      {/* Camera/View Info */}
      <div className="absolute bottom-3 right-3 bg-card border border-border rounded-lg shadow-sm px-2 py-1">
        <span className="text-xs text-muted-foreground">
          {viewport.viewType === 'perspective' ? '45°' : viewTypeLabels[viewport.viewType]}
        </span>
      </div>
    </div>
  );
}
