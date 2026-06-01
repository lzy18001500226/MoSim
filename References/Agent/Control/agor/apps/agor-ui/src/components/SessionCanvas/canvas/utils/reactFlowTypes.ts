/**
 * React Flow type extensions
 *
 * Extends base React Flow types with runtime properties that exist
 * but aren't in the official type definitions.
 */

import type { Node } from 'reactflow';

/**
 * Extended Node type with measured dimensions
 *
 * React Flow calculates node dimensions from the DOM at runtime and stores
 * them in a `measured` property. This isn't in the official type definitions,
 * so we extend the base Node type to include it.
 */
export interface ReactFlowNode extends Node {
  measured?: {
    width?: number;
    height?: number;
  };
}
