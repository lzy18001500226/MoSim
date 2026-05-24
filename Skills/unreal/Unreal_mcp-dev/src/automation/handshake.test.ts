import { EventEmitter } from 'node:events';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { WebSocket } from 'ws';
import { Logger } from '../utils/logger.js';
import { HandshakeHandler } from './handshake.js';

class FakeSocket extends EventEmitter {
    readyState = WebSocket.OPEN;
    sent: string[] = [];
    close = vi.fn();

    send(payload: string): void {
        this.sent.push(payload);
    }
}

describe('HandshakeHandler', () => {
    let debugSpy: ReturnType<typeof vi.spyOn>;
    let debugMessages: string[];

    beforeEach(() => {
        vi.useFakeTimers();
        debugMessages = [];
        debugSpy = vi.spyOn(Logger.prototype, 'debug').mockImplementation((...args: unknown[]) => {
            debugMessages.push(args.map(arg => String(arg)).join(' '));
        });
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.restoreAllMocks();
    });

    it('sends but does not log capability tokens', async () => {
        const socket = new FakeSocket();
        const promise = new HandshakeHandler('secret-token').initiateHandshake(socket as unknown as WebSocket, 1000);

        await vi.advanceTimersByTimeAsync(500);

        expect(socket.sent).toHaveLength(1);
        expect(socket.sent[0]).toContain('secret-token');

        expect(debugSpy).toHaveBeenCalledWith('Sending bridge_hello (delayed)');
        const debugOutput = debugMessages.join('\n');
        expect(debugOutput).not.toContain('secret-token');

        socket.emit('message', JSON.stringify({ type: 'bridge_ack' }));

        await expect(promise).resolves.toEqual({});
    });
});
