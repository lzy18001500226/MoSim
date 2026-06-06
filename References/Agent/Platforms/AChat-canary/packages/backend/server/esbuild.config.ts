import "dotenv/config";
import { sentryEsbuildPlugin } from "@sentry/esbuild-plugin";
import esbuild from "esbuild";

try {
  esbuild
    .build({
      entryPoints: {
        server: "src/index.ts",
      },
      bundle: true,
      platform: "node",
      format: "esm",
      target: "node18",
      outExtension: { ".js": ".mjs" },
      minify: true,
      sourcemap: true,
      outdir: "dist",
      tsconfig: "tsconfig.json",
      packages: "external",
      plugins: [
        sentryEsbuildPlugin({
          sourcemaps: {
            filesToDeleteAfterUpload: ["*.map"],
          },
        }),
      ],
    })
    .catch(() => {
      return process.exit(1);
    });
} catch (error) {
  console.log(error);
}
