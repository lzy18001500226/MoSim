"use client";

import Image from "next/image";
import { useIsClient } from "foxact/use-is-client";

export default function Hits() {
	const isClient = useIsClient();
	if (!isClient) return null;

	return (
		<Image
			unoptimized
			src={`https://hits.aprilnea.com/hits?url=${window.location.href}`}
			alt="Hits"
			width={150}
			height={20}
		/>
	);
}
