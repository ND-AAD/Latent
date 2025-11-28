#!/usr/bin/env python3
"""
Nielsen's 10 Heuristics Evaluation Tool
Systematically evaluate interfaces against usability heuristics
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class HeuristicEvaluator:
    """Evaluate interfaces using Nielsen's 10 Usability Heuristics"""

    HEURISTICS = {
        "H1": {
            "name": "Visibility of system status",
            "description": "System should keep users informed through appropriate feedback within reasonable time",
            "checklist": [
                "Loading states are shown for async operations",
                "Progress indicators for multi-step processes",
                "Current location is clear in navigation",
                "Form submission feedback is immediate",
                "System state changes are communicated"
            ]
        },
        "H2": {
            "name": "Match between system and real world",
            "description": "System should speak users' language with familiar concepts",
            "checklist": [
                "Uses familiar terminology, not jargon",
                "Icons match real-world conventions",
                "Information appears in natural order",
                "Metaphors are appropriate to audience",
                "Date/time formats match user locale"
            ]
        },
        "H3": {
            "name": "User control and freedom",
            "description": "Users need emergency exits to leave unwanted states",
            "checklist": [
                "Undo and redo are available",
                "Cancel option for multi-step processes",
                "Clear way to exit modal dialogs",
                "Back button works as expected",
                "Changes can be reverted"
            ]
        },
        "H4": {
            "name": "Consistency and standards",
            "description": "Users shouldn't wonder whether different words mean the same thing",
            "checklist": [
                "Similar elements behave consistently",
                "Platform conventions are followed",
                "Terminology is consistent throughout",
                "Icons have consistent meaning",
                "Layout patterns are predictable"
            ]
        },
        "H5": {
            "name": "Error prevention",
            "description": "Prevent problems from occurring in the first place",
            "checklist": [
                "Confirmations for destructive actions",
                "Constraints prevent invalid input",
                "Helpful defaults are provided",
                "Options are disabled when not applicable",
                "Clear formatting examples shown"
            ]
        },
        "H6": {
            "name": "Recognition rather than recall",
            "description": "Minimize user memory load by making elements visible",
            "checklist": [
                "Options are visible, not hidden",
                "Help is contextual and accessible",
                "Previously entered data is shown",
                "Instructions are visible when needed",
                "Menu items are descriptive"
            ]
        },
        "H7": {
            "name": "Flexibility and efficiency of use",
            "description": "Accelerators for expert users while remaining accessible to novices",
            "checklist": [
                "Keyboard shortcuts available",
                "Frequent actions are streamlined",
                "Customization options exist",
                "Batch operations supported",
                "Power user features available"
            ]
        },
        "H8": {
            "name": "Aesthetic and minimalist design",
            "description": "Interfaces should not contain irrelevant information",
            "checklist": [
                "Visual hierarchy is clear",
                "Unnecessary elements removed",
                "White space used effectively",
                "Decorative elements don't distract",
                "Focus on essential information"
            ]
        },
        "H9": {
            "name": "Help users recognize, diagnose, and recover from errors",
            "description": "Error messages in plain language with solutions",
            "checklist": [
                "Error messages are specific",
                "Solutions are suggested",
                "No error codes shown to users",
                "Visual treatment distinguishes errors",
                "Recovery path is clear"
            ]
        },
        "H10": {
            "name": "Help and documentation",
            "description": "Help should be easy to search, focused on user tasks",
            "checklist": [
                "Help is searchable",
                "Documentation is task-oriented",
                "Steps are concrete and specific",
                "Examples are provided",
                "Context-sensitive help available"
            ]
        }
    }

    SEVERITY_LEVELS = {
        0: "No problem",
        1: "Cosmetic - fix if time permits",
        2: "Minor - low priority fix",
        3: "Major - high priority fix",
        4: "Catastrophic - must fix before release"
    }

    def evaluate(self, interface_name: str) -> Dict:
        """
        Conduct heuristic evaluation

        Args:
            interface_name: Name of interface being evaluated

        Returns:
            Evaluation results dictionary
        """
        results = {
            "interface": interface_name,
            "date": datetime.now().isoformat(),
            "evaluator": "AI Assistant",
            "findings": [],
            "summary": {}
        }

        print(f"\\n{'='*60}")
        print(f"Heuristic Evaluation: {interface_name}")
        print(f"{'='*60}\\n")

        total_issues = 0
        severity_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for h_id, heuristic in self.HEURISTICS.items():
            print(f"\\n{h_id}: {heuristic['name']}")
            print(f"Description: {heuristic['description']}")
            print("\\nChecklist:")

            for i, item in enumerate(heuristic['checklist'], 1):
                print(f"  {i}. {item}")

            # Simulated evaluation (in practice, would be manual or AI-assisted)
            has_issue = input(f"\\nAny issues with {h_id}? (y/n): ").lower() == 'y'

            if has_issue:
                issue = {
                    "heuristic": h_id,
                    "name": heuristic['name'],
                    "description": input("Describe the issue: "),
                    "location": input("Where in the interface: "),
                    "severity": int(input("Severity (0-4): ")),
                    "recommendation": input("Suggested fix: ")
                }
                results['findings'].append(issue)
                total_issues += 1
                severity_counts[issue['severity']] += 1

        # Generate summary
        results['summary'] = {
            "total_issues": total_issues,
            "severity_breakdown": severity_counts,
            "critical_issues": severity_counts[4],
            "major_issues": severity_counts[3]
        }

        return results

    def generate_report(self, results: Dict) -> str:
        """Generate markdown report from evaluation results"""

        report = f"""# Heuristic Evaluation Report

## Interface: {results['interface']}
**Date:** {results['date']}
**Evaluator:** {results['evaluator']}

## Executive Summary
- **Total Issues Found:** {results['summary']['total_issues']}
- **Critical Issues:** {results['summary']['critical_issues']}
- **Major Issues:** {results['summary']['major_issues']}

### Severity Breakdown
"""

        for severity, count in results['summary']['severity_breakdown'].items():
            if count > 0:
                report += f"- {self.SEVERITY_LEVELS[severity]}: {count}\\n"

        report += "\\n## Detailed Findings\\n"

        # Group by severity
        for severity in [4, 3, 2, 1, 0]:
            severity_findings = [f for f in results['findings'] if f['severity'] == severity]
            if severity_findings:
                report += f"\\n### {self.SEVERITY_LEVELS[severity]}\\n"
                for finding in severity_findings:
                    report += f"""
**{finding['heuristic']}: {finding['name']}**
- **Location:** {finding['location']}
- **Issue:** {finding['description']}
- **Recommendation:** {finding['recommendation']}
"""

        report += """
## Next Steps
1. Address critical issues immediately
2. Plan major issues for next sprint
3. Schedule minor issues in backlog
4. Consider cosmetic issues for polish phase
5. Re-evaluate after fixes implemented
"""

        return report

def main():
    """Run heuristic evaluation"""
    evaluator = HeuristicEvaluator()

    print("Nielsen's 10 Heuristics Evaluation Tool")
    print("=" * 40)

    interface_name = input("Enter interface/page name to evaluate: ")
    results = evaluator.evaluate(interface_name)

    # Save results
    with open(f"heuristic_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)

    # Generate report
    report = evaluator.generate_report(results)
    report_file = f"heuristic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\\n✅ Evaluation complete!")
    print(f"Results saved to: {report_file}")

    # Show summary
    print(f"\\nSummary: {results['summary']['total_issues']} issues found")
    if results['summary']['critical_issues'] > 0:
        print(f"⚠️  {results['summary']['critical_issues']} CRITICAL issues need immediate attention!")

if __name__ == "__main__":
    main()