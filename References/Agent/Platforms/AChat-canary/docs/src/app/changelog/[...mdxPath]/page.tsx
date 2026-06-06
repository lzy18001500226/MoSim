import type { Props } from "./action";
import { generateChangelogParams, getPage } from "./action";

export const generateStaticParams = generateChangelogParams;

export async function generateMetadata(props: Props) {
	const { metadata } = await getPage(props);
	return metadata;
}

export default async function Page(props: Props) {
	const { default: MDXContent } = await getPage(props);

	return <MDXContent {...props} params={props.params} />;
}

export const dynamic = "force-static";
