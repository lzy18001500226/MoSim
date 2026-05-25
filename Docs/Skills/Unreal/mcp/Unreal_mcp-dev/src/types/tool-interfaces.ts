import { AutomationBridge } from '../automation/index.js';

export interface IBaseTool {
    getAutomationBridge(): AutomationBridge;
}

export interface StandardActionResponse<T = unknown> {
    success: boolean;
    message?: string;
    data?: T;
    warnings?: string[];
    error?: string | {
        code?: string;
        message: string;
        [key: string]: unknown;
    } | null;
    [key: string]: unknown;
}

export interface IAssetResources {
    list(directory?: string, recursive?: boolean, limit?: number): Promise<Record<string, unknown>>;
}

export interface ITools {
    systemTools: {
        executeConsoleCommand: (command: string) => Promise<unknown>;
        getProjectSettings: (section?: string) => Promise<Record<string, unknown>>;
    };
    elicit?: unknown;
    supportsElicitation?: () => boolean;
    elicitationTimeoutMs?: number;
    assetResources: IAssetResources;
    actorResources?: unknown;
    levelResources?: unknown;
    automationBridge?: AutomationBridge;
    bridge?: unknown;
    [key: string]: unknown;
}
