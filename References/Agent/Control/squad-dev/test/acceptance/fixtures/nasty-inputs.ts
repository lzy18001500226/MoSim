/**
 * Nasty input corpus for adversarial/fuzz-like testing.
 * Each entry has a label and the hostile string.
 * Used by hostile QA scenarios to probe CLI resilience.
 */

export interface NastyInput {
  label: string;
  value: string;
}

export const NASTY_INPUTS: NastyInput[] = [
  // Empty / whitespace
  { label: 'empty-string', value: '' },
  { label: 'single-space', value: ' ' },
  { label: 'tabs-only', value: '\t\t\t' },
  { label: 'newlines-only', value: '\n\n\n' },
  { label: 'crlf-only', value: '\r\n\r\n' },
  { label: 'mixed-whitespace', value: ' \t\n\r ' },

  // Control characters
  { label: 'null-byte', value: '\x00' },
  { label: 'bell', value: '\x07' },
  { label: 'backspace', value: '\x08\x08\x08' },
  { label: 'escape', value: '\x1B' },
  { label: 'ansi-escape-sequence', value: '\x1B[31mRED\x1B[0m' },
  { label: 'form-feed', value: '\x0C' },
  { label: 'delete-char', value: '\x7F' },
  { label: 'control-c', value: '\x03' },
  { label: 'control-d', value: '\x04' },
  { label: 'control-z', value: '\x1A' },

  // Unicode edge cases
  { label: 'emoji-simple', value: '🚀💥🔥' },
  { label: 'emoji-zwj', value: '👨‍👩‍👧‍👦' }, // family ZWJ sequence
  { label: 'emoji-flag', value: '🇺🇸🇬🇧🇯🇵' },
  { label: 'cjk-chinese', value: '你好世界测试' },
  { label: 'cjk-japanese', value: 'テスト日本語' },
  { label: 'cjk-korean', value: '테스트한국어' },
  { label: 'rtl-arabic', value: 'مرحبا بالعالم' },
  { label: 'rtl-hebrew', value: 'שלום עולם' },
  { label: 'zero-width-space', value: 'a\u200Bb\u200Bc' },
  { label: 'zero-width-joiner', value: 'a\u200Db\u200Dc' },
  { label: 'zero-width-non-joiner', value: 'a\u200Cb\u200Cc' },
  { label: 'bidi-override', value: '\u202Ereversed\u202C' },
  { label: 'combining-diacriticals', value: 'Z̤͔ͧ̑̓ä͖̭̈̇lͮ̒ͫǧ̗͚̌ͥõ̶̡̖̖' },
  { label: 'surrogate-pair-emoji', value: '𝕳𝖊𝖑𝖑𝖔' },
  { label: 'musical-symbols', value: '𝄞𝄢' },
  { label: 'thai-script', value: 'สวัสดีครับ' },
  { label: 'devanagari', value: 'नमस्ते' },

  // Injection-like strings
  { label: 'sql-injection', value: "'; DROP TABLE users; --" },
  { label: 'xss-script', value: '<script>alert("xss")</script>' },
  { label: 'shell-injection-semicolon', value: '; rm -rf /' },
  { label: 'shell-injection-backtick', value: '`rm -rf /`' },
  { label: 'shell-injection-dollar', value: '$(rm -rf /)' },
  { label: 'shell-injection-pipe', value: '| cat /etc/passwd' },
  { label: 'path-traversal', value: '../../../etc/passwd' },
  { label: 'windows-path-traversal', value: '..\\..\\..\\windows\\system32' },

  // Extremely long strings
  { label: '1kb-string', value: 'A'.repeat(1024) },
  { label: '10kb-string', value: 'B'.repeat(10240) },
  { label: '100kb-string', value: 'C'.repeat(102400) },
  { label: 'long-with-newlines', value: ('line\n').repeat(1000) },

  // Special format strings
  { label: 'percent-s', value: '%s%s%s%s%s%s%s%s%s%s' },
  { label: 'percent-n', value: '%n%n%n%n' },
  { label: 'curly-braces', value: '{{{{{{{{{{}}}}}}}}}}' },
  { label: 'template-literal', value: '${process.exit(1)}' },
  { label: 'backtick-template', value: '`${process.exit(1)}`' },

  // JSON edge cases
  { label: 'json-null', value: 'null' },
  { label: 'json-empty-object', value: '{}' },
  { label: 'json-empty-array', value: '[]' },
  { label: 'json-nested-deep', value: '{"a":'.repeat(50) + '"x"' + '}'.repeat(50) },
  { label: 'json-huge-number', value: '99999999999999999999999999999999999999' },

  // Filename-hostile
  { label: 'dot-dot', value: '..' },
  { label: 'slash', value: '/' },
  { label: 'backslash', value: '\\' },
  { label: 'nul-device', value: 'NUL' },
  { label: 'con-device', value: 'CON' },
  { label: 'prn-device', value: 'PRN' },
  { label: 'colon', value: ':' },
  { label: 'asterisk', value: '*' },
  { label: 'question-mark', value: '?' },
  { label: 'angle-brackets', value: '<>' },
  { label: 'pipe-char', value: '|' },
  { label: 'double-quotes', value: '"quoted"' },
];

/**
 * Subset of inputs safe to use as CLI arguments (no null bytes, not too long).
 */
export const CLI_SAFE_NASTY_INPUTS = NASTY_INPUTS.filter(
  i => !i.value.includes('\x00') && i.value.length < 2048
);

/**
 * Inputs that specifically target unicode rendering.
 */
export const UNICODE_NASTY_INPUTS = NASTY_INPUTS.filter(
  i => i.label.startsWith('emoji') ||
       i.label.startsWith('cjk') ||
       i.label.startsWith('rtl') ||
       i.label.startsWith('zero-width') ||
       i.label.startsWith('bidi') ||
       i.label.startsWith('combining') ||
       i.label.startsWith('surrogate') ||
       i.label.startsWith('thai') ||
       i.label.startsWith('devanagari')
);
