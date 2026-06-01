import winston, { format } from "winston";
import LokiTransport from "winston-loki";
import Transport from "winston-transport";
import * as Sentry from "@sentry/node";
const SentryWinstonTransport = Sentry.createSentryWinstonTransport(Transport);

declare module "winston" {
  interface Logger {
    clearMeta(): void;
    initMeta(meta: Record<string, any>): void;
    appendMeta(meta: Record<string, any>): void;
  }
}

export const getLogger = (appName: string, labels?: Record<string, string>) => {
  const transports: winston.transport | winston.transport[] = [];

  if (process.env.SENTRY_DSN) {
    transports.push(
      new SentryWinstonTransport({
        level: process.env.LOG_LEVEL || "info",
      })
    );
  }
  if (process.env.NODE_ENV === "production") {
    if (process.env.LOKI_URL) {
      transports.push(
        new LokiTransport({
          host: process.env.LOKI_URL,
          labels: { app: appName, ...labels },
          json: true,
          format: winston.format.json(),
          replaceTimestamp: true,
          onConnectionError: (err) => console.error("[Logger]", err),
        })
      );
    } else {
      console.warn(
        "[Logger] LOKI_URL is not set, LokiTransport will not be used"
      );
    }
  }
  if (process.env.NODE_ENV === "development") {
    transports.push(
      new winston.transports.Console({
        format: format.combine(
          format.colorize(),
          format.timestamp(),
          format.align(),
          format.printf(
            (info) =>
              `${info.timestamp}\t[${info.level}]\t${info.ip}\t${[
                info.type || info.method,
              ]}\t${info.path}${info.duration ? `(${info.duration}ms)` : ""}\t${
                info.message
              }` || JSON.stringify(info)
          )
        ),
      })
    );
  }

  const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || "info",
    transports: transports,
  });

  logger.clearMeta = () => {
    logger.defaultMeta = {};
  };
  logger.initMeta = (meta: Record<string, any>) => {
    logger.defaultMeta = meta;
  };
  logger.appendMeta = (meta: Record<string, any>) => {
    logger.defaultMeta = {
      ...logger.defaultMeta,
      ...meta,
    };
  };

  return logger;
};
