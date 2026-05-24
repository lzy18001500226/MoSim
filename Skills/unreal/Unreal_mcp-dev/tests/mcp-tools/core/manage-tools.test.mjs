#!/usr/bin/env node
/**
 * manage_tools Tool Integration Tests
 * Covers all 8 actions with proper setup/teardown sequencing.
 */

import { runToolTests } from '../../test-runner.mjs';

const TEST_FOLDER = '/Game/MCPTest/ManageTools';

const testCases = [
  // === SETUP ===
  { scenario: 'Setup: create test folder', toolName: 'manage_asset', arguments: { action: 'create_folder', path: TEST_FOLDER }, expected: 'success|already exists' },

  // === INFO ===
  { scenario: 'INFO: list_tools', toolName: 'manage_tools', arguments: {"action": "list_tools"}, expected: 'success' },
  { scenario: 'INFO: list_categories', toolName: 'manage_tools', arguments: {"action": "list_categories"}, expected: 'success' },
  // === TOGGLE ===
  { scenario: 'TOGGLE: enable_tools', toolName: 'manage_tools', arguments: { action: 'enable_tools', tools: ['system_control'] }, expected: 'success' },
  { scenario: 'TOGGLE: disable_tools', toolName: 'manage_tools', arguments: { action: 'disable_tools', tools: ['system_control'] }, expected: 'success' },
  { scenario: 'TOGGLE: enable_category', toolName: 'manage_tools', arguments: { action: 'enable_category', category: 'gameplay' }, expected: 'success' },
  { scenario: 'TOGGLE: disable_category', toolName: 'manage_tools', arguments: { action: 'disable_category', category: 'gameplay' }, expected: 'success' },
  // === INFO ===
  { scenario: 'INFO: get_status', toolName: 'manage_tools', arguments: {"action": "get_status"}, expected: 'success' },
  // === ACTION ===
  { scenario: 'ACTION: reset', toolName: 'manage_tools', arguments: {"action": "reset"}, expected: 'success' },

  // === CLEANUP ===
  { scenario: 'Cleanup: delete test folder', toolName: 'manage_asset', arguments: { action: 'delete', path: TEST_FOLDER, force: true }, expected: 'success|not found' },
];

runToolTests('manage-tools', testCases);
