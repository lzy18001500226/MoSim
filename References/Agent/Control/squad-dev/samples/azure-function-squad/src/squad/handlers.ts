/**
 * Agent Work Handlers — Content Review Squad
 *
 * Mock handler implementations for each review agent.
 * In production, these would call into the Squad runtime to
 * dispatch work to actual LLM-backed agents. Here we simulate
 * the review output to demonstrate the integration pattern.
 */

// ── Types ────────────────────────────────────────────────────────────

export interface ReviewFinding {
  severity: 'info' | 'suggestion' | 'warning' | 'error';
  location?: string;
  message: string;
}

export interface AgentReview {
  agent: string;
  role: string;
  score: number;
  findings: ReviewFinding[];
  summary: string;
}

export interface SquadReviewResult {
  prompt: string;
  timestamp: string;
  reviews: AgentReview[];
  overallScore: number;
  consensus: string;
}

// ── Tone Review Handler ──────────────────────────────────────────────

function reviewTone(content: string): AgentReview {
  const wordCount = content.split(/\s+/).length;
  const hasQuestions = /\?/.test(content);
  const hasExclamations = /!/.test(content);
  const hasCodeBlocks = /```/.test(content);

  const findings: ReviewFinding[] = [];

  if (wordCount < 50) {
    findings.push({
      severity: 'warning',
      message: `Content is short (${wordCount} words). Consider expanding for better audience engagement.`,
    });
  }

  if (hasExclamations && !hasQuestions) {
    findings.push({
      severity: 'suggestion',
      message: 'Content uses exclamations but no questions. Adding rhetorical questions can improve reader engagement.',
    });
  }

  if (hasCodeBlocks) {
    findings.push({
      severity: 'info',
      message: 'Code blocks detected. Ensure surrounding prose provides adequate context for non-technical readers.',
    });
  }

  if (!hasExclamations && !hasQuestions) {
    findings.push({
      severity: 'suggestion',
      message: 'Tone is neutral/flat. Consider adding variety to maintain reader interest.',
    });
  }

  const score = Math.min(10, 6 + findings.filter(f => f.severity === 'info').length
    - findings.filter(f => f.severity === 'warning').length);

  return {
    agent: 'tone-reviewer',
    role: 'Tone & Voice Analyst',
    score: Math.max(1, score),
    findings,
    summary: `Analyzed ${wordCount} words. Tone is ${hasQuestions ? 'engaging' : 'informational'}, ${hasExclamations ? 'energetic' : 'measured'}.`,
  };
}

// ── Technical Review Handler ─────────────────────────────────────────

function reviewTechnical(content: string): AgentReview {
  const hasCodeBlocks = /```[\s\S]*?```/.test(content);
  const hasUrls = /https?:\/\/\S+/.test(content);
  const hasVersionNumbers = /v?\d+\.\d+(\.\d+)?/.test(content);
  const hasTodoComments = /TODO|FIXME|HACK/i.test(content);

  const findings: ReviewFinding[] = [];

  if (hasCodeBlocks) {
    findings.push({
      severity: 'info',
      message: 'Code blocks present. Verify snippets compile and match described behavior.',
    });
  }

  if (hasUrls) {
    findings.push({
      severity: 'suggestion',
      message: 'External URLs found. Verify links are accessible and point to current documentation.',
    });
  }

  if (hasVersionNumbers) {
    findings.push({
      severity: 'suggestion',
      message: 'Version numbers referenced. Confirm they match the latest stable release.',
    });
  }

  if (hasTodoComments) {
    findings.push({
      severity: 'warning',
      message: 'TODO/FIXME markers found in content. These should be resolved before publishing.',
    });
  }

  if (!hasCodeBlocks && content.toLowerCase().includes('code')) {
    findings.push({
      severity: 'warning',
      message: 'Content mentions code but includes no code blocks. Consider adding examples.',
    });
  }

  const score = Math.min(10, 8
    - findings.filter(f => f.severity === 'warning').length
    + findings.filter(f => f.severity === 'info').length);

  return {
    agent: 'technical-reviewer',
    role: 'Technical Accuracy Checker',
    score: Math.max(1, score),
    findings,
    summary: `Technical review complete. ${hasCodeBlocks ? 'Code blocks verified.' : 'No code blocks found.'} ${hasUrls ? 'URLs need validation.' : ''} ${hasVersionNumbers ? 'Version refs need confirmation.' : ''}`.trim(),
  };
}

// ── Copy Edit Handler ────────────────────────────────────────────────

function reviewCopy(content: string): AgentReview {
  const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const avgSentenceLength = sentences.length > 0
    ? sentences.reduce((sum, s) => sum + s.split(/\s+/).length, 0) / sentences.length
    : 0;
  const hasPassiveVoice = /\b(is|are|was|were|be|been|being)\s+\w+ed\b/i.test(content);
  const hasRepeatedWords = /\b(\w+)\s+\1\b/i.test(content);
  const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim().length > 0);

  const findings: ReviewFinding[] = [];

  if (avgSentenceLength > 25) {
    findings.push({
      severity: 'warning',
      message: `Average sentence length is ${Math.round(avgSentenceLength)} words. Aim for 15–20 for readability.`,
    });
  }

  if (hasPassiveVoice) {
    findings.push({
      severity: 'suggestion',
      message: 'Passive voice detected. Consider rewriting in active voice for clarity.',
    });
  }

  if (hasRepeatedWords) {
    findings.push({
      severity: 'suggestion',
      message: 'Repeated adjacent words detected. Check for accidental duplications.',
    });
  }

  if (paragraphs.length === 1 && sentences.length > 5) {
    findings.push({
      severity: 'suggestion',
      message: 'Content is a single block of text. Break into paragraphs for scannability.',
    });
  }

  if (sentences.length < 3) {
    findings.push({
      severity: 'info',
      message: 'Very short content. Copy review is limited with minimal text.',
    });
  }

  const score = Math.min(10, 8
    - findings.filter(f => f.severity === 'warning').length * 2
    - findings.filter(f => f.severity === 'suggestion').length * 0.5);

  return {
    agent: 'copy-editor',
    role: 'Copy Editor',
    score: Math.max(1, Math.round(score)),
    findings,
    summary: `Reviewed ${sentences.length} sentences across ${paragraphs.length} paragraph(s). Avg sentence length: ${Math.round(avgSentenceLength)} words.`,
  };
}

// ── Orchestrator ─────────────────────────────────────────────────────

export function runContentReview(prompt: string): SquadReviewResult {
  const reviews = [
    reviewTone(prompt),
    reviewTechnical(prompt),
    reviewCopy(prompt),
  ];

  const overallScore = Math.round(
    reviews.reduce((sum, r) => sum + r.score, 0) / reviews.length,
  );

  const totalFindings = reviews.reduce((sum, r) => sum + r.findings.length, 0);
  const warnings = reviews.reduce(
    (sum, r) => sum + r.findings.filter(f => f.severity === 'warning').length, 0,
  );

  let consensus: string;
  if (overallScore >= 8) {
    consensus = '✅ Content is publication-ready with minor suggestions.';
  } else if (overallScore >= 5) {
    consensus = `⚠️ Content needs attention. ${warnings} warning(s) and ${totalFindings} total finding(s) across all reviewers.`;
  } else {
    consensus = `❌ Content requires significant revision. ${warnings} warning(s) flagged by the review squad.`;
  }

  return {
    prompt: prompt.slice(0, 200) + (prompt.length > 200 ? '...' : ''),
    timestamp: new Date().toISOString(),
    reviews,
    overallScore,
    consensus,
  };
}
