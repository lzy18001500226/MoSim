import { useEffect, useState } from "react";
import { formatDuration } from "@/lib/format";

/** Ticking duration display that updates every second while the component is mounted. */
export function LiveDuration({ startMs }: { startMs: number }) {
	const [now, setNow] = useState(Date.now());

	useEffect(() => {
		const interval = setInterval(() => setNow(Date.now()), 1000);
		return () => clearInterval(interval);
	}, []);

	const seconds = Math.floor((now - startMs) / 1000);
	return <span>{formatDuration(seconds)}</span>;
}
