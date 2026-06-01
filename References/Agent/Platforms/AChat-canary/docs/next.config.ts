import nextra from "nextra";

import type { NextConfig } from "next";

const withNextra = nextra({
	contentDirBasePath: "/changelog",
	staticImage: true,
	search: {
		codeblocks: true,
	},
	defaultShowCopyCode: true,
});
const nextConfig: NextConfig = {
  assetPrefix: '/docs',
	images: {
		loader: "custom",
		loaderFile: "./image-loader.ts",
	},
};

export default withNextra(nextConfig);
