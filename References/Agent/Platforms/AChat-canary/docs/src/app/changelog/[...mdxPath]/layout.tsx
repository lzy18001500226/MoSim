import { Link } from "nextra-theme-docs";

import { generateChangelogParams, getPage, type Props } from "./action";
import { useMDXComponents as getMDXComponents } from "@/mdx-components";
import { Author } from "@/components/authors";

// biome-ignore lint/style/noNonNullAssertion: <explanation>
const Wrapper = getMDXComponents().wrapper!;

export const generateStaticParams = generateChangelogParams

export default async function Layout({
	children,
	...props
}: Props & {
	children: React.ReactNode;
}) {
	const { toc, metadata } = await getPage(props);
	const { title, description, author, date } = metadata;
	return (
		<Wrapper toc={toc} metadata={metadata}>
			{title !== "Index" ? (
				<div className="md:mt-10 flex flex-col gap-10">
					<Link href="/changelog/" className="md:mb-10 text-primary">
						← Back to changelog
					</Link>
					<div>
						<div className="text-lg text-primary/60 mb-3">
							{date &&
								new Date(date).toLocaleDateString("zh-CN", {
									year: "numeric",
									month: "long",
									day: "numeric",
									timeZone: "Asia/Shanghai",
								})}
							{/* {!!badge && ` | ${badge}`} */}
						</div>
						<div className="flex flex-col gap-5 md:gap-10 md:flex-row justify-between md:items-center">
							<div>
								<h1 className="text-2xl md:text-3xl text-pretty font-mono">
									{title}
								</h1>
							</div>
							<Author author={author} />
						</div>
					</div>
					<p className="text-[17px]">{description}</p>
					{children}
				</div>
			) : (
				children
			)}
		</Wrapper>
	);
}

export const dynamic = "force-static";
