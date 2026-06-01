import { logger } from "../../utils/logger";
import type { ContentProcessorMiddleware, MiddlewareContext } from "./types";

/**
 * Middleware to extract links (href attributes from <a> tags) from HTML content using Cheerio.
 * It expects the Cheerio API object to be available in `context.dom`.
 * This should run *after* parsing but *before* conversion to Markdown.
 */
export class HtmlLinkExtractorMiddleware implements ContentProcessorMiddleware {
  /**
   * Processes the context to extract links from the sanitized HTML body.
   * @param context The current middleware context.
   * @param next Function to call the next middleware.
   */
  async process(context: MiddlewareContext, next: () => Promise<void>): Promise<void> {
    // Check if we have a Cheerio object from a previous step
    const $ = context.dom;
    if (!$) {
      logger.warn(
        `⏭️ Skipping ${this.constructor.name}: context.dom is missing. Ensure HtmlCheerioParserMiddleware runs before this.`,
      );
      await next();
      return;
    }

    try {
      // Determine effective document base (first <base href> if present)
      let docBase = context.source;
      try {
        const baseEl = $("base[href]").first();
        const rawBase = baseEl.attr("href");
        if (rawBase && rawBase.trim() !== "") {
          try {
            const trimmed = rawBase.trim();
            // Attempt to resolve candidate base against the document source.
            const candidate = new URL(trimmed, context.source);
            // Heuristic validation:
            // Accept if:
            //  - Starts with a valid scheme (e.g. https:, data:, etc.) OR
            //  - Protocol-relative (//...) OR
            //  - Root-relative (/...) OR
            //  - Dot-relative (./ or ../...) OR
            //  - Otherwise a plain relative path segment WITHOUT a suspicious leading colon
            //
            // Reject (fallback to original page URL) if the first character is a colon or
            // there is a colon before any slash that does NOT form a valid scheme.
            const hasScheme = /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(trimmed);
            const protocolRelative = trimmed.startsWith("//");
            const firstSlash = trimmed.indexOf("/");
            const firstColon = trimmed.indexOf(":");
            const colonBeforeSlash =
              firstColon !== -1 && (firstSlash === -1 || firstColon < firstSlash);
            const suspiciousColon = colonBeforeSlash && !hasScheme && !protocolRelative;
            if (suspiciousColon || trimmed.startsWith(":")) {
              logger.debug(
                `Ignoring suspicious <base href> value (colon misuse): ${rawBase}`,
              );
            } else {
              // Accept candidate (valid scheme, protocol/root/dot relative, or plain relative segment)
              docBase = candidate.href;
            }
          } catch {
            logger.debug(`Ignoring invalid <base href> value: ${rawBase}`);
          }
        }
      } catch {
        // Ignore base parsing errors
      }

      const linkElements = $("a[href]");
      logger.debug(
        `Found ${linkElements.length} potential links in ${context.source} (base=${docBase})`,
      );

      const extractedLinks: string[] = [];
      linkElements.each((_index, element) => {
        const href = $(element).attr("href");
        if (href && href.trim() !== "") {
          try {
            const urlObj = new URL(href, docBase);
            if (!["http:", "https:", "file:"].includes(urlObj.protocol)) {
              logger.debug(`Ignoring link with invalid protocol: ${href}`);
              return;
            }
            extractedLinks.push(urlObj.href);
          } catch (_e) {
            logger.debug(`Ignoring invalid URL syntax: ${href}`);
          }
        }
      });

      context.links = [...new Set(extractedLinks)];
      logger.debug(
        `Extracted ${context.links.length} unique, valid links from ${context.source}`,
      );
    } catch (error) {
      logger.error(`❌ Error extracting links from ${context.source}: ${error}`);
      context.errors.push(
        new Error(
          `Failed to extract links from HTML: ${error instanceof Error ? error.message : String(error)}`,
        ),
      );
    }

    await next();
  }
}
