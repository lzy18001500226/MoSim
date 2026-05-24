import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { UnrealBridge } from './unreal-bridge.js';
import { AutomationBridge } from './automation/index.js';
import { Logger } from './utils/logger.js';
import { HealthMonitor } from './services/health-monitor.js';
import { AssetResources } from './resources/assets.js';
import { ActorResources } from './resources/actors.js';
import { LevelResources } from './resources/levels.js';
import { ResourceRegistry } from './server/resource-registry.js';
import { ToolRegistry } from './server/tool-registry.js';
import fs from 'node:fs';

export class ServerSetup {
  private server: Server;
  private bridge: UnrealBridge;
  private automationBridge: AutomationBridge;
  private logger: Logger;
  private healthMonitor: HealthMonitor;
  private assetResources: AssetResources;
  private actorResources: ActorResources;
  private levelResources: LevelResources;

  constructor(
    server: Server,
    bridge: UnrealBridge,
    automationBridge: AutomationBridge,
    logger: Logger,
    healthMonitor: HealthMonitor
  ) {
    this.server = server;
    this.bridge = bridge;
    this.automationBridge = automationBridge;
    this.logger = logger;
    this.healthMonitor = healthMonitor;

    // Initialize resources
    this.assetResources = new AssetResources(bridge);
    this.actorResources = new ActorResources(bridge, automationBridge);
    this.levelResources = new LevelResources(bridge, automationBridge);
  }

  async setup() {
    this.validateEnvironment();

    const ensureConnected = this.ensureConnectedOnDemand.bind(this);

    // Register Resources
    const resourceRegistry = new ResourceRegistry(
      this.server,
      this.bridge,
      this.automationBridge,
      this.assetResources,
      this.actorResources,
      this.levelResources,
      this.healthMonitor,
      ensureConnected
    );
    resourceRegistry.register();

    // Register Tools
    const toolRegistry = new ToolRegistry(
      this.server,
      this.bridge,
      this.automationBridge,
      this.logger,
      this.healthMonitor,
      this.assetResources,
      this.actorResources,
      this.levelResources,
      ensureConnected
    );
    toolRegistry.register();
  }

  private validateEnvironment() {
    this.validateConfiguredPath(
      'UE_PROJECT_PATH',
      process.env.UE_PROJECT_PATH,
      'UE_PROJECT_PATH is not set. Offline project settings fallback will be disabled.'
    );
    this.validateConfiguredPath('UE_ENGINE_PATH', process.env.UE_ENGINE_PATH || process.env.UNREAL_ENGINE_PATH);
  }

  private validateConfiguredPath(envName: string, configuredPath: string | undefined, notSetMessage?: string) {
    if (!configuredPath) {
      if (notSetMessage) {
        this.logger.info(notSetMessage);
      }
      return;
    }

    if (!fs.existsSync(configuredPath)) {
      this.logger.warn(`${envName} is set to '${configuredPath}' but the path does not exist.`);
      return;
    }

    this.logger.info(`${envName} validated: ${configuredPath}`);
  }

  private async ensureConnectedOnDemand(): Promise<boolean> {
    if (this.bridge.isConnected) return true;
    const ok = await this.bridge.tryConnect(3, 5000, 1000);
    if (ok) {
      this.healthMonitor.metrics.connectionStatus = 'connected';
      this.healthMonitor.startHealthChecks(this.bridge);
    } else {
      this.healthMonitor.metrics.connectionStatus = 'disconnected';
    }
    return ok;
  }


}
