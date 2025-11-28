#!/usr/bin/env python3
"""
Component Generator
Creates boilerplate for accessible, well-structured UI components
"""

import os
from datetime import datetime
from typing import Optional

class ComponentGenerator:
    """Generate component boilerplate following best practices"""

    COMPONENT_TEMPLATES = {
        "react": {
            "component": '''import React from 'react';
import PropTypes from 'prop-types';
import './{name}.css';

/**
 * {name} Component
 * {description}
 */
const {name} = ({{
  children,
  className = '',
  variant = 'default',
  disabled = false,
  ariaLabel,
  ...props
}}) => {{
  const baseClass = '{kebab_name}';
  const classes = `${{baseClass}} ${{baseClass}}--${{variant}} ${{className}}`.trim();

  return (
    <div
      className={{classes}}
      aria-label={{ariaLabel}}
      aria-disabled={{disabled}}
      role="{role}"
      {{...props}}
    >
      {{children}}
    </div>
  );
}};

{name}.propTypes = {{
  children: PropTypes.node,
  className: PropTypes.string,
  variant: PropTypes.oneOf(['default', 'primary', 'secondary']),
  disabled: PropTypes.bool,
  ariaLabel: PropTypes.string,
}};

export default {name};
''',
            "styles": '''/* {name} Component Styles */

.{kebab_name} {{
  /* Base styles */
  position: relative;
  display: flex;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  font-family: var(--font-family);
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}}

/* Variants */
.{kebab_name}--primary {{
  color: var(--color-white);
  background: var(--color-primary);
  border-color: var(--color-primary);
}}

.{kebab_name}--secondary {{
  color: var(--color-primary);
  background: transparent;
  border-color: var(--color-primary);
}}

/* States */
.{kebab_name}:hover:not([aria-disabled="true"]) {{
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}}

.{kebab_name}:focus-visible {{
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}}

.{kebab_name}[aria-disabled="true"] {{
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}}

/* Responsive */
@media (max-width: 768px) {{
  .{kebab_name} {{
    padding: var(--spacing-2) var(--spacing-3);
    font-size: var(--text-sm);
  }}
}}

/* High contrast mode */
@media (prefers-contrast: high) {{
  .{kebab_name} {{
    border-width: 2px;
  }}
}}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {{
  .{kebab_name} {{
    transition: none;
  }}
}}
''',
            "test": '''import React from 'react';
import {{ render, screen, fireEvent }} from '@testing-library/react';
import {name} from './{name}';

describe('{name}', () => {{
  test('renders children', () => {{
    render(<{name}>Test Content</{name}>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  }});

  test('applies custom className', () => {{
    render(<{name} className="custom-class">Test</{name}>);
    const element = screen.getByRole('{role}');
    expect(element).toHaveClass('custom-class');
  }});

  test('handles disabled state', () => {{
    render(<{name} disabled>Test</{name}>);
    const element = screen.getByRole('{role}');
    expect(element).toHaveAttribute('aria-disabled', 'true');
  }});

  test('applies variant styles', () => {{
    render(<{name} variant="primary">Test</{name}>);
    const element = screen.getByRole('{role}');
    expect(element).toHaveClass('{kebab_name}--primary');
  }});

  test('supports aria-label', () => {{
    render(<{name} ariaLabel="Custom label">Test</{name}>);
    const element = screen.getByRole('{role}');
    expect(element).toHaveAttribute('aria-label', 'Custom label');
  }});
}});
''',
            "story": '''import React from 'react';
import {name} from './{name}';

export default {{
  title: 'Components/{name}',
  component: {name},
  argTypes: {{
    variant: {{
      control: {{ type: 'select' }},
      options: ['default', 'primary', 'secondary'],
    }},
    disabled: {{
      control: {{ type: 'boolean' }},
    }},
  }},
}};

const Template = (args) => <{name} {{...args}} />;

export const Default = Template.bind({{}});
Default.args = {{
  children: '{name} Content',
}};

export const Primary = Template.bind({{}});
Primary.args = {{
  children: '{name} Content',
  variant: 'primary',
}};

export const Secondary = Template.bind({{}});
Secondary.args = {{
  children: '{name} Content',
  variant: 'secondary',
}};

export const Disabled = Template.bind({{}});
Disabled.args = {{
  children: '{name} Content',
  disabled: true,
}};
''',
            "docs": '''# {name}

## Description
{description}

## Usage
```jsx
import {name} from './components/{name}';

function App() {{
  return (
    <{name} variant="primary">
      Your content here
    </{name}>
  );
}}
```

## Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| children | node | - | Content to render inside the component |
| className | string | '' | Additional CSS classes |
| variant | string | 'default' | Visual variant: default, primary, secondary |
| disabled | bool | false | Whether the component is disabled |
| ariaLabel | string | - | Accessible label for screen readers |

## Variants
- **default**: Standard appearance
- **primary**: Primary action style
- **secondary**: Secondary action style

## Accessibility
- Proper ARIA attributes
- Keyboard navigation support
- Focus indicators
- Screen reader friendly

## Examples

### Basic Usage
```jsx
<{name}>Basic content</{name}>
```

### With Variant
```jsx
<{name} variant="primary">Primary variant</{name}>
```

### Disabled State
```jsx
<{name} disabled>Disabled content</{name}>
```

### With Custom Styling
```jsx
<{name} className="custom-class">Custom styled</{name}>
```
'''
        }
    }

    def __init__(self, framework: str = "react"):
        """Initialize generator with specified framework"""
        self.framework = framework
        self.templates = self.COMPONENT_TEMPLATES.get(framework, {})

    def generate(self, name: str, description: str = "", role: str = "region",
                output_dir: Optional[str] = None):
        """
        Generate component files

        Args:
            name: Component name (PascalCase)
            description: Component description
            role: ARIA role for the component
            output_dir: Output directory path
        """
        # Convert name to different cases
        kebab_name = self._to_kebab_case(name)

        # Set output directory
        if not output_dir:
            output_dir = f"./components/{name}"

        # Create directory
        os.makedirs(output_dir, exist_ok=True)

        # Template variables
        vars = {
            "name": name,
            "kebab_name": kebab_name,
            "description": description or f"{name} component",
            "role": role,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        # Generate files
        files_created = []

        # Component file
        if "component" in self.templates:
            component_file = f"{output_dir}/{name}.jsx"
            self._write_file(component_file, self.templates["component"].format(**vars))
            files_created.append(component_file)

        # Styles file
        if "styles" in self.templates:
            styles_file = f"{output_dir}/{name}.css"
            self._write_file(styles_file, self.templates["styles"].format(**vars))
            files_created.append(styles_file)

        # Test file
        if "test" in self.templates:
            test_file = f"{output_dir}/{name}.test.js"
            self._write_file(test_file, self.templates["test"].format(**vars))
            files_created.append(test_file)

        # Storybook file
        if "story" in self.templates:
            story_file = f"{output_dir}/{name}.stories.js"
            self._write_file(story_file, self.templates["story"].format(**vars))
            files_created.append(story_file)

        # Documentation file
        if "docs" in self.templates:
            docs_file = f"{output_dir}/README.md"
            self._write_file(docs_file, self.templates["docs"].format(**vars))
            files_created.append(docs_file)

        # Index file for exports
        index_content = f"export {{ default }} from './{name}';\n"
        index_file = f"{output_dir}/index.js"
        self._write_file(index_file, index_content)
        files_created.append(index_file)

        return files_created

    @staticmethod
    def _to_kebab_case(name: str) -> str:
        """Convert PascalCase to kebab-case"""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('-')
            result.append(char.lower())
        return ''.join(result)

    @staticmethod
    def _write_file(filepath: str, content: str):
        """Write content to file"""
        with open(filepath, 'w') as f:
            f.write(content)

def main():
    """Interactive component generator"""
    print("Component Generator")
    print("=" * 40)

    # Get framework
    framework = input("Framework (react/vue/angular) [react]: ").lower() or "react"
    generator = ComponentGenerator(framework)

    # Get component details
    name = input("Component name (PascalCase): ")
    if not name:
        print("Component name is required!")
        return

    description = input("Description (optional): ")
    role = input("ARIA role [region]: ") or "region"
    output_dir = input(f"Output directory [./components/{name}]: ") or None

    # Generate component
    try:
        files = generator.generate(name, description, role, output_dir)
        print(f"\\n✅ Component '{name}' generated successfully!")
        print("\\nFiles created:")
        for file in files:
            print(f"  - {file}")
        print(f"\\n📁 Component location: {output_dir or f'./components/{name}'}")
    except Exception as e:
        print(f"❌ Error generating component: {e}")

if __name__ == "__main__":
    main()