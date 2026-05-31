import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Pi-native wrapper around the existing Windows-MCP stdio server.
// This intentionally does not change Windows-MCP internals.

type ToolResult = {
  content?: Array<{ type: string; text?: string; data?: string; mimeType?: string }>;
  [key: string]: unknown;
};

function resultToText(result: ToolResult): string {
  const parts = (result.content ?? [])
    .map((item) => {
      if (item.type === "text") return item.text ?? "";
      if (item.type === "image") return `[image omitted: ${item.mimeType ?? "image"}]`;
      return JSON.stringify(item);
    })
    .filter(Boolean);
  return parts.length ? parts.join("\n") : JSON.stringify(result, null, 2);
}

function isWindowsMcpRoot(path: string): boolean {
  return existsSync(resolve(path, "src/windows_mcp/__main__.py")) &&
    existsSync(resolve(path, "pyproject.toml"));
}

function findProjectRoot(): string {
  const here = dirname(fileURLToPath(import.meta.url));
  const candidates = [
    process.env.WINDOWS_MCP_ROOT,
    process.cwd(),
    resolve(process.cwd(), "Windows-MCP"),
    resolve(here, ".."),
    resolve(here, "../.."),
    resolve(here, "../../.."),
  ].filter((path): path is string => Boolean(path));

  const root = candidates.find(isWindowsMcpRoot);
  if (!root) {
    throw new Error(
      "Could not find the Windows-MCP project root. Run Pi from the Windows-MCP checkout, " +
      "install this package via `pi install git:github.com/CursorTouch/Windows-MCP`, " +
      "or set WINDOWS_MCP_ROOT=C:\\path\\to\\Windows-MCP."
    );
  }
  return root;
}

const point = Type.Array(Type.Number(), {
  minItems: 2,
  maxItems: 2,
  description: "Screen coordinates [x, y].",
});

