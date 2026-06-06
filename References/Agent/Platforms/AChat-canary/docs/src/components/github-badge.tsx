import IconGithub from "@/components/icons/github";
import { unstable_cache } from "next/cache";

export const GithubMenuBadge = () => (
	<a
		href="https://github.com/achat/vmboard"
		className="group h-8 flex shrink-0 flex-row items-center rounded border border-primary/10 overflow-hidden transition-opacity"
		target="_blank"
		rel="nofollow noreferrer"
		title="GitHub Repository"
	>
		<div className="py-1 px-1 block bg-primary/10">
			<IconGithub className="group-hover:opacity-80 opacity-100 h-6 w-6" />
		</div>
		<div className="py-1 text-center text-sm group-hover:opacity-80 opacity-100 w-10">
			<StarCount repo="achat/vmboard" />
		</div>
	</a>
);

const getStars = async (repo: string) =>
	await unstable_cache(
		async () => {
			const headers = {
				Accept: "application/vnd.github.v3+json",
				// If a GitHub access token is provided in the environment variables, include it in the headers
				Authorization: process.env.GITHUB_ACCESS_TOKEN
					? `token ${process.env.GITHUB_ACCESS_TOKEN}`
					: undefined,
			} as Record<string, string>;

			// Fetch the repository information from GitHub API
			const response = await fetch(`https://api.github.com/repos/${repo}`, {
				headers,
			});

			// If the response is not successful, throw an error
			if (!response.ok) {
				// throw new Error(`GitHub API responded with status: ${response.status}`);
				return {
					stargazersCount: 0,
				}
			}

			// Parse the response data
			const repoData = await response.json();

			return { stargazersCount: repoData.stargazers_count };
		},
		["vmboard-stars", repo],
		{
			revalidate: 60 * 60 * 1, // 1 hours
		},
	)();

export const StarCount: React.FC<{ repo: string }> = async ({ repo }) => {
	const { stargazersCount } = await getStars(repo);
	return stargazersCount ? (
		<span>
			{stargazersCount.toLocaleString("en-US", {
				compactDisplay: "short",
				notation: "compact",
			})}
		</span>
	) : null;
};
