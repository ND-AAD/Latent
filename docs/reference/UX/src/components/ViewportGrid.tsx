import { Viewport } from './Viewport';
import type { Viewport as ViewportType, ViewportLayout, EditMode } from '../App';

interface ViewportGridProps {
  viewports: ViewportType[];
  layout: ViewportLayout;
  editMode: EditMode;
  selectedRegion: number | null;
  onRegionSelect: (region: number | null) => void;
  onViewportsChange: (viewports: ViewportType[]) => void;
}

export function ViewportGrid({ 
  viewports, 
  layout, 
  editMode,
  selectedRegion, 
  onRegionSelect,
  onViewportsChange 
}: ViewportGridProps) {
  
  // Ensure we have the right number of viewports for the layout
  const getViewportsForLayout = () => {
    const defaultViewTypes: Array<ViewportType['viewType']> = ['perspective', 'top', 'front', 'right'];
    
    switch (layout) {
      case '1':
        return viewports.slice(0, 1);
      case '2-horizontal':
      case '2-vertical':
        if (viewports.length < 2) {
          return [
            viewports[0] || { id: '1', viewType: 'perspective', displayMode: 'solid' },
            { id: '2', viewType: 'top', displayMode: 'solid' }
          ];
        }
        return viewports.slice(0, 2);
      case '4-grid':
        if (viewports.length < 4) {
          const newViewports = [...viewports];
          while (newViewports.length < 4) {
            newViewports.push({
              id: `${newViewports.length + 1}`,
              viewType: defaultViewTypes[newViewports.length] || 'perspective',
              displayMode: 'solid'
            });
          }
          return newViewports;
        }
        return viewports.slice(0, 4);
    }
  };

  const activeViewports = getViewportsForLayout();

  const getGridClass = () => {
    switch (layout) {
      case '1':
        return 'grid-cols-1';
      case '2-horizontal':
        return 'grid-cols-2';
      case '2-vertical':
        return 'grid-rows-2';
      case '4-grid':
        return 'grid-cols-2 grid-rows-2';
    }
  };

  return (
    <div className={`flex-1 grid ${getGridClass()} gap-px bg-border overflow-hidden`}>
      {activeViewports.map((viewport, index) => (
        <Viewport
          key={viewport.id}
          viewport={viewport}
          editMode={editMode}
          selectedRegion={selectedRegion}
          onRegionSelect={onRegionSelect}
          onViewportChange={(updated) => {
            const newViewports = [...viewports];
            newViewports[index] = updated;
            onViewportsChange(newViewports);
          }}
        />
      ))}
    </div>
  );
}
