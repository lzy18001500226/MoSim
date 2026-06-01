import { MenuSwitcher } from "@/components/menu-switch";
import { MetaRecord } from "nextra";

export default {
	"-- Switcher": {
		type: "separator",
		title: <MenuSwitcher />,
	},
	index: "概述",
	install: "安装探针",
	// mobile: "移动端",
	"-- Features": {
		type: "separator",
		title: "功能",
	},
	manage: "主机管理",
	metrics: "指标监控",
	analysis: "数据分析",
	alert: "报警规则",
	webpage: "页面分享",
	import: "迁移导入",
	"-- Develop": {
		type: "separator",
		title: "开发",
	},
	architecture: "系统架构",
	develop: "本地开发",
	"-- More": {
		type: "separator",
		title: "更多",
	},
	roadmap: "路线图",
	"open-source": "开源",
	support: {
		href: "/support",
		title: "支持",
	},
} satisfies MetaRecord;
