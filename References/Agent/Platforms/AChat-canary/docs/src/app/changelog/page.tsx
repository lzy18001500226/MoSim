import { Link } from "nextra-theme-docs";
import { Header } from "@/components/landing/header";
import ChangelogIndex from "@/components/changelog";

export default function Page() {
	return (
		<div className="md:container">
			<div className="flex flex-col items-center content-center text-center my-10">
				<Header
					title="变更日志"
					description={
						<>
							来自 VMBoard 团队的最新版本更新. 查看我们的{" "}
							<Link href="/docs/roadmap" className="underline text-primary">
								路线图
							</Link>{" "}
							了解下一步计划。
						</>
					}
					className="mb-8"
					h="h1"
				/>
				<div className="mb-8">
					{/* <ProductUpdateSignup source="changelog" /> */}
				</div>
			</div>
			<ChangelogIndex />
		</div>
	);
}
