#!/usr/bin/env node
/**
 * Sync Agent Plugins from wshobson/agents
 *
 * This script fetches curated plugins from the wshobson/agents repository
 * and stores them in resources/agents/plugins/
 *
 * Usage: node scripts/sync-agents.js [--force]
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Configuration
const GITHUB_REPO = 'wshobson/agents';
const GITHUB_BRANCH = 'main';
const PLUGINS_DIR = path.join(__dirname, '..', 'resources', 'agents', 'plugins');
const CACHE_FILE = path.join(PLUGINS_DIR, '.sync-cache.json');

// Curated plugins to sync (based on relevance to Mysti's use cases)
const CURATED_PLUGINS = [
  'backend-development',
  'frontend-mobile-development',
  'code-review-ai',
  'debugging-toolkit',
  'tdd-workflows',
  'python-development',
  'javascript-typescript',
  'database-design',
  'cicd-automation',
  'code-documentation',
  'error-diagnostics',
  'code-refactoring',
  'llm-application-dev',
  'comprehensive-review',
  'unit-testing'
];

/**
 * Fetch JSON from GitHub API
 */
function fetchGitHub(urlPath) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.github.com',
      path: urlPath,
      headers: {
        'User-Agent': 'Mysti-Agent-Sync',
        'Accept': 'application/vnd.github.v3+json'
      }
    };

    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve(JSON.parse(data));
        } else if (res.statusCode === 403) {
          reject(new Error('GitHub API rate limit exceeded. Try again later or use a token.'));
        } else {
          reject(new Error(`GitHub API error: ${res.statusCode}`));
        }
      });
    }).on('error', reject);
  });
}

/**
 * Fetch raw file content from GitHub
 */
function fetchRawFile(filePath) {
  return new Promise((resolve, reject) => {
    const url = `https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/${filePath}`;

    https.get(url, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        https.get(res.headers.location, (redirectRes) => {
          let data = '';
          redirectRes.on('data', chunk => data += chunk);
          redirectRes.on('end', () => resolve(data));
        }).on('error', reject);
        return;
      }

      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve(data);
        } else {
          reject(new Error(`Failed to fetch ${filePath}: ${res.statusCode}`));
        }
      });
    }).on('error', reject);
  });
}

/**
 * Get directory contents from GitHub
 */
async function getDirectoryContents(dirPath) {
  try {
    return await fetchGitHub(`/repos/${GITHUB_REPO}/contents/${dirPath}?ref=${GITHUB_BRANCH}`);
  } catch (error) {
    console.warn(`Warning: Could not fetch ${dirPath}: ${error.message}`);
    return [];
  }
}

/**
 * Sync a single plugin
 */
async function syncPlugin(pluginName) {
  const pluginDir = path.join(PLUGINS_DIR, pluginName);

  // Create plugin directory
  if (!fs.existsSync(pluginDir)) {
    fs.mkdirSync(pluginDir, { recursive: true });
  }

  console.log(`  Syncing ${pluginName}...`);

  // Fetch agents
  const agentsDir = path.join(pluginDir, 'agents');
  if (!fs.existsSync(agentsDir)) {
    fs.mkdirSync(agentsDir, { recursive: true });
  }

  const agents = await getDirectoryContents(`plugins/${pluginName}/agents`);
  for (const agent of agents) {
    if (agent.name.endsWith('.md')) {
      try {
        const content = await fetchRawFile(`plugins/${pluginName}/agents/${agent.name}`);
        fs.writeFileSync(path.join(agentsDir, agent.name), content);
        console.log(`    ✓ agents/${agent.name}`);
      } catch (error) {
        console.warn(`    ✗ agents/${agent.name}: ${error.message}`);
      }
    }
  }

  // Fetch skills
  const skillsDir = path.join(pluginDir, 'skills');
  if (!fs.existsSync(skillsDir)) {
    fs.mkdirSync(skillsDir, { recursive: true });
  }

  const skills = await getDirectoryContents(`plugins/${pluginName}/skills`);
  for (const skill of skills) {
    if (skill.type === 'dir') {
      // Skills are in subdirectories with SKILL.md
      const skillSubDir = path.join(skillsDir, skill.name);
      if (!fs.existsSync(skillSubDir)) {
        fs.mkdirSync(skillSubDir, { recursive: true });
      }

      try {
        const content = await fetchRawFile(`plugins/${pluginName}/skills/${skill.name}/SKILL.md`);
        fs.writeFileSync(path.join(skillSubDir, 'SKILL.md'), content);
        console.log(`    ✓ skills/${skill.name}/SKILL.md`);
      } catch (error) {
        console.warn(`    ✗ skills/${skill.name}/SKILL.md: ${error.message}`);
      }
    }
  }

  return true;
}

/**
 * Load sync cache
 */
function loadCache() {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8'));
    }
  } catch (error) {
    console.warn('Warning: Could not load cache file');
  }
  return { lastSync: null, plugins: {} };
}

/**
 * Save sync cache
 */
function saveCache(cache) {
  fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
}

/**
 * Main sync function
 */
async function main() {
  const forceSync = process.argv.includes('--force');
  const cache = loadCache();

  // Check if we need to sync (once per day unless forced)
  const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
  if (!forceSync && cache.lastSync && new Date(cache.lastSync).getTime() > oneDayAgo) {
    console.log('Plugins are up to date. Use --force to sync anyway.');
    return;
  }

  console.log('Syncing agent plugins from wshobson/agents...\n');

  // Ensure plugins directory exists
  if (!fs.existsSync(PLUGINS_DIR)) {
    fs.mkdirSync(PLUGINS_DIR, { recursive: true });
  }

  let syncedCount = 0;
  let errorCount = 0;

  for (const pluginName of CURATED_PLUGINS) {
    try {
      await syncPlugin(pluginName);
      cache.plugins[pluginName] = { lastSync: new Date().toISOString() };
      syncedCount++;
    } catch (error) {
      console.error(`  ✗ Failed to sync ${pluginName}: ${error.message}`);
      errorCount++;
    }

    // Rate limiting - wait 100ms between plugins
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  cache.lastSync = new Date().toISOString();
  saveCache(cache);

  console.log(`\nSync complete: ${syncedCount} plugins synced, ${errorCount} errors`);
}

// Run
main().catch(error => {
  console.error('Sync failed:', error.message);
  process.exit(1);
});
