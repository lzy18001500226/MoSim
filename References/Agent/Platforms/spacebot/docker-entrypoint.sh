#!/bin/sh
set -e

mkdir -p "$SPACEBOT_DIR"
mkdir -p "$SPACEBOT_DIR/tools/bin"

# Generate config.toml from environment variables when no config file exists.
# Once a config.toml is present on the volume, this is skipped entirely.
if [ ! -f "$SPACEBOT_DIR/config.toml" ]; then
    cat > "$SPACEBOT_DIR/config.toml" <<EOF
[api]
bind = "::"

[llm]
anthropic_key = "env:ANTHROPIC_API_KEY"
openai_key = "env:OPENAI_API_KEY"
openrouter_key = "env:OPENROUTER_API_KEY"
EOF

    # Discord adapter
    if [ -n "$DISCORD_BOT_TOKEN" ]; then
        cat >> "$SPACEBOT_DIR/config.toml" <<EOF

[messaging.discord]
enabled = true
token = "env:DISCORD_BOT_TOKEN"
EOF
        if [ -n "$DISCORD_DM_ALLOWED_USERS" ]; then
            # Comma-separated user IDs -> TOML array
            DM_ARRAY=$(echo "$DISCORD_DM_ALLOWED_USERS" | sed 's/[[:space:]]//g' | sed 's/,/", "/g')
            cat >> "$SPACEBOT_DIR/config.toml" <<EOF
dm_allowed_users = ["$DM_ARRAY"]
EOF
        fi
    fi

    # Telegram adapter
    if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
        cat >> "$SPACEBOT_DIR/config.toml" <<EOF

[messaging.telegram]
enabled = true
token = "env:TELEGRAM_BOT_TOKEN"
EOF
    fi

    # Webhook adapter
    if [ -n "$WEBHOOK_ENABLED" ]; then
        cat >> "$SPACEBOT_DIR/config.toml" <<EOF

[messaging.webhook]
enabled = true
bind = "0.0.0.0"
EOF
    fi

    # Default agent
    cat >> "$SPACEBOT_DIR/config.toml" <<EOF

[[agents]]
id = "main"
default = true
EOF

    # Discord binding
    if [ -n "$DISCORD_GUILD_ID" ]; then
        cat >> "$SPACEBOT_DIR/config.toml" <<EOF

[[bindings]]
agent_id = "main"
channel = "discord"
guild_id = "$DISCORD_GUILD_ID"
EOF
        if [ -n "$DISCORD_CHANNEL_IDS" ]; then
            CH_ARRAY=$(echo "$DISCORD_CHANNEL_IDS" | sed 's/[[:space:]]//g' | sed 's/,/", "/g')
            cat >> "$SPACEBOT_DIR/config.toml" <<EOF
channel_ids = ["$CH_ARRAY"]
EOF
        fi
        if [ -n "$DISCORD_DM_ALLOWED_USERS" ]; then
            DM_ARRAY=$(echo "$DISCORD_DM_ALLOWED_USERS" | sed 's/[[:space:]]//g' | sed 's/,/", "/g')
            cat >> "$SPACEBOT_DIR/config.toml" <<EOF
dm_allowed_users = ["$DM_ARRAY"]
EOF
        fi
    fi

    # Telegram binding
    if [ -n "$TELEGRAM_CHAT_ID" ]; then
        cat >> "$SPACEBOT_DIR/config.toml" <<EOF

[[bindings]]
agent_id = "main"
channel = "telegram"
chat_id = "$TELEGRAM_CHAT_ID"
EOF
    fi

    echo "Generated config.toml from environment variables"
fi

exec "$@"
