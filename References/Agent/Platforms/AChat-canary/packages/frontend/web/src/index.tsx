import "./instrument.ts";
import * as Sentry from "@sentry/react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./router.tsx";
import "./index.css";

// biome-ignore lint/style/noNonNullAssertion: Exist in ./index.html
const container = document.getElementById("root")!;

const root = createRoot(container, {
  // Callback called when an error is thrown and not caught by an ErrorBoundary.
  onUncaughtError: Sentry.reactErrorHandler((error, errorInfo) => {
    console.warn("Uncaught error", error, errorInfo.componentStack);
  }),
  // Callback called when React catches an error in an ErrorBoundary.
  onCaughtError: Sentry.reactErrorHandler((error, errorInfo) => {
    console.warn("Caught error", error, errorInfo.componentStack);
  }),
  // Callback called when React automatically recovers from errors.
  onRecoverableError: Sentry.reactErrorHandler((error, errorInfo) => {
    console.warn("Recoverable error", error, errorInfo.componentStack);
  }),
});

root.render(
  <StrictMode>
    <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
      <App />
    </Sentry.ErrorBoundary>
  </StrictMode>
);
