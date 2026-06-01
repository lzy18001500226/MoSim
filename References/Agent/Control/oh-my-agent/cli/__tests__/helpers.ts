import type { Mock } from "vitest";

export function assertDefined<T>(
  value: T,
  label: string,
): asserts value is NonNullable<T> {
  if (value === undefined || value === null) {
    throw new Error(`${label} expected to be defined`);
  }
}

export function getCall<T extends unknown[]>(
  mock: Mock<(...args: T) => unknown>,
  index: number,
): T {
  const call = mock.mock.calls[index];
  if (!call) {
    throw new Error(`expected mock call at index ${index}`);
  }
  return call;
}

export function firstCall<T extends unknown[]>(
  mock: Mock<(...args: T) => unknown>,
): T {
  return getCall(mock, 0);
}

export function lastCall<T extends unknown[]>(
  mock: Mock<(...args: T) => unknown>,
): T {
  const calls = mock.mock.calls;
  const call = calls[calls.length - 1];
  if (!call) throw new Error("expected at least one mock call");
  return call;
}
