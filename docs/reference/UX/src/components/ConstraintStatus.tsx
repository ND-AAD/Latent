import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  CheckCircle2Icon, 
  AlertTriangleIcon, 
  XCircleIcon,
  ChevronUpIcon,
  ChevronDownIcon
} from 'lucide-react';
import { useState } from 'react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';

export function ConstraintStatus() {
  const [isExpanded, setIsExpanded] = useState(false);

  const constraints = {
    physical: [
      { name: 'Draft angles valid', status: 'pass' as const },
      { name: 'Wall thickness adequate', status: 'pass' as const },
      { name: 'Undercuts detected', status: 'fail' as const, message: 'Region 3 contains 2 undercuts' },
    ],
    manufacturing: [
      { name: 'Registration keys', status: 'pass' as const },
      { name: 'Seam accessibility', status: 'warning' as const, message: 'Region 4 has difficult seam access' },
      { name: 'Mold piece count', status: 'pass' as const },
    ],
    mathematical: [
      { name: 'Region unity', status: 'pass' as const },
      { name: 'Boundary smoothness', status: 'warning' as const, message: 'Consider smoothing 3 boundary segments' },
      { name: 'Topological validity', status: 'pass' as const },
    ]
  };

  const getOverallStatus = () => {
    const allConstraints = [...constraints.physical, ...constraints.manufacturing, ...constraints.mathematical];
    if (allConstraints.some(c => c.status === 'fail')) return 'fail';
    if (allConstraints.some(c => c.status === 'warning')) return 'warning';
    return 'pass';
  };

  const overallStatus = getOverallStatus();

  const StatusIcon = ({ status }: { status: 'pass' | 'warning' | 'fail' }) => {
    if (status === 'pass') return <CheckCircle2Icon className="size-4 text-green-600" />;
    if (status === 'warning') return <AlertTriangleIcon className="size-4 text-yellow-600" />;
    return <XCircleIcon className="size-4 text-red-600" />;
  };

  const getStatusColor = (status: string) => {
    if (status === 'pass') return 'bg-green-600/10 text-green-600 border-green-600/20';
    if (status === 'warning') return 'bg-yellow-600/10 text-yellow-600 border-yellow-600/20';
    return 'bg-red-600/10 text-red-600 border-red-600/20';
  };

  return (
    <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
      <div className="border-t border-border bg-card">
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            className="w-full h-12 rounded-none flex items-center justify-between px-4 hover:bg-accent"
          >
            <div className="flex items-center gap-3">
              <StatusIcon status={overallStatus} />
              <span className="font-medium">
                {overallStatus === 'pass' && 'All Constraints Satisfied'}
                {overallStatus === 'warning' && '2 Warnings Detected'}
                {overallStatus === 'fail' && '1 Critical Issue Found'}
              </span>
              <Badge 
                variant="outline" 
                className={getStatusColor(overallStatus)}
              >
                Physical • Manufacturing • Mathematical
              </Badge>
            </div>
            {isExpanded ? (
              <ChevronDownIcon className="size-4" />
            ) : (
              <ChevronUpIcon className="size-4" />
            )}
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-4 pb-4 pt-2">
            <div className="grid grid-cols-3 gap-4">
              {/* Physical Constraints */}
              <Card className="p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <h4>Physical</h4>
                  <Badge variant="outline" className={getStatusColor('fail')}>
                    {constraints.physical.filter(c => c.status === 'fail').length} Fail
                  </Badge>
                </div>
                <div className="space-y-2">
                  {constraints.physical.map((constraint, i) => (
                    <div key={i} className="space-y-1">
                      <div className="flex items-start gap-2">
                        <StatusIcon status={constraint.status} />
                        <div className="flex-1">
                          <p className="text-sm">{constraint.name}</p>
                          {constraint.message && (
                            <p className="text-xs text-muted-foreground">{constraint.message}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Manufacturing Constraints */}
              <Card className="p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <h4>Manufacturing</h4>
                  <Badge variant="outline" className={getStatusColor('warning')}>
                    {constraints.manufacturing.filter(c => c.status === 'warning').length} Warning
                  </Badge>
                </div>
                <div className="space-y-2">
                  {constraints.manufacturing.map((constraint, i) => (
                    <div key={i} className="space-y-1">
                      <div className="flex items-start gap-2">
                        <StatusIcon status={constraint.status} />
                        <div className="flex-1">
                          <p className="text-sm">{constraint.name}</p>
                          {constraint.message && (
                            <p className="text-xs text-muted-foreground">{constraint.message}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Mathematical Constraints */}
              <Card className="p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <h4>Mathematical</h4>
                  <Badge variant="outline" className={getStatusColor('warning')}>
                    {constraints.mathematical.filter(c => c.status === 'warning').length} Warning
                  </Badge>
                </div>
                <div className="space-y-2">
                  {constraints.mathematical.map((constraint, i) => (
                    <div key={i} className="space-y-1">
                      <div className="flex items-start gap-2">
                        <StatusIcon status={constraint.status} />
                        <div className="flex-1">
                          <p className="text-sm">{constraint.name}</p>
                          {constraint.message && (
                            <p className="text-xs text-muted-foreground">{constraint.message}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}
