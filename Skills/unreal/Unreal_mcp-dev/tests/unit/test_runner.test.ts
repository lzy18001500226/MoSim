import { describe, expect, it } from 'vitest';
import { evaluateExpectation, summarizeResponseForReport } from '../test-runner.mjs';

describe('test runner response evaluation', () => {
  it('fails success-primary expectations when structuredContent.data reports failure', () => {
    const result = evaluateExpectation(
      { expected: 'success|error' },
      {
        isError: false,
        structuredContent: {
          success: true,
          message: 'Wrapped response',
          data: {
            success: false,
            error: 'TEXTURE_ERROR',
            message: 'Failed to create render target'
          }
        }
      }
    );

    expect(result.passed).toBe(false);
    expect(result.reason).toContain('TEXTURE_ERROR');
  });

  it('allows explicit idempotent failure alternatives for success-primary expectations', () => {
    const result = evaluateExpectation(
      { expected: 'success|already exists' },
      {
        isError: true,
        structuredContent: {
          success: false,
          error: 'ALREADY_EXISTS',
          message: 'Folder already exists'
        }
      }
    );

    expect(result.passed).toBe(true);
    expect(result.reason).toContain('already exists');
  });

  it('reports nested structuredContent.data.result failures as response failures', () => {
    const summary = summarizeResponseForReport({
      isError: false,
      structuredContent: {
        success: true,
        data: {
          result: {
            success: false,
            error: 'TEXTURE_ERROR',
            message: 'Failed to create render target'
          }
        }
      }
    });

    expect(summary.responseSuccess).toBe(false);
    expect(summary.responseIsError).toBe(true);
    expect(summary.responseError).toBe('TEXTURE_ERROR');
    expect(summary.responseMessage).toBe('Failed to create render target');
  });
});
