import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { TaskBadgeActions } from "../TaskBadgeActions";

describe("TaskBadgeActions", () => {
  it("renders Logs before the enabled badge", () => {
    const html = renderToStaticMarkup(
      React.createElement(TaskBadgeActions, {
        enabled: true,
        logsHref: "/logs",
        onToggle: () => {},
      }),
    );

    expect(html.indexOf("Logs")).toBeLessThan(html.indexOf("Enabled"));
  });

  it("renders the toggle as a button", () => {
    const html = renderToStaticMarkup(
      React.createElement(TaskBadgeActions, {
        enabled: false,
        logsHref: "/logs",
        onToggle: () => {},
      }),
    );

    expect(html).toContain("<button");
    expect(html).toContain("Disabled");
  });
});
