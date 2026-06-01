import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

const root = process.cwd();
const skill = readFileSync(join(root, 'skills', 'best-practice-research', 'SKILL.md'), 'utf-8');
const pluginSkill = readFileSync(join(root, 'plugins', 'oh-my-codex', 'skills', 'best-practice-research', 'SKILL.md'), 'utf-8');

describe('best-practice-research skill contract', () => {
  it('defines a bounded wrapper without replacing researcher', () => {
    assert.match(skill, /^---\nname: best-practice-research/m);
    assert.match(skill, /workflow wrapper/i);
    assert.match(skill, /not a new research authority/i);
    assert.match(skill, /does not replace `researcher`/i);
  });

  it('preserves specialist routing and source quality boundaries', () => {
    assert.match(skill, /use `explore` first/i);
    assert.match(skill, /Use `researcher` for official\/upstream docs/i);
    assert.match(skill, /Use `dependency-expert` only/i);
    assert.match(skill, /Prefer official documentation, upstream source/i);
    assert.match(skill, /State date\/version context/i);
    assert.match(skill, /third-party summaries as supplemental/i);
  });

  it('keeps plugin mirror in sync with canonical skill', () => {
    assert.equal(pluginSkill, skill);
  });
});
