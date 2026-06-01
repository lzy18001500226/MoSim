import * as fs from "node:fs";

/**
 * Read and parse a JSON file. Returns `null` when the file is absent,
 * unreadable, or unparseable. Never throws.
 *
 * The return type is `unknown` because JSON content is opaque from the
 * caller's perspective — validate the shape at the call site (or pass a
 * `validator` to narrow inline).
 *
 * @example
 *   const v = safeReadJson(path);
 *   if (v && typeof v === "object" && "version" in v) { ... }
 *
 * @example with validator
 *   const v = safeReadJson<{version: string}>(path, (x): x is {version: string} =>
 *     !!x && typeof x === "object" && typeof (x as any).version === "string",
 *   );
 */
export function safeReadJson<T = unknown>(
  filePath: string,
  validator?: (value: unknown) => value is T,
): T | null {
  if (!fs.existsSync(filePath)) return null;
  let raw: string;
  try {
    raw = fs.readFileSync(filePath, "utf-8");
  } catch {
    return null;
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return null;
  }
  if (validator && !validator(parsed)) return null;
  return parsed as T;
}
