import type { DeploymentOption } from "./options";

export type Section = {
	name: string;
	href?: string;
	features: {
		name: string;
		href?: string;
		tiers: Partial<Record<DeploymentOption, Record<string, boolean | string>>>;
	}[];
};

export const sections: Section[] = [
	{
		name: "监控",
		href: "/docs/tracing",
		features: [
			{
				name: "服务器数量",
				href: "/docs/integrations/overview",
				tiers: {
					cloud: {
						Free: "包含 3 台",
						Lite: "包含 10 台",
						Pro: "每个用户包含 25 台",
						Enterprise: true,
					},
					selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
				},
			},
			{
				name: "数据保留期限",
				href: "/docs/api",
				tiers: {
					cloud: {
						Free: "7 天",
						Lite: "30 天",
						Pro: "365 天",
						Enterprise: "定制",
					},
					selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
				},
			},
			{
				name: "最小上报间隔",
				tiers: {
					cloud: {
						Free: "10 秒",
						Lite: "3 秒",
						Pro: "1 秒",
						Enterprise: "定制",
					},
					selfHosted: {
						"Open Source": "Unlimited",
						Lite: "Unlimited",
						Enterprise: "Unlimited",
					},
				},
			},
			{
				name: "报警规则",
				href: "/faq/all/api-limits",
				tiers: {
					cloud: {
						Free: "包含 10 条",
						Lite: "包含 25 条",
						Pro: "每个用户包含 50 条",
						Enterprise: "定制",
					},
				},
			},
			{
				name: "分享页面",
				href: "/faq/all/api-limits",
				tiers: {
					cloud: {
						Free: "最多 10 个",
						Lite: "♾️ 无限",
						Pro: "♾️ 无限",
						Enterprise: "♾️ 无限",
					},
				},
			},
			{
				name: "自定义二级域名",
				href: "/faq/all/api-limits",
				tiers: {
					cloud: {
						Free: "包含 1 个",
						Lite: "包含 3 个",
						Pro: "每个用户包含 10 个",
						Enterprise: "定制",
					},
				},
			},
			{
				name: "额外自定义二级域名",
				href: "/faq/all/api-limits",
				tiers: {
					cloud: {
						Free: "每个 $1",
						Lite: "每个 $1",
						Pro: "每个 $1",
						Enterprise: "定制",
					},
				},
			},
			{
				name: "自定义主机名",
				href: "/faq/all/api-limits",
				tiers: {
					cloud: {
						Free: false,
						Lite: "包含 1 个",
						Pro: "每个用户包含 3 个",
						Enterprise: "定制",
					},
				},
			},
			{
				name: "额外自定义主机名",
				href: "/faq/all/api-limits",
				tiers: {
					cloud: {
						Free: "每个 $10",
						Lite: "每个 $6",
						Pro: "每个 $4",
						Enterprise: "定制",
					},
				},
			},
		],
	},
	{
		name: "核心平台功能",
		features: [
			{
				name: "ICMP Ping",
				href: "/docs/datasets",
				tiers: {
					cloud: { Free: true, Lite: true, Pro: true, Enterprise: true },
					selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
				},
			},
			{
				name: "SSH 远程连接",
				href: "/docs/scores",
				tiers: {
					cloud: { Free: true, Lite: true, Pro: true, Enterprise: true },
					selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
				},
			},
			{
				name: "Prompt Management",
				href: "/docs/prompts",
				tiers: {
					cloud: { Free: true, Lite: true, Pro: true, Enterprise: true },
					selfHosted: {
						"Open Source": true,
						Lite: true,
						Enterprise: true,
					},
				},
			},
		],
	},
	// {
	// 	name: "Add-on Features",
	// 	features: [
	// 		{
	// 			name: "Playground",
	// 			href: "/docs/playground",
	// 			tiers: {
	// 				cloud: { Free: true, Lite: true, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": false, Lite: true, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Prompt Experiments",
	// 			href: "/docs/datasets/prompt-experiments",
	// 			tiers: {
	// 				cloud: { Free: true, Lite: true, Pro: true, Enterprise: true },
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: true,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "LLM-as-judge evaluators",
	// 			href: "/docs/scores/model-based-evals",
	// 			tiers: {
	// 				cloud: {
	// 					Free: "1 evaluator",
	// 					Lite: true,
	// 					Pro: true,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: true,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Human Annotation Queues",
	// 			href: "/docs/scores/annotation#annotation-queues",
	// 			tiers: {
	// 				cloud: {
	// 					Free: "1 queue",
	// 					Lite: "3 queues",
	// 					Pro: true,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: true,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 	],
	// },
	// {
	// 	name: "Collaboration",
	// 	features: [
	// 		{
	// 			name: "Projects",
	// 			tiers: {
	// 				cloud: {
	// 					Free: "Unlimited",
	// 					Lite: "Unlimited",
	// 					Pro: "Unlimited",
	// 					Enterprise: "Unlimited",
	// 				},
	// 				selfHosted: {
	// 					"Open Source": "Unlimited",
	// 					Lite: "Unlimited",
	// 					Enterprise: "Unlimited",
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Users",
	// 			tiers: {
	// 				cloud: {
	// 					Free: "2",
	// 					Lite: "Unlimited",
	// 					Pro: "Unlimited",
	// 					Enterprise: "Unlimited",
	// 				},
	// 				selfHosted: {
	// 					"Open Source": "Unlimited",
	// 					Lite: "As licensed",
	// 					Enterprise: "As licensed",
	// 				},
	// 			},
	// 		},
	// 	],
	// },
	// {
	// 	name: "API",
	// 	href: "/docs/api",
	// 	features: [
	// 		{
	// 			name: "Extensive Public API",
	// 			tiers: {
	// 				cloud: {
	// 					Free: true,
	// 					Lite: true,
	// 					Pro: true,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": true,
	// 					Lite: true,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Rate limit",
	// 			href: "/faq/all/api-limits",
	// 			tiers: {
	// 				cloud: {
	// 					Free: "1,000 requests / min",
	// 					Lite: "1,000 requests / min",
	// 					Pro: "1,000 requests / min",
	// 					Enterprise: "Custom",
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "SLA",
	// 			href: "/faq/all/api-limits",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: false, Enterprise: true },
	// 			},
	// 		},
	// 	],
	// },
	// {
	// 	name: "Support",
	// 	href: "/support",
	// 	features: [
	// 		{
	// 			name: "Ask AI",
	// 			href: "/docs/ask-ai",
	// 			tiers: {
	// 				cloud: { Free: true, Lite: true, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Community (GitHub, Discord)",
	// 			tiers: {
	// 				cloud: { Free: true, Lite: true, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Chat & Email",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: true, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": false, Lite: true, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Private Slack/Discord channel",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: true, Enterprise: true },
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: "included at >10 users",
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Dedicated Support Engineer",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: false, Enterprise: true },
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Support SLA",
	// 			tiers: {
	// 				cloud: {
	// 					Free: false,
	// 					Lite: false,
	// 					Pro: false,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: false,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Architectural guidance",
	// 			tiers: {
	// 				cloud: {
	// 					Free: false,
	// 					Lite: false,
	// 					Pro: false,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: false,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 	],
	// },
	// {
	// 	name: "Security",
	// 	href: "/docs/security",
	// 	features: [
	// 		{
	// 			name: "Data region",
	// 			tiers: {
	// 				cloud: {
	// 					Free: "US or EU",
	// 					Lite: "US or EU",
	// 					Pro: "US or EU",
	// 					Enterprise: "US or EU",
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "SSO via Google, AzureAD, GitHub",
	// 			tiers: {
	// 				cloud: {
	// 					Free: true,
	// 					Lite: true,
	// 					Pro: true,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": true,
	// 					Lite: true,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Organization-level RBAC",
	// 			href: "/docs/rbac",
	// 			tiers: {
	// 				cloud: {
	// 					Free: true,
	// 					Lite: true,
	// 					Pro: true,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": true,
	// 					Lite: true,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Enterprise SSO (e.g. Okta, AzureAD/EntraID)",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "SSO enforcement",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": true, Lite: true, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Project-level RBAC",
	// 			href: "/docs/rbac#project-level-roles",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Data retention management",
	// 			href: "/docs/data-retention",
	// 			tiers: {
	// 				cloud: {
	// 					Free: false,
	// 					Lite: false,
	// 					Pro: true,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: false,
	// 					Enterprise: true,
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Organization Creators",
	// 			href: "/self-hosting/organization-creators",
	// 			tiers: {
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "UI Customization",
	// 			href: "/self-hosting/ui-customization",
	// 			tiers: {
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "Audit Logs",
	// 			href: "/changelog/2025-01-21-audit-logs",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: false, Enterprise: true },
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 	],
	// },
	{
		name: "账单",
		features: [
			{
				name: "订阅管理",
				tiers: {
					cloud: {
						Free: false,
						Lite: "Self-serve",
						Pro: "Self-serve",
						Enterprise: "Sales",
					},
					selfHosted: {
						"Open Source": false,
						Lite: "自助服务",
						Enterprise: "合同",
					},
				},
			},
			{
				name: "支付方式",
				tiers: {
					cloud: {
						Free: false,
						Lite: "微信支付",
						Pro: "微信支付",
						Enterprise: "增值税发票",
					},
					selfHosted: {
						"Open Source": false,
						Lite: "Credit card",
						Enterprise: "Credit card, Invoice",
					},
				},
			},
			{
				name: "合同周期",
				tiers: {
					cloud: {
						Free: false,
						Lite: "每月 / 每年",
						Pro: "每月 / 每年",
						Enterprise: "定制",
					},
					selfHosted: {
						"Open Source": false,
						Lite: "每月 / 每年",
						Enterprise: "定制",
					},
				},
			},
			// {
			// 	name: "Billing via AWS Marketplace",
			// 	tiers: {
			// 		cloud: {
			// 			Free: false,
			// 			Lite: false,
			// 			Pro: false,
			// 			Enterprise: true,
			// 		},
			// 		selfHosted: {
			// 			"Open Source": false,
			// 			Lite: ">10 users",
			// 			Enterprise: true,
			// 		},
			// 	},
			// },
		],
	},
	// {
	// 	name: "Compliance",
	// 	href: "/security",
	// 	features: [
	// 		{
	// 			name: "Contracts",
	// 			tiers: {
	// 				cloud: {
	// 					Free: "Standard T&Cs",
	// 					Lite: "Standard T&Cs & DPA",
	// 					Pro: "Standard T&Cs & DPA",
	// 					Enterprise: "Custom",
	// 				},
	// 				selfHosted: {
	// 					"Open Source": false,
	// 					Lite: "Standard T&Cs",
	// 					Enterprise: "Custom",
	// 				},
	// 			},
	// 		},
	// 		{
	// 			name: "Data processing agreement (GDPR)",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: true, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "SOC2 Type II & ISO27001 reports",
	// 			tiers: {
	// 				cloud: { Free: false, Lite: false, Pro: true, Enterprise: true },
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 		{
	// 			name: "InfoSec/legal reviews",
	// 			tiers: {
	// 				cloud: {
	// 					Free: false,
	// 					Lite: false,
	// 					Pro: false,
	// 					Enterprise: true,
	// 				},
	// 				selfHosted: { "Open Source": false, Lite: false, Enterprise: true },
	// 			},
	// 		},
	// 	],
	// },
];
