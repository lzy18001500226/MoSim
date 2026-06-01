export class PipelineError extends Error {
  constructor(
    message: string,
    public readonly cause?: Error,
  ) {
    super(message);
    this.name = this.constructor.name;
    if (cause?.stack) {
      this.stack = `${this.stack}\nCaused by: ${cause.stack}`;
    }
  }
}

export class PipelineStateError extends PipelineError {}

/**
 * Error indicating that an operation was cancelled.
 */
export class CancellationError extends PipelineError {
  constructor(message = "Operation cancelled") {
    super(message);
  }
}
