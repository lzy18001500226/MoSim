import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

// Spacebot GitHub repository
export const gitConfig = {
  user: 'spacedriveapp',
  repo: 'spacebot',
  branch: 'main',
};

export function baseOptions(): BaseLayoutProps {
  return {
    nav: {
      title: 'Spacebot',
    },
    githubUrl: `https://github.com/${gitConfig.user}/${gitConfig.repo}`,
  };
}
