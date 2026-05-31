/**
 * `agor daemon stop` - Stop daemon gracefully
 */

import { Command } from '@oclif/core';
import chalk from 'chalk';
import { isInstalledPackage } from '../../lib/context.js';
import { stopDaemon } from '../../lib/daemon-manager.js';

export default class DaemonStop extends Command {
  static description = 'Stop daemon gracefully';

  static examples = ['<%= config.bin %> <%= command.id %>'];

  async run(): Promise<void> {
    // Check if running in production mode
    if (!isInstalledPackage()) {
      this.log(chalk.red('✗ Daemon lifecycle commands only work in production mode.'));
      this.log('');
      this.log(chalk.bold('In development, stop the daemon with:'));
      this.log(`  ${chalk.cyan('Use Ctrl+C in the daemon terminal')}`);
      this.log('');
      this.exit(1);
    }

    try {
      const stopped = stopDaemon();

      if (!stopped) {
        this.log(chalk.yellow('⚠ Daemon is not running'));
        this.log('');
        this.exit(0);
      }

      this.log(chalk.green('✓ Daemon stopped successfully'));
      this.log('');
    } catch (error) {
      this.log(chalk.red('✗ Failed to stop daemon'));
      this.log('');
      this.log(`Error: ${(error as Error).message}`);
      this.log('');
      this.exit(1);
    }
  }
}
