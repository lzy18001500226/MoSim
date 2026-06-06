export type DeploymentOption = "cloud" | "selfHosted";

export type DeploymentOptionParams = {
	switch: React.ReactNode;
	title: string;
	subtitle: string;
	// href: string;
};

export const deploymentOptions: Record<DeploymentOption, DeploymentOptionParams> = {
	cloud: {
		switch: (
			<span className="flex flex-row items-center gap-x-1">
				VMBoard
				<span className="hidden md:block"> (专业托管)</span>
			</span>
		),
		title: "定价",
		subtitle:
			"Get started on the Hobby plan for free. No credit card required.",
		// href: "/pricing",
	},
	selfHosted: {
		switch: (
			<span className="flex flex-row items-center gap-x-1">
				自部署
				<span className="hidden md:block"> (自托管)</span>
			</span>
		),
		title: "定价",
		subtitle:
			"Deploy Langfuse OSS today. Upgrade to Pro or Enterprise at any time.",
		// href: "/pricing-self-host",
	},
} as const;
