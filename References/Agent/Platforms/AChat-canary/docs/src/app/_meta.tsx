import type { MetaRecord } from "nextra";

export default {
	index: {
		type: "page",
		title: "VMBoard",
		display: "hidden",
		theme: {
			layout: "full",
		},
	},
	docs: {
		type: "page",
		title: "文档",
	},
	pricing: {
		title: "定价",
		type: "page",
		theme: {
			layout: "full",
		},
	},
	sponsor: {
		type: "page",
		title: "赞助",
	},
	changelog: {
		type: "page",
		title: "变更日志",
		theme: {
			breadcrumb: false,
			sidebar: false,
			timestamp: false,
			toc: false,
		},
	},
	forum: {
		type: "page",
		title: "社区论坛",
		href: "https://forum.vmboard.io",
	},
	"self-hosting": {
		type: "page",
		title: "自托管",
		// hidden from main menu via overrides.css, nextra display:hidden otherwise breaks type:page
	},
	showcase: {
		type: "page",
		title: "展示",
		// hidden from main menu via overrides.css, nextra display:hidden otherwise breaks type:page
	},
	faq: {
		type: "page",
		title: "FAQ",
		// hidden from main menu via overrides.css, nextra display:hidden otherwise breaks type:page
	},
	support: {
		type: "page",
		title: "支持",
		display: "hidden",
	},
	// about: {
	//   title: "About us",
	//   type: "page",
	//   display: "hidden",
	//   theme: {
	//     typesetting: "article",
	//     timestamp: false,
	//   },
	// },
	// "404": {
	//   type: "page",
	//   theme: {
	//     typesetting: "article",
	//     timestamp: false,
	//   },
	// },
} satisfies MetaRecord;
