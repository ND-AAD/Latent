import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import { 
  CircleDotIcon,
  WavesIcon,
  NetworkIcon,
  GaugeIcon,
  SparklesIcon
} from 'lucide-react';

interface MathematicalLensSelectorProps {
  selectedLens: string;
  onLensChange: (lens: string) => void;
}

const lenses = [
  {
    id: 'curvature',
    name: 'Curvature Analysis',
    icon: WavesIcon,
    description: 'Discovers regions based on surface curvature patterns',
    resonance: 92,
    color: 'rgb(147, 197, 253)'
  },
  {
    id: 'geodesic',
    name: 'Geodesic Partitioning',
    icon: NetworkIcon,
    description: 'Finds natural boundaries using geodesic distance fields',
    resonance: 85,
    color: 'rgb(196, 181, 253)'
  },
  {
    id: 'principal',
    name: 'Principal Directions',
    icon: CircleDotIcon,
    description: 'Segments by principal curvature direction alignment',
    resonance: 78,
    color: 'rgb(134, 239, 172)'
  },
  {
    id: 'harmonic',
    name: 'Harmonic Fields',
    icon: SparklesIcon,
    description: 'Uses harmonic functions to reveal mathematical structure',
    resonance: 71,
    color: 'rgb(252, 165, 165)'
  }
];

export function MathematicalLensSelector({ selectedLens, onLensChange }: MathematicalLensSelectorProps) {
  const [sensitivity, setSensitivity] = useState([65]);
  const [minRegionSize, setMinRegionSize] = useState([15]);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-1">Mathematical Lens</h3>
        <p className="text-sm text-muted-foreground">
          Select an analytical method to discover natural boundaries
        </p>
      </div>

      <div className="space-y-2">
        {lenses.map((lens) => {
          const Icon = lens.icon;
          const isSelected = selectedLens === lens.id;
          
          return (
            <Card
              key={lens.id}
              className={`p-3 cursor-pointer transition-all ${
                isSelected 
                  ? 'border-primary bg-accent' 
                  : 'hover:border-muted-foreground/30'
              }`}
              onClick={() => onLensChange(lens.id)}
            >
              <div className="flex items-start gap-3">
                <div 
                  className="size-10 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: lens.color, opacity: 0.2 }}
                >
                  <Icon className="size-5" style={{ color: lens.color }} />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium">{lens.name}</span>
                    {isSelected && (
                      <Badge variant="secondary" className="text-xs">Active</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">
                    {lens.description}
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-muted rounded-full h-1.5 overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all"
                        style={{ 
                          width: `${lens.resonance}%`,
                          backgroundColor: lens.color
                        }}
                      />
                    </div>
                    <span className="text-xs font-medium tabular-nums">
                      {lens.resonance}%
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">Resonance</span>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="space-y-4 pt-2">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Sensitivity</Label>
            <span className="text-sm text-muted-foreground tabular-nums">{sensitivity[0]}%</span>
          </div>
          <Slider 
            value={sensitivity} 
            onValueChange={setSensitivity}
            max={100}
            step={1}
          />
          <p className="text-xs text-muted-foreground">
            Higher values create more regions with finer boundaries
          </p>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Minimum Region Size</Label>
            <span className="text-sm text-muted-foreground tabular-nums">{minRegionSize[0]}%</span>
          </div>
          <Slider 
            value={minRegionSize} 
            onValueChange={setMinRegionSize}
            max={50}
            step={1}
          />
          <p className="text-xs text-muted-foreground">
            Prevents overly small regions that are difficult to cast
          </p>
        </div>

        <Button className="w-full" size="sm">
          <GaugeIcon className="size-4 mr-2" />
          Apply Analysis
        </Button>
      </div>
    </div>
  );
}
