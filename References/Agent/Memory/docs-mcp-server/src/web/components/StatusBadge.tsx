/**
 * StatusBadge component displays version status with appropriate styling.
 * Uses database VersionStatus and helper functions for proper display.
 */

import { VersionStatus, getStatusDescription } from "../../store/types";

interface StatusBadgeProps {
  status: VersionStatus;
  showDescription?: boolean;
}

/**
 * Get CSS classes for status badge based on status type.
 */
function getStatusClasses(status: VersionStatus): string {
  const baseClasses = "px-1.5 py-0.5 text-xs font-medium rounded";

  switch (status) {
    case VersionStatus.COMPLETED:
      return `${baseClasses} bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300`;
    case VersionStatus.RUNNING:
    case VersionStatus.UPDATING:
      return `${baseClasses} bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300`;
    case VersionStatus.QUEUED:
      return `${baseClasses} bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300`;
    case VersionStatus.FAILED:
      return `${baseClasses} bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300`;
    case VersionStatus.CANCELLED:
      return `${baseClasses} bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300`;
    case VersionStatus.NOT_INDEXED:
    default:
      return `${baseClasses} bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400`;
  }
}

const StatusBadge = ({ status, showDescription = true }: StatusBadgeProps) => (
  <span class={getStatusClasses(status)}>
    {showDescription ? getStatusDescription(status) : status}
  </span>
);

export default StatusBadge;
