import { useState } from 'react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { 
  PlusIcon, 
  CheckIcon,
  CopyIcon,
  TrashIcon,
  ChevronRightIcon,
  ChevronLeftIcon
} from 'lucide-react';
import { cn } from './ui/utils';

interface IterationManagerProps {
  currentIteration: number;
  onIterationChange: (iteration: number) => void;
}

interface Iteration {
  id: number;
  name: string;
  timestamp: string;
  thumbnail?: string;
}

export function IterationManager({ currentIteration, onIterationChange }: IterationManagerProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [iterations, setIterations] = useState<Iteration[]>([
    { id: 1, name: 'Initial Analysis', timestamp: '10:24 AM' },
    { id: 2, name: 'Refined Boundaries', timestamp: '10:45 AM' },
    { id: 3, name: 'Draft Angle Test', timestamp: '11:12 AM' },
  ]);

  const addNewIteration = () => {
    const newId = Math.max(...iterations.map(i => i.id)) + 1;
    const now = new Date();
    const timestamp = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    
    setIterations([...iterations, {
      id: newId,
      name: `Iteration ${newId}`,
      timestamp
    }]);
    onIterationChange(newId);
  };

  const deleteIteration = (id: number) => {
    if (iterations.length > 1) {
      setIterations(iterations.filter(i => i.id !== id));
      if (currentIteration === id) {
        onIterationChange(iterations[0].id);
      }
    }
  };

  const duplicateIteration = (id: number) => {
    const iteration = iterations.find(i => i.id === id);
    if (iteration) {
      const newId = Math.max(...iterations.map(i => i.id)) + 1;
      const now = new Date();
      const timestamp = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
      
      setIterations([...iterations, {
        id: newId,
        name: `${iteration.name} (Copy)`,
        timestamp
      }]);
    }
  };

  if (!isExpanded) {
    return (
      <div className="w-12 border-r border-border bg-card flex flex-col items-center py-4">
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-8 w-8 p-0 mb-4"
          onClick={() => setIsExpanded(true)}
        >
          <ChevronRightIcon className="size-4" />
        </Button>
        
        <div className="flex-1 flex flex-col gap-2">
          {iterations.map((iteration) => (
            <button
              key={iteration.id}
              className={cn(
                "size-8 rounded flex items-center justify-center text-xs transition-colors",
                currentIteration === iteration.id
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted hover:bg-muted-foreground/10"
              )}
              onClick={() => onIterationChange(iteration.id)}
            >
              {iteration.id}
            </button>
          ))}
        </div>
        
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-8 w-8 p-0 mt-4"
          onClick={addNewIteration}
        >
          <PlusIcon className="size-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="w-64 border-r border-border bg-card flex flex-col">
      <div className="h-14 border-b border-border px-4 flex items-center justify-between">
        <h3>Design Iterations</h3>
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-7 w-7 p-0"
          onClick={() => setIsExpanded(false)}
        >
          <ChevronLeftIcon className="size-4" />
        </Button>
      </div>

      <ScrollArea className="flex-1 p-3">
        <div className="space-y-2">
          {iterations.map((iteration) => {
            const isActive = currentIteration === iteration.id;
            
            return (
              <div
                key={iteration.id}
                className={cn(
                  "p-3 rounded-lg border transition-all cursor-pointer group",
                  isActive 
                    ? "border-primary bg-accent" 
                    : "border-border hover:border-muted-foreground/30 hover:bg-accent/50"
                )}
                onClick={() => onIterationChange(iteration.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      "size-6 rounded flex items-center justify-center text-xs shrink-0",
                      isActive ? "bg-primary text-primary-foreground" : "bg-muted"
                    )}>
                      {isActive ? <CheckIcon className="size-3" /> : iteration.id}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{iteration.name}</p>
                      <p className="text-xs text-muted-foreground">{iteration.timestamp}</p>
                    </div>
                  </div>
                </div>
                
                {/* Thumbnail placeholder */}
                <div className="w-full h-24 bg-muted rounded mb-2 flex items-center justify-center">
                  <span className="text-xs text-muted-foreground">Preview</span>
                </div>
                
                {/* Quick actions */}
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 px-2 flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      duplicateIteration(iteration.id);
                    }}
                  >
                    <CopyIcon className="size-3 mr-1" />
                    <span className="text-xs">Duplicate</span>
                  </Button>
                  {iterations.length > 1 && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 px-2 text-destructive"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteIteration(iteration.id);
                      }}
                    >
                      <TrashIcon className="size-3" />
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>

      <div className="border-t border-border p-3">
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full"
          onClick={addNewIteration}
        >
          <PlusIcon className="size-4 mr-2" />
          New Iteration
        </Button>
      </div>
    </div>
  );
}
