/**
 * Minimal Gherkin parser for .feature files.
 */

export interface GherkinStep {
  keyword: 'Given' | 'When' | 'Then' | 'And' | 'But';
  text: string;
}

export interface GherkinScenario {
  name: string;
  steps: GherkinStep[];
}

export interface GherkinFeature {
  name: string;
  scenarios: GherkinScenario[];
}

export function parseFeature(content: string): GherkinFeature {
  const lines = content.split('\n').map((line) => line.trim());
  const feature: GherkinFeature = { name: '', scenarios: [] };
  let currentScenario: GherkinScenario | null = null;
  let lastKeyword: GherkinStep['keyword'] = 'Given';

  for (const line of lines) {
    if (!line || line.startsWith('#')) continue;

    if (line.startsWith('Feature:')) {
      feature.name = line.substring(8).trim();
      continue;
    }

    if (line.startsWith('Scenario:')) {
      if (currentScenario) {
        feature.scenarios.push(currentScenario);
      }
      currentScenario = {
        name: line.substring(9).trim(),
        steps: [],
      };
      continue;
    }

    if (
      line.startsWith('Given ') ||
      line.startsWith('When ') ||
      line.startsWith('Then ') ||
      line.startsWith('And ') ||
      line.startsWith('But ')
    ) {
      const spaceIdx = line.indexOf(' ');
      const keyword = line.substring(0, spaceIdx) as GherkinStep['keyword'];
      const text = line.substring(spaceIdx + 1).trim();

      const effectiveKeyword =
        keyword === 'And' || keyword === 'But' ? lastKeyword : keyword;

      if (keyword !== 'And' && keyword !== 'But') {
        lastKeyword = effectiveKeyword;
      }

      if (currentScenario) {
        currentScenario.steps.push({ keyword: effectiveKeyword, text });
      }
    }
  }

  if (currentScenario) {
    feature.scenarios.push(currentScenario);
  }

  return feature;
}
