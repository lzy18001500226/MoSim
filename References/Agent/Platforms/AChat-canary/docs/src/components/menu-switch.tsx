"use client";

import { CircleHelp, Server } from "lucide-react";
import { FileCode } from "lucide-react";
import { LibraryBig } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

export const MenuSwitcher = () => {
	const pathname = usePathname();
	return (
		<div className="-mx-2 hidden md:block">
			{[
				{ title: "使用文档", path: "/docs", Icon: LibraryBig },
				{ title: "自建部署", path: "/self-hosting", Icon: Server },
				{ title: "用户展示", path: "/showcase", Icon: FileCode },
				{ title: "常见问题", path: "/faq", Icon: CircleHelp },
			].map((item) =>
				pathname.startsWith(item.path) ? (
					<div
						key={item.path}
						className="group mb-3 flex flex-row items-center gap-3 x:text-primary-800 dark:x:text-primary-600"
					>
						<item.Icon className="w-7 h-7 p-1 border rounded x:bg-primary-100 dark:x:bg-primary-400/10" />
						{item.title}
					</div>
				) : (
					<Link
						href={item.path}
						key={item.path}
						className="group mb-3 flex flex-row items-center gap-3 x:text-gray-500 hover:x:text-primary/100"
					>
						<item.Icon className="w-7 h-7 p-1 border rounded group-hover:x:bg-border/30" />
						{item.title}
					</Link>
				),
			)}
		</div>
	);
};
