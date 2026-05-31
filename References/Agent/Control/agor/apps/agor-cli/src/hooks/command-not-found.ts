/**
 * Hook for handling command not found errors gracefully
 */
import type { Hook } from '@oclif/core';
import chalk from 'chalk';

const hook: Hook<'command_not_found'> = async ({ id }) => {
  console.log('');
  console.log(chalk.red('✗ Command not found:'), chalk.cyan(id));
  console.log('');
  console.log(`Run ${chalk.cyan('agor --help')} to see available commands.`);
  console.log('');
  process.exit(1);
};

export default hook;
