import type { Preview } from '@storybook/react-vite';
import { App, ConfigProvider, theme } from 'antd';

// Component to provide theme-aware background that fills entire Storybook canvas
const ThemeBackground = ({ children }) => {
  const { token } = theme.useToken();

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: token.colorBgLayout,
        overflow: 'auto',
      }}
    >
      <div
        style={{
          padding: '20px',
          minHeight: '100%',
        }}
      >
        {children}
      </div>
    </div>
  );
};

// Global decorator to wrap all stories with Ant Design ConfigProvider
const withAntdTheme = (Story, context) => {
  const isDark = context.globals.theme === 'dark';

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <App>
        <ThemeBackground>
          <Story />
        </ThemeBackground>
      </App>
    </ConfigProvider>
  );
};

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      // Disabled - using theme.colorBgLayout instead
      disable: true,
    },
    options: {
      storySort: {
        order: ['App', '*'],
      },
    },
    viewMode: 'story',
  },
  decorators: [withAntdTheme],
  globalTypes: {
    theme: {
      name: 'Theme',
      description: 'Global theme for components',
      defaultValue: 'dark',
      toolbar: {
        icon: 'circlehollow',
        items: [
          { value: 'light', title: 'Light', icon: 'sun' },
          { value: 'dark', title: 'Dark', icon: 'moon' },
        ],
        showName: true,
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: {
    theme: 'dark',
  },
};

export default preview;
