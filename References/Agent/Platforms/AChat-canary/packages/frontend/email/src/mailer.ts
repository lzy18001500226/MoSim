import { render } from "@react-email/render";
import React from "react";
import { Resend } from "resend";
import { z } from "zod";
import type { LayoutProps } from "./_components/layout";

export const EmailConfig = z
  .object({
    transport: z.enum(["hosting", "resend", "plunk", "smtp"]),
    sender: z.string().optional(),
    resend: z
      .object({
        apiKey: z.string(),
      })
      .optional(),
    plunk: z
      .object({
        apiKey: z.string(),
      })
      .optional(),
    smtp: z
      .object({
        host: z.string(),
        port: z.number(),
      })
      .optional(),
  })
  .default({
    transport: "hosting",
  });

export type EmailConfig = z.infer<typeof EmailConfig>;

export type TransportPayload = {
  to: string[];
  name?: string;
  subject: string;
  html?: string;
  text?: string;
};
export type Transporter = (data: TransportPayload) => Promise<any>;

export class Emailer {
  private transporter: Transporter;

  constructor(
    private config: EmailConfig,
    private layout: Omit<LayoutProps, "children">,
  ) {
    if (config.transport === "resend") {
      if (!config.resend || !config.sender) {
        throw new Error("Resend is not enabled");
      }
      const resend = new Resend(config.resend.apiKey);
      this.transporter = ({ to, subject, html, text }) =>
        resend.emails.send({
          from: config.sender as string,
          to: to,
          subject: subject,
          html,
          text: text || subject,
        });
    } else if (config.transport === "plunk") {
      if (!config.plunk) {
        throw new Error("Plunk is not enabled");
      }
      this.transporter = async ({ name, to, subject, html, text }) =>
        fetch("https://api.useplunk.com/v1/send", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${config.plunk?.apiKey}`,
          },
          body: JSON.stringify({
            to: to,
            subject: subject,
            body: html || text || subject,
            subscribed: true,
            name: name,
            from: config.sender,
          }),
        }).then((response) => response.json());
    } else {
      throw new Error("Invalid transport");
    }
  }

  transport(payload: TransportPayload) {
    return this.transporter(payload);
  }

  render(element: React.ReactElement) {
    if (!element || typeof element !== "object" || !element.props) {
      throw new Error(
        "Invalid React element provided to renderEmailWithModifiedProps",
      );
    }
    const tenantElement = React.cloneElement(element, {
      ...element.props,
      ...this.layout,
    });
    return render(tenantElement);
  }
}
