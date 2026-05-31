export { ThemeProvider, useTheme } from "../providers/ThemeProvider";

export type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: string;
  storageKey?: string;
  attribute?: string;
};
