"use client";

import type React from "react";
import { forwardRef, useRef } from "react";
import { AlibabaCloud, Aws, Azure, Baidu, TencentCloud } from "@lobehub/icons";
import { cn } from "@/lib/utils";
import { AnimatedBeam } from "@/components/magicui/animated-beam";
import GCPIcon from "../icons/gcp";
import Logo from "../icons/logo";
import { UserIcon } from "lucide-react";

const Circle = forwardRef<
	HTMLDivElement,
	{ className?: string; children?: React.ReactNode }
>(({ className, children }, ref) => {
	return (
		<div
			ref={ref}
			className={cn(
				"z-10 flex size-12 items-center justify-center rounded-full border-2 bg-white p-3 shadow-[0_0_20px_-12px_rgba(0,0,0,0.8)]",
				className,
			)}
		>
			{children}
		</div>
	);
});

Circle.displayName = "Circle";

export default function FeatureIntegrations({
	className,
}: {
	className?: string;
}) {
	const containerRef = useRef<HTMLDivElement>(null);
	const startRef = useRef<HTMLDivElement>(null);
	const middleRef = useRef<HTMLDivElement>(null);
	const div1Ref = useRef<HTMLDivElement>(null);
	const div2Ref = useRef<HTMLDivElement>(null);
	const div3Ref = useRef<HTMLDivElement>(null);
	const div4Ref = useRef<HTMLDivElement>(null);
	const div5Ref = useRef<HTMLDivElement>(null);

	return (
		<div
			className={cn(
				"relative flex h-[500px] w-full items-center justify-center overflow-hidden p-10",
				className,
			)}
			ref={containerRef}
		>
			<div className="flex size-full max-w-lg flex-row items-stretch justify-between gap-10">
				<div className="flex flex-col justify-center">
					<Circle ref={startRef}>
						<UserIcon />
					</Circle>
				</div>
				<div className="flex flex-col justify-center">
					<Circle ref={middleRef} className="size-16">
						<Logo width={48} height={48} />
					</Circle>
				</div>
				<div className="flex flex-col justify-center gap-2">
					<Circle ref={div1Ref}>
						<Aws.Color />
					</Circle>
					<Circle ref={div2Ref}>
						<GCPIcon />
					</Circle>
					<Circle ref={div3Ref}>
						<Azure.Color />
					</Circle>
					<Circle ref={div4Ref}>
						<TencentCloud.Color />
					</Circle>
					<Circle ref={div5Ref}>
						<AlibabaCloud.Color />
					</Circle>
				</div>
			</div>

			{/* AnimatedBeams */}
			<AnimatedBeam
				containerRef={containerRef}
				fromRef={startRef}
				toRef={middleRef}
				duration={5}
			/>
			<AnimatedBeam
				containerRef={containerRef}
				fromRef={div1Ref}
				toRef={middleRef}
				duration={5}
				reverse
			/>
			<AnimatedBeam
				containerRef={containerRef}
				fromRef={div2Ref}
				toRef={middleRef}
				duration={5}
				reverse
			/>
			<AnimatedBeam
				containerRef={containerRef}
				fromRef={div3Ref}
				toRef={middleRef}
				duration={5}
				reverse
			/>
			<AnimatedBeam
				containerRef={containerRef}
				fromRef={div4Ref}
				toRef={middleRef}
				duration={5}
				reverse
			/>
			<AnimatedBeam
				containerRef={containerRef}
				fromRef={div5Ref}
				toRef={middleRef}
				duration={5}
				reverse
			/>
		</div>
	);
}
