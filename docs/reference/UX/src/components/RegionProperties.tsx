import { Card } from './ui/card';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Slider } from './ui/slider';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { useState } from 'react';
import type { EditMode } from '../App';

interface RegionPropertiesProps {
  selectedRegion: number | null;
  editMode: EditMode;
}

export function RegionProperties({ selectedRegion, editMode }: RegionPropertiesProps) {
  const [draftAngle, setDraftAngle] = useState([3]);
  const [wallThickness, setWallThickness] = useState([8]);

  if (!selectedRegion) {
    return (
      <div className="flex items-center justify-center h-64 text-center">
        <div className="space-y-2">
          <p className="text-muted-foreground">
            {editMode === 'edge' && 'No edge selected'}
            {editMode === 'vertex' && 'No vertex selected'}
            {editMode === 'panel' && 'No panel selected'}
            {editMode === 'solid' && 'No region selected'}
          </p>
          <p className="text-sm text-muted-foreground">
            {editMode === 'edge' && 'Select an edge to view and edit its properties'}
            {editMode === 'vertex' && 'Select a vertex to view and edit its properties'}
            {editMode === 'panel' && 'Select a panel to view and edit its properties'}
            {editMode === 'solid' && 'Select a region to view its properties'}
          </p>
        </div>
      </div>
    );
  }

  const getTitle = () => {
    if (editMode === 'edge') return `Edge ${selectedRegion}`;
    if (editMode === 'vertex') return `Vertex ${selectedRegion}`;
    if (editMode === 'panel') return `Panel ${selectedRegion}`;
    return `Region ${selectedRegion}`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-1">{getTitle()}</h3>
        <p className="text-sm text-muted-foreground">
          {editMode === 'panel' ? 'Adjust mold generation parameters' : 'Edit properties'}
        </p>
      </div>

      <Card className="p-4 space-y-4">
        <div className="space-y-2">
          <Label>Region Name</Label>
          <Input defaultValue={`Region ${selectedRegion}`} />
        </div>

        <Separator />

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Draft Angle</Label>
            <span className="text-sm text-muted-foreground tabular-nums">{draftAngle[0]}°</span>
          </div>
          <Slider 
            value={draftAngle} 
            onValueChange={setDraftAngle}
            min={0}
            max={15}
            step={0.5}
          />
          <p className="text-xs text-muted-foreground">
            Taper for removing cast piece from mold
          </p>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Wall Thickness</Label>
            <span className="text-sm text-muted-foreground tabular-nums">{wallThickness[0]}mm</span>
          </div>
          <Slider 
            value={wallThickness} 
            onValueChange={setWallThickness}
            min={3}
            max={20}
            step={0.5}
          />
          <p className="text-xs text-muted-foreground">
            Plaster mold wall thickness
          </p>
        </div>

        <Separator />

        <div className="space-y-2">
          <Label>Surface Area</Label>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">142.3 cm²</Badge>
            <span className="text-xs text-muted-foreground">(23.8% of total)</span>
          </div>
        </div>

        <div className="space-y-2">
          <Label>Seam Length</Label>
          <Badge variant="secondary">38.6 cm</Badge>
        </div>
      </Card>

      <div className="space-y-2">
        <Button className="w-full" variant="outline">
          Edit Boundary
        </Button>
        <Button className="w-full" variant="outline">
          Split Region
        </Button>
        <Button className="w-full" variant="destructive">
          Delete Region
        </Button>
      </div>

      <Card className="p-4 space-y-2">
        <Label>History</Label>
        <div className="space-y-1 text-xs text-muted-foreground">
          <div>• Discovered by Curvature Analysis</div>
          <div>• Boundary adjusted manually</div>
          <div>• Draft angle modified</div>
        </div>
        <Button variant="ghost" size="sm" className="w-full mt-2">
          Reset to Discovered
        </Button>
      </Card>
    </div>
  );
}
