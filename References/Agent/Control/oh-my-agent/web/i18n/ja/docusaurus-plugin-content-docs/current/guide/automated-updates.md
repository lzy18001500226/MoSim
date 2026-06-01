---
title: "ガイド：自動更新"
description: oh-my-agent GitHub Actionの完全ドキュメント。セットアップ、全入出力、詳細例、内部動作を解説します。
---

# ガイド：自動更新

## 概要

oh-my-agent GitHub Action（`first-fluke/oma-update-action@v1`）は、CIで`oma update`を実行してプロジェクトのエージェントスキルを自動更新します。PRを作成してレビューするモードと、ブランチに直接コミットするモードをサポート。

---

## クイックセットアップ

`.github/workflows/update-oh-my-agent.yml`として追加：

```yaml
name: Update oh-my-agent

on:
  schedule:
    - cron: '0 9 * * 1'  # 毎週月曜9時UTC
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: first-fluke/oma-update-action@v1
```

---

## 全Action入力

| 入力 | 型 | デフォルト | 説明 |
|:------|:-----|:--------|:-----------|
| `mode` | string | `"pr"` | `"pr"`でPR作成、`"commit"`で直接コミット |
| `base-branch` | string | `"main"` | PRのベースブランチまたはコミット先 |
| `force` | string | `"false"` | `"true"`でカスタム設定を上書き |
| `pr-title` | string | `"chore(deps): update oh-my-agent skills"` | PRタイトル |
| `pr-labels` | string | `"dependencies,automated"` | カンマ区切りラベル |
| `commit-message` | string | `"chore(deps): update oh-my-agent skills"` | コミットメッセージ |
| `token` | string | `${{ github.token }}` | GitHubトークン |

## 全Action出力

| 出力 | 説明 |
|:-------|:-----------|
| `updated` | 変更検出時`"true"` |
| `version` | 更新後のバージョン |
| `pr-number` | PR番号（prモード） |
| `pr-url` | PR URL（prモード） |

---

## 詳細例

### 例1：デフォルトPRモード

```yaml
- uses: first-fluke/oma-update-action@v1
  id: update
- name: Summary
  if: steps.update.outputs.updated == 'true'
  run: echo "Updated to v${{ steps.update.outputs.version }}"
```

### 例2：直接コミット + PAT

```yaml
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.OH_MY_AGENT_PAT }}
- uses: first-fluke/oma-update-action@v1
  with:
    mode: commit
    token: ${{ secrets.OH_MY_AGENT_PAT }}
    base-branch: develop
```

### 例3：Slack通知付き

```yaml
- uses: first-fluke/oma-update-action@v1
  id: update
- name: Notify Slack
  if: steps.update.outputs.updated == 'true'
  uses: slackapi/slack-github-action@v2
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK }}
    webhook-type: incoming-webhook
    payload: |
      {"text": "oh-my-agent updated to v${{ steps.update.outputs.version }}"}
```

### 例4：強制更新

```yaml
- uses: first-fluke/oma-update-action@v1
  with:
    force: 'true'
    pr-title: "chore(deps): force-update oh-my-agent skills (reset configs)"
```

**注意：** forceモードは`oma-config.yaml`、`mcp.json`、`stack/`を上書きします。

---

## 内部動作

このActionは`action/action.yml`で定義された[Composite Action](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)です。次の4ステップを実行します。

### Step 1：Bunのセットアップ

```yaml
- uses: oven-sh/setup-bun@v2
```

oh-my-agent CLIの実行に必要なBunランタイムをインストールします。

### Step 2：oh-my-agentのインストール

```bash
bun install -g oh-my-agent
```

npmレジストリからCLIをグローバルインストールします。これにより`oma`コマンドが利用可能になります。

### Step 3：oma updateの実行

```bash
FLAGS="--ci"
if [ "${{ inputs.force }}" = "true" ]; then
  FLAGS="$FLAGS --force"
fi
oma update $FLAGS
```

`--ci`フラグは更新を非インタラクティブモードで実行します（プロンプトをすべてスキップし、スピナーアニメーションの代わりにプレーンテキストを出力）。`--force`フラグを有効にすると、ユーザーがカスタマイズした設定ファイルを上書きします。

`oma update --ci`の内部処理：

1. メインブランチから`prompt-manifest.json`を取得して最新バージョン番号を確認
2. `.agents/skills/_version.json`のローカルバージョンと比較
3. バージョンが一致する場合、「Already up to date.」で終了
4. 新しいバージョンが利用可能な場合、最新tarballをダウンロードして展開
5. ユーザーがカスタマイズしたファイルを保持（`--force`が指定されていない限り）：`oma-config.yaml`、`mcp.json`、`stack/`ディレクトリ
6. 既存の`.agents/`ディレクトリ上に新規ファイルをコピー
7. 保持していたファイルを復元
8. すべてのベンダー向けにベンダー適応（フック、設定、エージェント定義）を更新
9. CLIシンボリックリンクをリフレッシュ

### Step 4：変更の確認

```bash
if [ -n "$(git status --porcelain .agents/ .claude/ 2>/dev/null)" ]; then
  echo "updated=true" >> "$GITHUB_OUTPUT"
  VERSION=$(jq -r '.version' .agents/skills/_version.json)
  echo "version=$VERSION" >> "$GITHUB_OUTPUT"
else
  echo "updated=false" >> "$GITHUB_OUTPUT"
fi
```

`oma update`が`.agents/`または`.claude/`内のファイルを実際に変更したかどうかを確認します。`updated`と`version`の出力をそれに応じて設定します。

その後、`mode`入力に応じて以下が実行されます。

- **`pr`モード：** `peter-evans/create-pull-request@v8`を使い、`chore/update-oh-my-agent`ブランチでPRを作成します。PRには新バージョン番号、oh-my-agentリポジトリへのリンク、設定されたラベルが含まれます。ブランチがすでに存在する場合（前回未クローズのPRから）、既存のPRを更新します。

- **`commit`モード：** Gitを`github-actions[bot]`として設定し、`.agents/`と`.claude/`をステージングし、設定されたメッセージでコミットしてベースブランチにプッシュします。
