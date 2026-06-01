import { generateStaticParamsFor, importPage } from "nextra/pages";

export type Props = {
	params: Promise<{
		mdxPath: string[];
	}>;
};

export const getPage = async (props: Props) => {
	const params = await props.params;
	const mdxPath = params.mdxPath ?? [];
	const result = await importPage(mdxPath);
	// const result = await importPage([mergeParams(mdxPath)]);
	return result;
};

// export const splitParams = (name: string): string[] => {
// 	return name.split("-", 3);
// };

// export const mergeParams = (params: string[]): string => {
// 	return params.length > 1 ? params.join("-") : params[0];
// };

export const generateChangelogParams = async () => {
	const params = await generateStaticParamsFor("mdxPath")();
	return params;
	// return params.map(({ mdxPath: param }) => {
	// 	if (param[0] === "")
	// 		return {
	// 			mdxPath: param,
	// 		};
	// 	return {
	// 		mdxPath: splitParams(param[0]),
	// 	};
	// });
};
