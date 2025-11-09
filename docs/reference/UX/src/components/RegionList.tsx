import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  PinIcon,
  Edit3Icon,
  TrashIcon,
  EyeIcon,
  EyeOffIcon,
  AlertTriangleIcon,
  ScissorsIcon
} from 'lucide-react';
import { useState } from 'react';
import type { EditMode } from '../App';

interface RegionListProps {
  selectedRegion: number | null;
  onRegionSelect: (region: number | null) => void;
  editMode: EditMode;
}

const mockRegions = [
  { id: 1, name: 'Region 1', unity: 94, pinned: true, visible: true, hasWarning: false, color: 'rgb(147, 197, 253)' },
  { id: 2, name: 'Region 2', unity: 88, pinned: false, visible: true, hasWarning: false, color: 'rgb(252, 165, 165)' },
  { id: 3, name: 'Region 3', unity: 91, pinned: false, visible: true, hasWarning: true, color: 'rgb(196, 181, 253)' },
  { id: 4, name: 'Region 4', unity: 76, pinned: false, visible: true, hasWarning: false, color: 'rgb(134, 239, 172)' },
  { id: 5, name: 'Region 5', unity: 82, pinned: false, visible: false, hasWarning: false, color: 'rgb(253, 224, 71)' },
];

export function RegionList({ selectedRegion, onRegionSelect, editMode }: RegionListProps) {
  const [regions, setRegions] = useState(mockRegions);

  const togglePin = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setRegions(regions.map(r => 
      r.id === id ? { ...r, pinned: !r.pinned } : r
    ));
  };

  const toggleVisibility = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setRegions(regions.map(r => 
      r.id === id ? { ...r, visible: !r.visible } : r
    ));
  };

  const getTitle = () => {
    if (editMode === 'edge') return 'Edges';
    if (editMode === 'vertex') return 'Vertices';
    return 'Discovered Regions';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3>{getTitle()}</h3>
          <p className="text-sm text-muted-foreground">
            {editMode === 'edge' && '12 edges'}
            {editMode === 'vertex' && '9 vertices'}
            {editMode === 'panel' && `${regions.length} regions found`}
            {editMode === 'solid' && `${regions.length} regions`}
          </p>
        </div>
        {editMode === 'panel' && (
          <Button variant="outline" size="sm">
            Merge
          </Button>
        )}
      </div>

      <div className="space-y-2">
        {regions.map((region) => {
          const isSelected = selectedRegion === region.id;
          
          return (
            <Card
              key={region.id}
              className={`p-3 cursor-pointer transition-all ${
                isSelected 
                  ? 'border-primary bg-accent' 
                  : 'hover:border-muted-foreground/30'
              }`}
              onClick={() => onRegionSelect(region.id)}
            >
              <div className="flex items-start gap-3">
                <div 
                  className="size-10 rounded-lg flex-shrink-0 border-2 border-white dark:border-gray-800"
                  style={{ backgroundColor: region.color }}
                />
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium">{region.name}</span>
                    {region.pinned && (
                      <Badge variant="secondary" className="text-xs">
                        <PinIcon className="size-3 mr-1" />
                        Pinned
                      </Badge>
                    )}
                    {region.hasWarning && (
                      <AlertTriangleIcon className="size-4 text-yellow-600" />
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex-1 bg-muted rounded-full h-1.5 overflow-hidden">
                      <div 
                        className="h-full rounded-full"
                        style={{ 
                          width: `${region.unity}%`,
                          backgroundColor: region.color
                        }}
                      />
                    </div>
                    <span className="text-xs font-medium tabular-nums">
                      {region.unity}%
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">Unity Strength</span>
                  
                  <div className="flex items-center gap-1 mt-2">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-7 px-2"
                      onClick={(e) => togglePin(region.id, e)}
                    >
                      <PinIcon className={`size-3 ${region.pinned ? 'fill-current' : ''}`} />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-7 px-2"
                      onClick={(e) => toggleVisibility(region.id, e)}
                    >
                      {region.visible ? (
                        <EyeIcon className="size-3" />
                      ) : (
                        <EyeOffIcon className="size-3" />
                      )}
                    </Button>
                    {editMode === 'panel' && (
                      <Button variant="ghost" size="sm" className="h-7 px-2">
                        <ScissorsIcon className="size-3" />
                      </Button>
                    )}
                    <Button variant="ghost" size="sm" className="h-7 px-2">
                      <Edit3Icon className="size-3" />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 px-2 text-destructive">
                      <TrashIcon className="size-3" />
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
