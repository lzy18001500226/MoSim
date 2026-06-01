import { HeaderGenerator, type HeaderGeneratorOptions } from "header-generator";

/**
 * Generates realistic browser-like HTTP headers to help avoid bot detection.
 * Uses the `header-generator` library for header generation.
 */
export class FingerprintGenerator {
  private headerGenerator: HeaderGenerator;

  /**
   * Creates an instance of FingerprintGenerator.
   * @param options Optional configuration for the header generator.
   */
  constructor(options?: Partial<HeaderGeneratorOptions>) {
    // Default options for a broad range of realistic headers
    const defaultOptions: Partial<HeaderGeneratorOptions> = {
      browsers: [{ name: "chrome", minVersion: 100 }, "firefox", "safari"],
      devices: ["desktop", "mobile"],
      operatingSystems: ["windows", "linux", "macos", "android", "ios"],
      locales: ["en-US", "en"],
      httpVersion: "2",
    };

    this.headerGenerator = new HeaderGenerator({
      ...defaultOptions,
      ...options,
    });
  }

  /**
   * Generates a set of realistic HTTP headers.
   * @returns A set of realistic HTTP headers.
   */
  generateHeaders(): Record<string, string> {
    return this.headerGenerator.getHeaders();
  }
}
