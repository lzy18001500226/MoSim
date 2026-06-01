/**
 * AgorAvatar - Standardized avatar component wrapping Ant Design's Avatar
 *
 * Provides consistent styling for user avatars throughout the application,
 * using colorPrimaryBg for the background to match the facepile in the navbar.
 *
 * Standard size: 40px (do not override unless absolutely necessary)
 */

import { Avatar, type AvatarProps, theme } from 'antd';
import type { CSSProperties } from 'react';

const STANDARD_AVATAR_SIZE = 40;

export interface AgorAvatarProps extends Omit<AvatarProps, 'style' | 'size'> {
  /** Optional style overrides */
  style?: CSSProperties;
}

/**
 * Standardized avatar component with consistent Agor styling
 */
export const AgorAvatar: React.FC<AgorAvatarProps> = ({ style, children, ...props }) => {
  const { token } = theme.useToken();

  return (
    <Avatar
      {...props}
      size={STANDARD_AVATAR_SIZE}
      style={{
        backgroundColor: token.colorPrimaryBg,
        color: token.colorText,
        fontSize: '24px', // Standard emoji size for 40px avatar
        ...style,
      }}
    >
      {children}
    </Avatar>
  );
};
