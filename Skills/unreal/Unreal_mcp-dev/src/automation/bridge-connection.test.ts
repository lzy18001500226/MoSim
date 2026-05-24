import net from 'node:net';
import { afterEach, describe, expect, it } from 'vitest';
import { AutomationBridge } from './bridge.js';

async function closeTcpServer(server: net.Server): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    server.close(error => {
      if (error) reject(error);
      else resolve();
    });
  });
}

describe('AutomationBridge lazy connection recovery', () => {
  const sockets: net.Socket[] = [];

  afterEach(() => {
    for (const socket of sockets.splice(0)) {
      socket.destroy();
    }
  });

  it('starts a fresh connection attempt after a lazy connection timeout', async () => {
    let connectionCount = 0;
    const server = net.createServer(socket => {
      connectionCount++;
      sockets.push(socket);
    });

    await new Promise<void>((resolve, reject) => {
      server.once('error', reject);
      server.listen(0, '127.0.0.1', resolve);
    });

    const address = server.address();
    if (!address || typeof address === 'string') {
      await closeTcpServer(server);
      throw new Error('Failed to bind test TCP server');
    }

    const bridge = new AutomationBridge({
      clientHost: '127.0.0.1',
      clientPort: address.port,
      connectionTimeoutMs: 50,
      heartbeatIntervalMs: 0
    });
    bridge.on('error', () => undefined);

    try {
      await expect(bridge.sendAutomationRequest('list', {}, { timeoutMs: 50 }))
        .rejects.toThrow(/Lazy connection timeout/);
      const firstConnectionCount = connectionCount;
      expect(firstConnectionCount).toBeGreaterThan(0);

      await expect(bridge.sendAutomationRequest('list', {}, { timeoutMs: 50 }))
        .rejects.toThrow(/Lazy connection timeout/);
      expect(connectionCount).toBeGreaterThan(firstConnectionCount);
    } finally {
      bridge.stop();
      for (const socket of sockets.splice(0)) {
        socket.destroy();
      }
      await closeTcpServer(server);
    }
  });

  it('rejects an in-flight lazy connection attempt immediately when stopped', async () => {
    const server = net.createServer(socket => {
      sockets.push(socket);
    });

    await new Promise<void>((resolve, reject) => {
      server.once('error', reject);
      server.listen(0, '127.0.0.1', resolve);
    });

    const address = server.address();
    if (!address || typeof address === 'string') {
      await closeTcpServer(server);
      throw new Error('Failed to bind test TCP server');
    }

    const bridge = new AutomationBridge({
      clientHost: '127.0.0.1',
      clientPort: address.port,
      connectionTimeoutMs: 5000,
      heartbeatIntervalMs: 0
    });
    bridge.on('error', () => undefined);

    try {
      const request = bridge.sendAutomationRequest('list', {}, { timeoutMs: 5000 });
      await new Promise(resolve => setTimeout(resolve, 25));

      bridge.stop();

      await expect(Promise.race([
        request,
        new Promise((_, reject) => setTimeout(() => reject(new Error('stop did not reject lazy attempt promptly')), 500))
      ])).rejects.toThrow(/server stopped/);
    } finally {
      bridge.stop();
      for (const socket of sockets.splice(0)) {
        socket.destroy();
      }
      await closeTcpServer(server);
    }
  });
});
