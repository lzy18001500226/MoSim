import "@/globals.css";
import "nextra-theme-docs/style.css";
import "@/overrides.css";

import { Layout, Link, Navbar } from "nextra-theme-docs";
import Footer from "@/components/layout/footer";
import { Banner, Head, Search } from "nextra/components";
import { getPageMap } from "nextra/page-map";
import { Background } from "@/components/background";
import Telegram from "@/components/icons/telegram";
import { ForumLink } from "@/components/ui/link";
import Logo from "@/components/icons/logo";
import { Button } from "@/components/ui/button";
import { GithubMenuBadge } from "@/components/github-badge";

export const metadata = {
	title: {
		default: "VMBoard",
		template: "%s | VMBoard",
	},
	description:
		"VMBoard 是一个强大且轻量的服务器监控平台，实时获取服务器指标数据，支持 SSH 连接管理。",
	icons: {
		icon: "/icon.svg",
	},
};

const banner = <Banner storageKey="2025-03-15-unreleased">即将发布...</Banner>;
const navbar = (
	<Navbar
		logo={
			<>
				<Logo width={32} height={32} className="mr-2" />
				<b>VMBoard</b>
			</>
		}
		projectLink="https://github.com/achat/vmboard"
		chatLink="https://t.me/vmboard"
		chatIcon={<Telegram width={24} height={24} />}
	>
		<GithubMenuBadge />
		<Link href="/auth">
			<Button variant="default" size="sm" className="h-8">
				登录
			</Button>
		</Link>
	</Navbar>
);
const footer = <Footer />;
const search = (
	<Search
		emptyResult="没有找到结果"
		loading="加载中..."
		errorText="加载失败"
		placeholder="搜索..."
	/>
);

export default async function RootLayout({
	children,
}: { children: React.ReactNode }) {
	return (
		<html
			// Not required, but good for SEO
			lang="zh-CN"
			// Required to be set
			dir="ltr"
			className="antialiased"
			// Suggested by `next-themes` package https://github.com/pacocoursey/next-themes#with-app
			suppressHydrationWarning
		>
			<Head
			// ... Your additional head options
			>
				{/* Your additional tags should be passed as `children` of `<Head>` element */}
			</Head>
			<body>
				<Layout
					banner={banner}
					navbar={navbar}
					footer={footer}
					search={search}
					pageMap={await getPageMap()}
					editLink={null}
					feedback={{
						content: "有问题吗？给我们反馈",
					}}
					toc={{
						backToTop: "返回顶部",
						title: "目录",
						extraContent: (
							<ForumLink href="https://forum.vmboard.io">
								或与大家交流
							</ForumLink>
						),
					}}
					docsRepositoryBase="https://github.com/achat/vmboard"
				>
					{children}
				</Layout>
				<Background />
			</body>
		</html>
	);
}
