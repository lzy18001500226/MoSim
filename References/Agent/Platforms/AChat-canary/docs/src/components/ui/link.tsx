import { cn } from "@/lib/utils";
import { Anchor } from "nextra/components";

const linkClassName = cn(
	"x:text-xs x:font-medium x:transition",
	"x:text-gray-600 x:dark:text-gray-400",
	"x:hover:text-gray-800 x:dark:hover:text-gray-200",
	"x:contrast-more:text-gray-700 x:contrast-more:dark:text-gray-100",
);

export function ForumLink({
	href,
	children,
	...props
}: React.AnchorHTMLAttributes<HTMLAnchorElement>) {
	return (
		<Anchor href={href} className={linkClassName} {...props}>
			{children}
		</Anchor>
	);
}
