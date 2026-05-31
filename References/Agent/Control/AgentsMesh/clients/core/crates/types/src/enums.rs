use serde::{Deserialize, Serialize};

macro_rules! status_enum {
    ($(#[$meta:meta])* $vis:vis enum $Name:ident { $($Variant:ident => $str:literal),+ $(,)? }) => {
        $(#[$meta])*
        #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
        #[serde(rename_all = "snake_case")]
        $vis enum $Name {
            $($Variant,)+
            #[serde(other)]
            Unknown,
        }

        impl std::fmt::Display for $Name {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                f.write_str(match self { $(Self::$Variant => $str,)+ Self::Unknown => "unknown" })
            }
        }
    };
}

status_enum! {
    pub enum PodStatus {
        Pending => "pending",
        Creating => "creating",
        Initializing => "initializing",
        Running => "running",
        Paused => "paused",
        Stopping => "stopping",
        Disconnected => "disconnected",
        Orphaned => "orphaned",
        Completed => "completed",
        Terminated => "terminated",
        Error => "error",
        Failed => "failed",
    }
}
impl Default for PodStatus { fn default() -> Self { Self::Pending } }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pod_status_serde_roundtrip() {
        assert_eq!(serde_json::to_string(&PodStatus::Running).unwrap(), "\"running\"");
        assert_eq!(serde_json::from_str::<PodStatus>("\"running\"").unwrap(), PodStatus::Running);
        assert_eq!(serde_json::from_str::<PodStatus>("\"creating\"").unwrap(), PodStatus::Creating);
    }

    #[test]
    fn pod_status_unknown_fallback() {
        assert_eq!(serde_json::from_str::<PodStatus>("\"something_new\"").unwrap(), PodStatus::Unknown);
    }

    #[test]
    fn display_matches_serde() {
        assert_eq!(PodStatus::Running.to_string(), "running");
    }

    #[test]
    fn default_values() {
        assert_eq!(PodStatus::default(), PodStatus::Pending);
    }
}
