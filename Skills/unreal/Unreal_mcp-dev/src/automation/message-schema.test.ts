import { describe, expect, it } from 'vitest';
import { automationMessageSchema } from './message-schema.js';

describe('automationMessageSchema', () => {
    it('preserves unknown top-level bridge payload fields', () => {
        const message = {
            type: 'bridge_ack',
            serverName: 'UnrealMCP',
            heartbeatIntervalMs: 15000,
            futureCapability: {
                modes: ['native', 'bridge']
            }
        };

        expect(automationMessageSchema.parse(message)).toEqual(message);
    });
});
