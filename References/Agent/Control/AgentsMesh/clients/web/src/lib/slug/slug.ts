import { isReservedSlug } from "./reserved";

export type SlugError =
  | "empty"
  | "too_short"
  | "too_long"
  | "invalid_format"
  | "reserved";

export const SLUG_MIN_LEN = 2;
export const SLUG_MAX_LEN = 100;

const SLUG_PATTERN = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const NON_ALNUM = /[^a-z0-9]+/g;
const TRIM_HYPHENS = /^-+|-+$/g;

export function sanitizeSlug(raw: string): string {
  if (!raw) return "";
  let s = raw.toLowerCase().trim();
  s = s.replace(NON_ALNUM, "-");
  s = s.replace(TRIM_HYPHENS, "");
  if (s.length > SLUG_MAX_LEN) {
    s = s.substring(0, SLUG_MAX_LEN).replace(/-+$/, "");
  }
  return s;
}

export function validateSlug(s: string): SlugError | null {
  if (!s) return "empty";
  if (s.length < SLUG_MIN_LEN) return "too_short";
  if (s.length > SLUG_MAX_LEN) return "too_long";
  if (!SLUG_PATTERN.test(s)) return "invalid_format";
  if (isReservedSlug(s)) return "reserved";
  return null;
}
