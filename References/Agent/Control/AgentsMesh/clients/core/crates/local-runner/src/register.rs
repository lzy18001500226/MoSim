use crate::cli::run_runner_cli;
use crate::error::{LocalRunnerError, Result};
use crate::paths::InstallPaths;

pub async fn is_registered(paths: &InstallPaths) -> bool {
    tokio::fs::metadata(paths.config_file()).await.is_ok()
}

pub async fn local_node_id(paths: &InstallPaths) -> Option<String> {
    let bytes = tokio::fs::read(paths.config_file()).await.ok()?;
    let text = String::from_utf8_lossy(&bytes);
    parse_node_id(&text)
}

fn parse_node_id(yaml: &str) -> Option<String> {
    for line in yaml.lines() {
        let Some(rest) = line.trim_start().strip_prefix("node_id:") else {
            continue;
        };
        let value = rest
            .split('#')
            .next()
            .unwrap_or("")
            .trim()
            .trim_matches(|c| c == '"' || c == '\'');
        if value.is_empty() {
            return None;
        }
        return Some(value.to_string());
    }
    None
}

pub async fn register(paths: &InstallPaths, token: &str, server_url: &str) -> Result<()> {
    if token.is_empty() {
        return Err(LocalRunnerError::InvalidArgument(
            "registration token must not be empty".into(),
        ));
    }
    let mut args: Vec<&str> = vec!["register", "--token", token, "--headless", "--force"];
    if !server_url.is_empty() {
        args.extend(["--server", server_url]);
    }
    run_runner_cli(paths, &args).await?.ok().map(|_| ())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_unquoted_node_id() {
        let yaml = "server_url: https://x\nnode_id: macmini-03\norg_slug: foo\n";
        assert_eq!(parse_node_id(yaml).as_deref(), Some("macmini-03"));
    }

    #[test]
    fn parses_quoted_node_id() {
        let yaml = "node_id: \"my-host\"\n";
        assert_eq!(parse_node_id(yaml).as_deref(), Some("my-host"));
    }

    #[test]
    fn ignores_inline_comment() {
        let yaml = "node_id: foo  # set by register\n";
        assert_eq!(parse_node_id(yaml).as_deref(), Some("foo"));
    }

    #[test]
    fn returns_none_when_missing() {
        assert!(parse_node_id("server_url: x\n").is_none());
    }

    #[test]
    fn returns_none_when_empty() {
        assert!(parse_node_id("node_id: \n").is_none());
    }
}
