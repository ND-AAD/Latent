import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { MathematicalLensSelector } from './MathematicalLensSelector';
import { RegionList } from './RegionList';
import { RegionProperties } from './RegionProperties';
import { ScrollArea } from './ui/scroll-area';
import type { EditMode } from '../App';

interface SidePanelProps {
  selectedRegion: number | null;
  onRegionSelect: (region: number | null) => void;
  selectedLens: string;
  onLensChange: (lens: string) => void;
  editMode: EditMode;
}

export function SidePanel({ selectedRegion, onRegionSelect, selectedLens, onLensChange, editMode }: SidePanelProps) {
  // Determine default tab based on edit mode
  const getDefaultTab = () => {
    if (editMode === 'panel') return 'regions';
    if (editMode === 'edge' || editMode === 'vertex') return 'properties';
    return 'analysis';
  };

  return (
    <div className="w-[380px] border-l border-border bg-card flex flex-col">
      <Tabs value={getDefaultTab()} className="flex-1 flex flex-col">
        <TabsList className="w-full rounded-none border-b border-border h-12 bg-transparent justify-start px-4">
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="regions">
            {editMode === 'panel' ? 'Panels' : 
             editMode === 'edge' ? 'Edges' : 
             editMode === 'vertex' ? 'Vertices' : 'Regions'}
          </TabsTrigger>
          <TabsTrigger value="properties">Properties</TabsTrigger>
        </TabsList>

        <ScrollArea className="flex-1">
          <TabsContent value="analysis" className="p-4 space-y-6 mt-0">
            <MathematicalLensSelector 
              selectedLens={selectedLens}
              onLensChange={onLensChange}
            />
          </TabsContent>

          <TabsContent value="regions" className="p-4 mt-0">
            <RegionList 
              selectedRegion={selectedRegion}
              onRegionSelect={onRegionSelect}
              editMode={editMode}
            />
          </TabsContent>

          <TabsContent value="properties" className="p-4 mt-0">
            <RegionProperties 
              selectedRegion={selectedRegion}
              editMode={editMode}
            />
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  );
}
