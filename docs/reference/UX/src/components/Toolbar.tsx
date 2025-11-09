import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { 
  FileIcon, 
  DownloadIcon, 
  SettingsIcon, 
  HelpCircleIcon,
  PanelRightIcon,
  RefreshCwIcon,
  Undo2Icon,
  Redo2Icon,
  SquareIcon,
  RectangleVerticalIcon,
  RectangleHorizontalIcon,
  Grid2x2Icon,
  BoxSelectIcon,
  GitBranchIcon,
  MousePointerClickIcon
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from './ui/dropdown-menu';
import { ToggleGroup, ToggleGroupItem } from './ui/toggle-group';
import type { EditMode, ViewportLayout } from '../App';

interface ToolbarProps {
  editMode: EditMode;
  onEditModeChange: (mode: EditMode) => void;
  isPanelCollapsed: boolean;
  onTogglePanel: () => void;
  viewportLayout: ViewportLayout;
  onViewportLayoutChange: (layout: ViewportLayout) => void;
}

export function Toolbar({ 
  editMode, 
  onEditModeChange, 
  isPanelCollapsed, 
  onTogglePanel,
  viewportLayout,
  onViewportLayoutChange 
}: ToolbarProps) {
  return (
    <div className="h-14 border-b border-border bg-card px-4 flex items-center justify-between">
      {/* Left Section - File and Primary Actions */}
      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <FileIcon className="size-4 mr-2" />
              File
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem>New Analysis</DropdownMenuItem>
            <DropdownMenuItem>Open...</DropdownMenuItem>
            <DropdownMenuItem>Save</DropdownMenuItem>
            <DropdownMenuItem>Save As...</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Export Molds...</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Separator orientation="vertical" className="h-6 mx-2" />

        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm">
            <Undo2Icon className="size-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Redo2Icon className="size-4" />
          </Button>
        </div>
      </div>

      {/* Center Section - Edit Mode and Viewport Layout */}
      <div className="flex items-center gap-4">
        {/* Edit Mode Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Edit:</span>
          <ToggleGroup 
            type="single" 
            value={editMode} 
            onValueChange={(value) => value && onEditModeChange(value as EditMode)}
          >
            <ToggleGroupItem value="solid" aria-label="Solid view">
              <MousePointerClickIcon className="size-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="panel" aria-label="Edit panels">
              <BoxSelectIcon className="size-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="edge" aria-label="Edit edges">
              <GitBranchIcon className="size-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="vertex" aria-label="Edit vertices">
              <span className="size-4 flex items-center justify-center">●</span>
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        <Separator orientation="vertical" className="h-6" />

        {/* Viewport Layout Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Layout:</span>
          <ToggleGroup 
            type="single" 
            value={viewportLayout} 
            onValueChange={(value) => value && onViewportLayoutChange(value as ViewportLayout)}
          >
            <ToggleGroupItem value="1" aria-label="Single viewport">
              <SquareIcon className="size-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="2-horizontal" aria-label="Two viewports horizontal">
              <RectangleHorizontalIcon className="size-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="2-vertical" aria-label="Two viewports vertical">
              <RectangleVerticalIcon className="size-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="4-grid" aria-label="Four viewports">
              <Grid2x2Icon className="size-4" />
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        <Separator orientation="vertical" className="h-6" />

        <Button variant="ghost" size="sm">
          <RefreshCwIcon className="size-4 mr-2" />
          Reanalyze
        </Button>
      </div>

      {/* Right Section - Utilities and Connection Status */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm">
          <DownloadIcon className="size-4 mr-2" />
          Export
        </Button>
        
        <Separator orientation="vertical" className="h-6 mx-2" />
        
        <Button variant="ghost" size="sm">
          <SettingsIcon className="size-4" />
        </Button>
        <Button variant="ghost" size="sm">
          <HelpCircleIcon className="size-4" />
        </Button>
        
        <Separator orientation="vertical" className="h-6 mx-2" />
        
        <Button 
          variant="ghost" 
          size="sm"
          onClick={onTogglePanel}
        >
          <PanelRightIcon className="size-4" />
        </Button>
        
        <Separator orientation="vertical" className="h-6 mx-2" />
        
        {/* Connection Status - moved to far right */}
        <div className="flex items-center gap-1.5">
          <div className="size-2 rounded-full bg-emerald-500" />
          <span className="text-sm text-muted-foreground">Rhino</span>
        </div>
      </div>
    </div>
  );
}
