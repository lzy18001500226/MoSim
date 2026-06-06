import { CalendarIcon, FileTextIcon } from "@radix-ui/react-icons";
import { BellIcon, ServerIcon, Share2Icon } from "lucide-react";

import { Calendar } from "@/components/ui/calendar";
import { cn } from "@/lib/utils";
import FeatureIntegrations from "./feature-integrations";
import FeatureNotification from "./feature-notification";
import { BentoCard, BentoGrid } from "@/components/magicui/bento-grid";
import { Marquee } from "@/components/magicui/marquee";
import { Header } from "./header";
import { HomeSection } from "./home-section";

const files = [
	{
		name: "LAX.EB.WEE",
		body: "39.9 USD/年 -> ¥24.08/月，¥288.98/年	1	1G	20G	1T (In+Out)	1Gbps	活动款，不定期补货",
	},
	{
		name: "HKG.EB.TINYv2",
		body: "29.9 USD/月 -> ¥216.29/月，¥2595.53/年	1	1G	20G	1T (In+Out)	1Gbps",
	},
	{
		name: "TYO.Pro.Shinagawa",
		body: "199.99 USD/年 -> ¥120.56/月，¥1446.71/年	1	2G	60G	500G (In+Out)	500Mbps	活动款，不定期补货",
	},
	{
		name: "LAX.Pro.PalmSpring",
		body: "100 USD/年 -> ¥60.36/月，¥724.27/年	2	2G	40G	2T (In+Out)	2Gbps	活动款，不定期补货",
	},
	{
		name: "LAX.sPro.Fixed",
		body: "139 USD/年 -> ¥83.89/月，¥1006.74/年	2	2G	40G	1T (In+Out)	300Mbps	活动款，不定期补货",
	},
];

const features = [
	{
		Icon: ServerIcon,
		name: "监控主机",
		description: "服务器，虚拟机，容器，都可以监控。",
		href: "#",
		cta: "Learn more",
		className: "col-span-3 lg:col-span-1",
		background: (
			<Marquee
				pauseOnHover
				className="absolute top-10 [--duration:20s] [mask-image:linear-gradient(to_top,transparent_40%,#000_100%)] "
			>
				{files.map((f) => (
					<figure
						key={f.name}
						className={cn(
							"relative w-32 cursor-pointer overflow-hidden rounded-xl border p-4",
							"border-gray-950/[.1] bg-gray-950/[.01] hover:bg-gray-950/[.05]",
							"dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15]",
							"transform-gpu blur-[1px] transition-all duration-300 ease-out hover:blur-none",
						)}
					>
						<div className="flex flex-row items-center gap-2">
							<div className="flex flex-col">
								<figcaption className="text-sm font-medium dark:text-white ">
									{f.name}
								</figcaption>
							</div>
						</div>
						<blockquote className="mt-2 text-xs">{f.body}</blockquote>
					</figure>
				))}
			</Marquee>
		),
	},
	{
		Icon: BellIcon,
		name: "通知",
		description: "配合报警规则，任何动静，随时知晓。",
		href: "#",
		cta: "Learn more",
		className: "col-span-3 lg:col-span-2",
		background: (
			<FeatureNotification className="absolute right-2 top-4 h-[300px] w-full scale-75 border-none transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_100%)] group-hover:scale-90" />
		),
	},
	{
		Icon: Share2Icon,
		name: "集成",
		description: "支持各大知名主机商，并持续增加中。",
		href: "#",
		cta: "Learn more",
		className: "col-span-3 lg:col-span-2",
		background: (
			<FeatureIntegrations className="absolute right-2 top-4 h-[300px] border-none transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_100%)] group-hover:scale-105" />
		),
	},
	{
		Icon: CalendarIcon,
		name: "Calendar",
		description: "Use the calendar to filter your server by date.",
		className: "col-span-3 lg:col-span-1",
		href: "#",
		cta: "Learn more",
		background: (
			<Calendar
				mode="single"
				selected={new Date(2022, 4, 11, 0, 0, 0)}
				className="absolute right-0 top-10 origin-top scale-75 rounded-md border transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_40%,#000_100%)] group-hover:scale-90"
			/>
		),
	},
];

export default function FeatureBento() {
	return (
		<HomeSection>
			<Header
				title="管理主机，一应俱全"
				description="监控，报警，集成，应有尽有。"
				buttons={[{ href: "/docs", text: "探索文档" }]}
			/>
			<BentoGrid>
				{features.map((feature) => (
					<BentoCard key={feature.name} {...feature} />
				))}
			</BentoGrid>
		</HomeSection>
	);
}
