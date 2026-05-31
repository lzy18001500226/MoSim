#!/usr/bin/env node
/**
 * Export registry data as a flat JSON list.
 * Usage:
 *   node scripts/export-json.js --pretty --output dist/registry.json
 *   node scripts/export-json.js --pretty > dist/registry.json
 */

const fs = require('fs');
const path = require('path');
const { readYamlDir, slugify } = require('./utils/yaml');
const { validateEntry, formatValidationErrors } = require('./utils/validation');

const CATEGORIES = ['plugins', 'themes', 'agents', 'projects', 'resources'];

function parseArgs(args) {
  const outputFlagIndex = args.findIndex((arg) => arg === '--output');
  const outputPath = outputFlagIndex !== -1 && args[outputFlagIndex + 1]
    ? args[outputFlagIndex + 1]
    : null;
  const pretty = args.includes('--pretty');
  return { outputPath, pretty };
}

function buildProductId(entry) {
  if (entry._fileName) {
    return entry._fileName;
  }
  if (entry.name) {
    return slugify(entry.name);
  }
  return '';
}

function sanitizeArray(value, fallback) {
  if (Array.isArray(value) && value.length > 0) {
    return value;
  }
  return fallback;
}

function mapEntry(entry, category) {
  const productId = buildProductId(entry);
  if (!productId) {
    return null;
  }

  const output = {
    productId,
    type: category,
    displayName: entry.name,
    repoUrl: entry.repo,
    tagline: entry.tagline,
    description: entry.description,
    scope: sanitizeArray(entry.scope, ['global']),
    tags: sanitizeArray(entry.tags, []),
    homepageUrl: entry.homepage,
    installation: entry.installation,
    minVersion: entry.min_version
  };

  return output;
}

function stripUndefined(data) {
  const cleaned = {};
  for (const [key, value] of Object.entries(data)) {
    if (value !== undefined) {
      cleaned[key] = value;
    }
  }
  return cleaned;
}

async function loadEntries() {
  const results = [];
  const errors = [];

  for (const category of CATEGORIES) {
    const categoryPath = path.join(__dirname, '../data', category);
    let entries = [];

    try {
      entries = await readYamlDir(categoryPath);
    } catch (err) {
      if (err.code === 'ENOENT') {
        continue;
      }
      throw err;
    }

    for (const entry of entries) {
      const result = validateEntry(entry, entry._filePath || categoryPath);
      if (!result.valid) {
        errors.push(formatValidationErrors(result));
        continue;
      }

      const mapped = mapEntry(entry, category);
      if (mapped) {
        results.push(stripUndefined(mapped));
      }
    }
  }

  return { results, errors };
}

async function main() {
  const { outputPath, pretty } = parseArgs(process.argv.slice(2));
  const writeToStdout = !outputPath;
  const log = (...args) => {
    if (writeToStdout) {
      console.error(...args);
    } else {
      console.log(...args);
    }
  };

  const { results, errors } = await loadEntries();

  results.sort((a, b) => {
    const typeCompare = a.type.localeCompare(b.type);
    if (typeCompare !== 0) {
      return typeCompare;
    }
    return a.productId.localeCompare(b.productId);
  });

  if (errors.length > 0) {
    for (const error of errors) {
      log(error);
    }
    log(`\n⚠️  Skipped ${errors.length} invalid entr${errors.length === 1 ? 'y' : 'ies'}.`);
  }

  const json = JSON.stringify(results, null, pretty ? 2 : 0);

  if (outputPath) {
    const outputDir = path.dirname(outputPath);
    if (outputDir && outputDir !== '.') {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    fs.writeFileSync(outputPath, json);
    log(`Saved ${results.length} entries to ${outputPath}`);
  } else {
    process.stdout.write(json);
  }

  if (errors.length > 0) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Export failed:', err.message);
  process.exit(1);
});
