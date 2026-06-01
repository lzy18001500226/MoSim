import FeatureBento from "@/components/landing/feature-bento";
import { Hero } from "@/components/landing/hero";
import OpenSource from "@/components/landing/open-source";

export default function Home() {
	return (
		<main className="relative overflow-hidden w-full">
			<Hero />
			<FeatureBento />
			<OpenSource />
		</main>
	);
}
