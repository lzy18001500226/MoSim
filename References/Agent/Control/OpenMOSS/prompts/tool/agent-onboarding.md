# Agent 首次注册指南

> 本文档指导 OpenClaw Agent 完成首次注册，获取 API Key 并保存到自己的 SKILL.md 中。
> 每个 Agent 只需执行一次。

---

## 前置条件

- 任务调度服务已启动
- 你有注册令牌（Registration Token），由管理员提供
- 你已知道自己的角色：`planner` / `executor` / `reviewer` / `patrol`

## 注册步骤

### 1. 注册自己

在你的 Skill 目录下运行：

```bash
python task-cli.py register --name "你的中文名称" --role <你的角色> --token <注册令牌> --description "你的专业能力描述"
```

> ⚠️ **请使用自己的中文名注册**（如"AI小吴"、"AI酱瓜"），方便团队成员识别和协作。

示例：

```bash
python task-cli.py register --name "AI小吴" --role executor --token openclaw-register-2024 --description "专业资讯搜集员，擅长中文互联网信息检索"
```

注册成功后，终端会输出你的 Agent ID 和 API Key：

```
✅ 注册成功
   Agent ID:  a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   API Key:   ock_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   角色:      executor

⚠️ 请立即将 API Key 保存到你的 SKILL.md 中！
```

### 2. 保存 API Key 到 SKILL.md

打开你的 SKILL.md 文件，在 `## 认证信息` 部分填入 API Key：

```markdown
## 认证信息

- API_KEY: `ock_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
```

> **重要**：API Key 只在注册时显示一次，请务必立即保存。如果遗失，需要联系管理员重置。

### 3. 验证注册并了解职责

```bash
python task-cli.py --key ock_xxxxxxxx rules
```

如果返回规则内容，说明注册成功且 Key 有效。

> 你的详细职责已写在角色提示词中（`prompts/task-{role}.md`），每次唤醒时通过 `rules` 命令获取最新规则即可。

## 之后的使用

注册完成后，每次执行命令时带上你的 Key：

```bash
python task-cli.py --key <你的API_KEY> <命令> [参数]
```

你的 SKILL.md 文档中已列出了你角色可用的所有命令，按文档操作即可。

## 常见问题

| 问题               | 解决方案                                                |
| ------------------ | ------------------------------------------------------- |
| 注册令牌无效       | 联系管理员确认令牌是否正确                              |
| API Key 丢失       | 联系管理员通过 `POST /admin/agents/{id}/reset-key` 重置 |
| 注册时提示名称重复 | 更换一个唯一的名称                                      |
