/**
 * React ErrorBoundary for the Ink shell.
 *
 * Catches unhandled errors in the component tree and shows a friendly
 * message instead of a raw stack trace. Logs the error to stderr for debugging.
 */

import React from 'react';
import { Box, Text } from 'ink';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error('[squad] Unhandled UI error:', error);
    if (info.componentStack) {
      console.error('[squad] Component stack:', info.componentStack);
    }
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <Box flexDirection="column" padding={1}>
          <Text color="red" bold>Something went wrong. Press Ctrl+C to exit.</Text>
          <Text dimColor>The error has been logged to stderr for debugging.</Text>
        </Box>
      );
    }
    return this.props.children;
  }
}
