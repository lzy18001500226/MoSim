# Tool Renderer Registry

Custom renderers for specific tools in the conversation UI.

## Architecture

```
MessageBlock (renders messages)
  └─> ToolUseRenderer (renders tool uses)
       └─> getToolRenderer(toolName)
            ├─> If found: <CustomRenderer />
            │    └─> TodoListRenderer (for TodoWrite)
            │    └─> [Add more here...]
            └─> If not found: <DefaultRenderer />
```

## How to Add a New Tool Renderer

### 1. Create the Component

Create `MyToolRenderer.tsx`:

```typescript
import type React from 'react';
import type { ToolRendererProps } from './index';
import { theme } from 'antd';

export const MyToolRenderer: React.FC<ToolRendererProps> = ({ input, result }) => {
  const { token } = theme.useToken();

  // Extract typed input
  const myToolInput = input as { /* your tool's input type */ };

  return (
    <div style={{
      padding: token.sizeUnit * 1.5,
      borderRadius: token.borderRadius,
      background: token.colorBgContainer,
      border: `1px solid ${token.colorBorder}`,
    }}>
      {/* Your custom rendering */}
    </div>
  );
};
```

### 2. Register in `index.ts`

```typescript
import { MyToolRenderer } from './MyToolRenderer';

export const TOOL_RENDERERS = new Map<string, ToolRenderer>([
  ['TodoWrite', TodoListRenderer as ToolRenderer],
  ['MyTool', MyToolRenderer as ToolRenderer], // <-- Add here
]);
```

### 3. Create Storybook Stories (Optional)

Create `MyToolRenderer.stories.tsx`:

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { MyToolRenderer } from './MyToolRenderer';

const meta = {
  title: 'Tool Renderers/MyToolRenderer',
  component: MyToolRenderer,
} satisfies Meta<typeof MyToolRenderer>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    input: {
      /* example input */
    },
  },
};
```

## Design Guidelines

When creating custom tool renderers:

1. **Use Ant Design tokens** for all styling (colors, spacing, borders)
2. **Support dark mode** by default (tokens handle this)
3. **Keep it compact** - inline display, no unnecessary padding
4. **Show input by default** - users want to see what parameters were used
5. **Highlight errors** - use `token.colorError` for error states
6. **Use semantic icons** - `@ant-design/icons` for consistency
7. **Add collapse/expand** for large content
8. **Consider mobile** - responsive design

## Available Props

```typescript
interface ToolRendererProps {
  input: Record<string, unknown>; // Tool input parameters
  result?: {
    // Optional tool result
    content: string | unknown[];
    is_error?: boolean;
  };
}
```

## Examples

See existing renderers:

- `TodoListRenderer.tsx` - Todo lists with checkboxes
- (Add more as they're created)

## Testing

Run Storybook to preview:

```bash
cd apps/agor-ui
pnpm storybook
# Navigate to: Tool Renderers > [Your Renderer]
```
