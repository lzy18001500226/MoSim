/**
 * `agor daemon` - Daemon lifecycle management overview
 */

import { Command } from '@oclif/core';
import chalk from 'chalk';
import { isInstalledPackage } from '../../lib/context.js';

export default class DaemonIndex extends Command {
  static description = 'Manage the Agor daemon lifecycle';

  static examples = [
    '<%= config.bin %> <%= command.id %> start',
    '<%= config.bin %> <%= command.id %> stop',
    '<%= config.bin %> <%= command.id %> status',
  ];

  async run(): Promise<void> {
    // Check if running in production mode
    if (!isInstalledPackage()) {
      this.log(chalk.yellow('⚠ Daemon lifecycle commands only work in production mode.'));
      this.log('');
      this.log(chalk.bold('In development, manage the daemon manually:'));
      this.log('');
      this.log(chalk.cyan('  Start daemon:'));
      this.log('    cd apps/agor-daemon && pnpm dev');
      this.log('');
      this.log(chalk.cyan('  Stop daemon:'));
      this.log('    Use Ctrl+C in the daemon terminal');
      this.log('');
      this.exit(1);
    }

    this.log(chalk.bold('\nDaemon Lifecycle Management'));
    this.log(chalk.dim('─'.repeat(50)));
    this.log('');
    this.log(chalk.bold('Available Commands:'));
    this.log('');
    this.log(`  ${chalk.cyan('agor daemon start')}    Start daemon in background`);
    this.log(`  ${chalk.cyan('agor daemon stop')}     Stop daemon gracefully`);
    this.log(`  ${chalk.cyan('agor daemon restart')}  Restart daemon`);
    this.log(`  ${chalk.cyan('agor daemon status')}   Check daemon status`);
    this.log(`  ${chalk.cyan('agor daemon logs')}     View daemon logs`);
    this.log('');
    this.log(chalk.bold('Examples:'));
    this.log('');
    this.log('  # Start daemon');
    this.log('  $ agor daemon start');
    this.log('');
    this.log('  # Check status');
    this.log('  $ agor daemon status');
    this.log('');
    this.log('  # View recent logs');
    this.log('  $ agor daemon logs');
    this.log('');
    this.log('  # View last 100 log lines');
    this.log('  $ agor daemon logs --lines 100');
    this.log('');
  }
}