export default function (pi: ExtensionAPI) {
  let client: Client | undefined;
  let connecting: Promise<Client> | undefined;
  let pendingClient: Client | undefined;
  let shuttingDown = false;

  async function getClient(): Promise<Client> {
    if (process.platform !== "win32") {
      throw new Error("Windows-MCP can only control a Windows desktop. Run this Pi extension on Windows.");
    }
    if (shuttingDown) {
      throw new Error("Windows-MCP Pi extension is shutting down.");
    }
    if (client) return client;
    if (!connecting) {
      let connection!: Promise<Client>;
      connection = (async () => {
        const transport = new StdioClientTransport({
          command: "uv",
          args: ["run", "windows-mcp"],
          cwd: findProjectRoot(),
        });
        const next = new Client({ name: "pi-windows-mcp", version: "0.1.0" });
        pendingClient = next;
        try {
          await next.connect(transport);
          if (shuttingDown) {
            await next.close();
            throw new Error("Windows-MCP Pi extension shut down during connection.");
          }
          client = next;
          return next;
        } catch (error) {
          if (client === next) client = undefined;
          try { await next.close(); } catch {}
          throw error;
        } finally {
          if (pendingClient === next) pendingClient = undefined;
          if (connecting === connection) connecting = undefined;
        }
      })();
      connecting = connection;
    }
    return connecting;
  }

  async function callWindows(tool: string, args: Record<string, unknown>) {
    const activeClient = await getClient();
    const result = (await activeClient.callTool({ name: tool, arguments: args })) as ToolResult;
    return { content: [{ type: "text" as const, text: resultToText(result) }], details: result };
  }

  pi.on("session_shutdown", async () => {
    shuttingDown = true;
    const activeClient = client;
    const inFlightConnection = connecting;
    const inFlightClient = pendingClient;
    client = undefined;
    connecting = undefined;
    pendingClient = undefined;

    try { await activeClient?.close(); } catch {}
    if (inFlightClient && inFlightClient !== activeClient) {
      try { await inFlightClient.close(); } catch {}
    }
    if (inFlightConnection) {
      try {
        const connectedClient = await inFlightConnection;
        if (connectedClient !== activeClient && connectedClient !== inFlightClient) {
          await connectedClient.close();
        }
      } catch {}
    }
  });

  pi.registerTool({
    name: "win_snapshot",
    label: "Windows Snapshot",
    description: "Read Windows UI state through Windows-MCP Snapshot. Returns windows, interactive elements, labels/ids, scrollable areas, and optional screenshot data.",
    promptSnippet: "Inspect Windows UI state through Windows-MCP.",
    promptGuidelines: [
      "Use win_snapshot before controlling Windows applications with Windows-MCP tools.",
      "Prefer labels/ids returned by win_snapshot when available; otherwise use coordinates.",
      "Set use_vision=true only when you need screenshot context.",
      "Use use_dom=true for browser page content instead of browser chrome.",
    ],
    parameters: Type.Object({
      use_vision: Type.Optional(Type.Boolean({ default: false })),
      use_dom: Type.Optional(Type.Boolean({ default: false })),
      use_annotation: Type.Optional(Type.Boolean({ default: true })),
      use_ui_tree: Type.Optional(Type.Boolean({ default: true })),
      display: Type.Optional(Type.Array(Type.Number())),
    }),
    async execute(_id, params) {
      return callWindows("Snapshot", {
        use_vision: params.use_vision ?? false,
        use_dom: params.use_dom ?? false,
        use_annotation: params.use_annotation ?? true,
        use_ui_tree: params.use_ui_tree ?? true,
        display: params.display,
      });
    },
  });

  pi.registerTool({
    name: "win_screenshot",
    label: "Windows Screenshot",
    description: "Capture a fast screenshot-first Windows desktop snapshot through Windows-MCP. Use win_snapshot when you need UI element labels/ids.",
    parameters: Type.Object({
      use_annotation: Type.Optional(Type.Boolean({ default: false })),
      display: Type.Optional(Type.Array(Type.Number())),
    }),
    async execute(_id, params) {
      return callWindows("Screenshot", {
        use_annotation: params.use_annotation ?? false,
        display: params.display,
      });
    },
  });

  pi.registerTool({
    name: "win_app",
    label: "Windows App",
    description: "Launch, switch, or resize Windows applications/windows through Windows-MCP.",
    parameters: Type.Object({
      mode: Type.Union([Type.Literal("launch"), Type.Literal("switch"), Type.Literal("resize")]),
      name: Type.Optional(Type.String()),
      window_loc: Type.Optional(point),
      window_size: Type.Optional(point),
    }),
    async execute(_id, params) {
      return callWindows("App", params as Record<string, unknown>);
    },
  });

  pi.registerTool({
    name: "win_click",
    label: "Windows Click",
    description: "Click Windows screen coordinates or a UI element label/id through Windows-MCP. Call win_snapshot first.",
    parameters: Type.Object({
      loc: Type.Optional(point),
      label: Type.Optional(Type.Number()),
      button: Type.Optional(Type.Union([Type.Literal("left"), Type.Literal("right"), Type.Literal("middle")], { default: "left" })),
      clicks: Type.Optional(Type.Number({ default: 1, description: "0=hover, 1=single click, 2=double click." })),
    }),
    async execute(_id, params) {
      return callWindows("Click", {
        loc: params.loc,
        label: params.label,
        button: params.button ?? "left",
        clicks: params.clicks ?? 1,
      });
    },
  });

  pi.registerTool({
    name: "win_type",
    label: "Windows Type",
    description: "Type text at Windows coordinates or a UI element label/id through Windows-MCP. Call win_snapshot first.",
    parameters: Type.Object({
      text: Type.String(),
      loc: Type.Optional(point),
      label: Type.Optional(Type.Number()),
      clear: Type.Optional(Type.Boolean({ default: false })),
      caret_position: Type.Optional(Type.Union([Type.Literal("start"), Type.Literal("idle"), Type.Literal("end")], { default: "idle" })),
      press_enter: Type.Optional(Type.Boolean({ default: false })),
    }),
    async execute(_id, params) {
      return callWindows("Type", {
        text: params.text,
        loc: params.loc,
        label: params.label,
        clear: params.clear ?? false,
        caret_position: params.caret_position ?? "idle",
        press_enter: params.press_enter ?? false,
      });
    },
  });

  pi.registerTool({
    name: "win_move",
    label: "Windows Move",
    description: "Move the mouse or drag to coordinates/a UI element label through Windows-MCP.",
    parameters: Type.Object({
      loc: Type.Optional(point),
      label: Type.Optional(Type.Number()),
      drag: Type.Optional(Type.Boolean({ default: false })),
    }),
    async execute(_id, params) {
      return callWindows("Move", {
        loc: params.loc,
        label: params.label,
        drag: params.drag ?? false,
      });
    },
  });

  pi.registerTool({
    name: "win_scroll",
    label: "Windows Scroll",
    description: "Scroll vertically or horizontally at coordinates, a UI element label/id, or the current cursor through Windows-MCP.",
    parameters: Type.Object({
      loc: Type.Optional(point),
      label: Type.Optional(Type.Number()),
      type: Type.Optional(Type.Union([Type.Literal("horizontal"), Type.Literal("vertical")], { default: "vertical" })),
      direction: Type.Optional(Type.Union([Type.Literal("up"), Type.Literal("down"), Type.Literal("left"), Type.Literal("right")], { default: "down" })),
      wheel_times: Type.Optional(Type.Number({ default: 1 })),
    }),
    async execute(_id, params) {
      return callWindows("Scroll", {
        loc: params.loc,
        label: params.label,
        type: params.type ?? "vertical",
        direction: params.direction ?? "down",
        wheel_times: params.wheel_times ?? 1,
      });
    },
  });

  pi.registerTool({
    name: "win_shortcut",
    label: "Windows Shortcut",
    description: "Run a Windows keyboard shortcut through Windows-MCP, e.g. ctrl+c, alt+tab, win+r.",
    parameters: Type.Object({ shortcut: Type.String() }),
    async execute(_id, params) {
      return callWindows("Shortcut", { shortcut: params.shortcut });
    },
  });

  pi.registerTool({
    name: "win_wait",
    label: "Windows Wait",
    description: "Wait for UI loading/animations through Windows-MCP.",
    parameters: Type.Object({ duration: Type.Number({ description: "Seconds to wait." }) }),
    async execute(_id, params) {
      return callWindows("Wait", { duration: params.duration });
    },
  });
}
