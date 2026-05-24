import { describe, expect, it } from 'vitest';
import { ErrorHandler } from './error-handler.js';

describe('ErrorHandler', () => {
  it('classifies timed-out requests as timeout errors', () => {
    const response = ErrorHandler.createErrorResponse(
      new Error('Request 123 timed out after 1000ms'),
      'manage_asset'
    );

    expect(response.error).toBe('Operation timed out. Unreal Engine may be busy or unresponsive.');
    expect(response.message).toContain('Operation timed out');
    expect(response.retriable).toBe(true);
  });
});
