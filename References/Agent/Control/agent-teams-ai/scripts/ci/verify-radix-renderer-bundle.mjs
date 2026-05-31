import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const assetsDir = join(process.cwd(), 'out', 'renderer', 'assets');
const rendererBundles = readdirSync(assetsDir)
  .filter((entry) => entry.endsWith('.js'))
  .sort();

if (rendererBundles.length === 0) {
  console.error(
    [
      'No renderer JavaScript bundles found under out/renderer/assets.',
      'Run `pnpm build` before packaging production artifacts.',
    ].join('\n')
  );
  process.exit(1);
}

const requiredMarkers = [
  'nodeCleanupGenerationRef',
  'syncNode(null)',
  'useGuardedNodeSetter',
  'setTriggerRef',
  'setValueNodeRef',
  'setContentRef',
  'setViewportRef',
  'setSelectedItemRef',
  'setSelectedItemTextRef',
  'setItemTextNodeRef',
  'setControlRef',
  'setBubbleInputRef',
];

const forbiddenSnippets = [
  '(node) => setContent(node)',
  '(node2) => setNode(node2)',
  '(node) => setItemTextNode(node)',
  'onContentChange: setContent,',
  'onTriggerChange: setTrigger,',
  'onValueNodeChange: setValueNode,',
  'onViewportChange: setViewport,',
  'ref: setContentWrapper,',
  'setSelectedItem(node);',
  'setSelectedItemText(node);',
  'useComposedRefs(forwardedRef, setControl)',
  'useComposedRefs(forwardedRef, setBubbleInput)',
  'useComposedRefs)(forwardedRef, setControl)',
  'useComposedRefs)(forwardedRef, setBubbleInput)',
];

const failures = [];
const bundleSources = new Map();
let combinedSource = '';

for (const bundleName of rendererBundles) {
  const bundlePath = join(assetsDir, bundleName);
  const source = readFileSync(bundlePath, 'utf8');
  bundleSources.set(bundleName, source);
  combinedSource += source;
}

const missingMarkers = requiredMarkers.filter((marker) => !combinedSource.includes(marker));
if (missingMarkers.length > 0) {
  failures.push(`renderer bundles: missing markers: ${missingMarkers.join(', ')}`);
}

for (const [bundleName, source] of bundleSources) {
  const presentForbiddenSnippets = forbiddenSnippets.filter((snippet) => source.includes(snippet));

  if (presentForbiddenSnippets.length > 0) {
    failures.push(
      `${bundleName}: forbidden snippets still present: ${presentForbiddenSnippets.join(', ')}`
    );
  }
}

if (failures.length > 0) {
  console.error(
    [
      'Renderer bundle was built without the complete Radix React 19 ref-cleanup guards.',
      '',
      ...failures,
    ].join('\n')
  );
  process.exit(1);
}
