import { DeploymentOption } from "./options";

export type Tier = {
	name: string;
	id: string;
	href: string;
	featured: boolean;
	description: string;
	price: string;
	priceUnit?: string;
	mainFeatures: string[];
	cta: string;
	priceDiscountCta?: {
		name: string;
		href: string;
	};
	learnMore?: string;
};

export const tiers: Record<DeploymentOption, Tier[]> = {
	cloud: [
		{
			name: "Free",
			id: "tier-free",
			href: "https://vmboard.io/auth",
			featured: false,
			description:
				"开始使用，无需信用卡。非常适合业余项目和 POC。",
			price: "¥0",
			mainFeatures: [
				"所有平台功能（有限制）",
				"3 台服务器监控",
				"7 天数据保留",
				"独立用户访问",
				"社区支持 (论坛 & GitHub)",
			],
			cta: "立即体验",
		},
		{
			name: "Lite",
			id: "tier-lite",
			href: "https://vmboard.io/auth",
			featured: true,
			description:
				"适用于生产项目。包括访问完整历史记录和更高的使用率。",
			price: "$5",
			priceDiscountCta: {
				name: "Discounts available",
				href: "/pricing#discounts",
			},
			mainFeatures: [
				"包含 Hobby 计划",
				"10 台服务器监控",
				"30 天数据保留",
				"独立用户访问",
				"随时随地邮件支持",
			],
			cta: "立即体验",
		},
		{
			name: "Pro",
			id: "tier-pro",
			href: "https://vmboard.io/auth",
			featured: false,
			price: "$10",
			priceUnit: "用户/月",
			description: "为大型团队提供专门支持和安全控制。",
			mainFeatures: [
				"包含 Pro 计划",
				"50 台服务器监控",
				"365 天数据保留",
				"细粒度 RBAC",
				"随时随地邮件支持",
			],
			cta: "立即体验",
		},
		{
			name: "Enterprise",
			id: "tier-enterprise",
			href: "/schedule-demo",
			featured: false,
			description: "企业级支持和安全功能。",
			price: "定制",
			mainFeatures: [
				"包含所有功能",
				"企业级安全功能",
				"SOC2, ISO27001, 和 InfoSec 审查",
				"专属支持工程师",
				"支持 SLA",
			],
			cta: "与我们联系",
		},
	],
	selfHosted: [
		{
			name: "Open Source",
			id: "tier-self-hosted-oss",
			href: "/self-hosting",
			featured: true,
			description:
				"自托管所有核心 Langfuse 功能，无需任何限制。",
			price: "免费",
			mainFeatures: [
				"MIT License",
				"所有核心平台功能和 API（可观测性、评估、提示管理、数据集等）",
				"Langfuse Cloud 的可扩展性",
				"部署文档 & Helm 图表",
				"企业 SSO 和 RBAC",
				"社区支持（论坛和 GitHub）",
			],
			cta: "部署文档",
		},
		{
			name: "部署维护",
			id: "tier-self-hosted-pro",
			href: "https://buy.stripe.com/aEU6qufIwfJy0CYbIR",
			featured: false,
			description:
				"获取额外的流程功能以加速您的团队。",
			price: "¥100",
			priceUnit: "次",
			mainFeatures: [
				"All Open Source features",
				"LLM Playground",
				"Human annotation queues",
				"LLM-as-a-judge evaluators",
				"Prompt Experiments",
				"Chat & Email support",
			],
			cta: "Subscribe",
		},
		{
			name: "Enterprise",
			id: "tier-self-hosted-enterprise",
			href: "/schedule-demo",
			featured: false,
			price: "Custom",
			description: "Enterprise-grade support and security features.",
			mainFeatures: [
				"包含所有功能",
				"项目级 RBAC",
				"企业级安全功能",
				"SOC2, ISO27001, 和 InfoSec 审查",
				"专属支持工程师",
				"支持 SLA",
			],
			cta: "Talk to sales",
			learnMore: "/enterprise",
		},
	],
} as const;