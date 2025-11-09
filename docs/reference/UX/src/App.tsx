import { useState } from 'react';
import { ViewportGrid } from './components/ViewportGrid';
import { Toolbar } from './components/Toolbar';
import { SidePanel } from './components/SidePanel';
import { ConstraintStatus } from './components/ConstraintStatus';
import { IterationManager } from './components/IterationManager';
import { Toaster } from './components/ui/sonner';

export type EditMode = 'panel' | 'edge' | 'vertex' | 'solid';
export type ViewType = 'perspective' | 'top' | 'front' | 'right' | 'isometric' | 'axonometric';
export type ViewportLayout = '1' | '2-horizontal' | '2-vertical' | '4-grid';

export interface Viewport {
  id: string;
  viewType: ViewType;
  displayMode: 'solid' | 'wireframe' | 'xray';
}

export default function App() {
  const [isPanelCollapsed, setIsPanelCollapsed] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState<number | null>(1);
  const [selectedLens, setSelectedLens] = useState<string>('curvature');
  const [editMode, setEditMode] = useState<EditMode>('panel');
  const [currentIteration, setCurrentIteration] = useState(1);
  const [viewportLayout, setViewportLayout] = useState<ViewportLayout>('1');
  
  const [viewports, setViewports] = useState<Viewport[]>([
    { id: '1', viewType: 'perspective', displayMode: 'solid' }
  ]);

  return (
    <div className="size-full flex flex-col bg-background overflow-hidden">
      <Toolbar 
        editMode={editMode}
        onEditModeChange={setEditMode}
        isPanelCollapsed={isPanelCollapsed}
        onTogglePanel={() => setIsPanelCollapsed(!isPanelCollapsed)}
        viewportLayout={viewportLayout}
        onViewportLayoutChange={setViewportLayout}
      />
      
      <div className="flex-1 flex overflow-hidden">
        <IterationManager 
          currentIteration={currentIteration}
          onIterationChange={setCurrentIteration}
        />
        
        <ViewportGrid 
          viewports={viewports}
          layout={viewportLayout}
          editMode={editMode}
          selectedRegion={selectedRegion}
          onRegionSelect={setSelectedRegion}
          onViewportsChange={setViewports}
        />
        
        {!isPanelCollapsed && (
          <SidePanel 
            selectedRegion={selectedRegion}
            onRegionSelect={setSelectedRegion}
            selectedLens={selectedLens}
            onLensChange={setSelectedLens}
            editMode={editMode}
          />
        )}
      </div>
      
      <ConstraintStatus />
      
      <Toaster />
    </div>
  );
}
