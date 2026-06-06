use schemars::JsonSchema;
use serde::{Deserialize, Deserializer, Serialize};

fn any_to_string(value: serde_json::Value) -> String {
    match value {
        serde_json::Value::Null => String::new(),
        serde_json::Value::String(s) => s,
        serde_json::Value::Bool(v) => v.to_string(),
        serde_json::Value::Number(v) => v.to_string(),
        serde_json::Value::Array(v) => serde_json::to_string(&v).unwrap_or_default(),
        serde_json::Value::Object(v) => serde_json::to_string(&v).unwrap_or_default(),
    }
}

fn deserialize_string_lenient<'de, D>(deserializer: D) -> Result<String, D::Error>
where
    D: Deserializer<'de>,
{
    let value = serde_json::Value::deserialize(deserializer)?;
    Ok(any_to_string(value))
}

fn deserialize_u8_lenient<'de, D>(deserializer: D) -> Result<u8, D::Error>
where
    D: Deserializer<'de>,
{
    let value = serde_json::Value::deserialize(deserializer)?;
    let parsed = match value {
        serde_json::Value::Number(n) => n.as_u64().map(|v| v as i64).unwrap_or(0),
        serde_json::Value::String(s) => s.parse::<i64>().unwrap_or(0),
        serde_json::Value::Bool(v) => {
            if v {
                1
            } else {
                0
            }
        }
        _ => 0,
    };

    Ok(parsed.clamp(0, u8::MAX as i64) as u8)
}

fn deserialize_vec_string_lenient<'de, D>(deserializer: D) -> Result<Vec<String>, D::Error>
where
    D: Deserializer<'de>,
{
    let value = serde_json::Value::deserialize(deserializer)?;

    match value {
        serde_json::Value::Null => Ok(Vec::new()),
        serde_json::Value::Array(items) => Ok(items
            .into_iter()
            .map(any_to_string)
            .filter(|item| !item.trim().is_empty())
            .collect()),
        other => {
            let single = any_to_string(other);
            if single.trim().is_empty() {
                Ok(Vec::new())
            } else {
                Ok(vec![single])
            }
        }
    }
}

fn deserialize_dependency_type_lenient<'de, D>(deserializer: D) -> Result<DependencyType, D::Error>
where
    D: Deserializer<'de>,
{
    let value = serde_json::Value::deserialize(deserializer)?;
    Ok(DependencyType::map_from_raw(&any_to_string(value)))
}

fn deserialize_opt_string_lenient<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
where
    D: Deserializer<'de>,
{
    let value = serde_json::Value::deserialize(deserializer)?;
    if value.is_null() {
        return Ok(None);
    }

    let text = any_to_string(value);
    if text.trim().is_empty() {
        Ok(None)
    } else {
        Ok(Some(text))
    }
}

/// Streamlined relationship analysis result
#[derive(Debug, Serialize, Deserialize, Clone, JsonSchema, Default)]
#[serde(default)]
pub struct RelationshipAnalysis {
    /// Core dependency relationships (only keep important ones)
    #[serde(
        default,
        deserialize_with = "deserialize_vec_core_dependencies_lenient"
    )]
    pub core_dependencies: Vec<CoreDependency>,

    /// Architecture layer information
    #[serde(
        default,
        deserialize_with = "deserialize_vec_architecture_layers_lenient"
    )]
    pub architecture_layers: Vec<ArchitectureLayer>,

    /// Key issues and recommendations
    #[serde(default, deserialize_with = "deserialize_vec_string_lenient")]
    pub key_insights: Vec<String>,
}

fn deserialize_vec_core_dependencies_lenient<'de, D>(
    deserializer: D,
) -> Result<Vec<CoreDependency>, D::Error>
where
    D: Deserializer<'de>,
{
    let value = serde_json::Value::deserialize(deserializer)?;

    match value {
        serde_json::Value::Null => Ok(Vec::new()),
        serde_json::Value::Array(items) => {
            let mut out = Vec::new();
            for item in items {
                if let Ok(parsed) = serde_json::from_value::<CoreDependency>(item) {
                    out.push(parsed);
                }
            }
            Ok(out)
        }
        serde_json::Value::Object(map) => {
            let parsed = serde_json::from_value::<CoreDependency>(serde_json::Value::Object(map));
            Ok(parsed.into_iter().collect())
        }
        _ => Ok(Vec::new()),
    }
}

fn deserialize_vec_architecture_layers_lenient<'de, D>(
    deserializer: D,
) -> Result<Vec<ArchitectureLayer>, D::Error>
where
    D: Deserializer<'de>,
{
    let value = serde_json::Value::deserialize(deserializer)?;

    match value {
        serde_json::Value::Null => Ok(Vec::new()),
        serde_json::Value::Array(items) => {
            let mut out = Vec::new();
            for item in items {
                if let Ok(parsed) = serde_json::from_value::<ArchitectureLayer>(item) {
                    out.push(parsed);
                }
            }
            Ok(out)
        }
        serde_json::Value::Object(map) => {
            let parsed =
                serde_json::from_value::<ArchitectureLayer>(serde_json::Value::Object(map));
            Ok(parsed.into_iter().collect())
        }
        _ => Ok(Vec::new()),
    }
}

/// Core dependency (simplified version)
#[derive(Debug, Serialize, Deserialize, Clone, JsonSchema, Default)]
#[serde(default)]
pub struct CoreDependency {
    /// Source component
    #[serde(default, deserialize_with = "deserialize_string_lenient")]
    pub from: String,

    /// Target component
    #[serde(default, deserialize_with = "deserialize_string_lenient")]
    pub to: String,

    /// Dependency type
    #[serde(default, deserialize_with = "deserialize_dependency_type_lenient")]
    pub dependency_type: DependencyType,

    /// Importance score (1-5, only keep important ones)
    #[serde(default, deserialize_with = "deserialize_u8_lenient")]
    pub importance: u8,

    /// Brief description
    #[serde(default, deserialize_with = "deserialize_opt_string_lenient")]
    pub description: Option<String>,
}

/// Architecture layer
#[derive(Debug, Serialize, Deserialize, Clone, JsonSchema, Default)]
#[serde(default)]
pub struct ArchitectureLayer {
    /// Layer name
    #[serde(default, deserialize_with = "deserialize_string_lenient")]
    pub name: String,

    /// Components in this layer
    #[serde(default, deserialize_with = "deserialize_vec_string_lenient")]
    pub components: Vec<String>,

    /// Layer level (smaller number means lower level)
    #[serde(default, deserialize_with = "deserialize_u8_lenient")]
    pub level: u8,
}

/// Dependency type enumeration
#[derive(Debug, Serialize, Deserialize, Clone, JsonSchema)]
pub enum DependencyType {
    /// Import dependency (use, import statements)
    Import,
    /// Function call dependency
    FunctionCall,
    /// Inheritance relationship
    Inheritance,
    /// Composition relationship
    Composition,
    /// Data flow dependency
    DataFlow,
    /// Module dependency
    Module,
}

impl Default for DependencyType {
    fn default() -> Self {
        Self::Module
    }
}

impl DependencyType {
    pub fn map_from_raw(raw: &str) -> Self {
        let normalized = raw.trim().to_lowercase();

        if normalized.contains("import") || normalized == "use" {
            return Self::Import;
        }
        if normalized.contains("function") || normalized.contains("call") {
            return Self::FunctionCall;
        }
        if normalized.contains("inherit") || normalized.contains("extend") {
            return Self::Inheritance;
        }
        if normalized.contains("composition") || normalized.contains("compose") {
            return Self::Composition;
        }
        if normalized.contains("data") && normalized.contains("flow") {
            return Self::DataFlow;
        }
        if normalized.contains("module") || normalized.contains("dependency") {
            return Self::Module;
        }

        match normalized.as_str() {
            "import" => Self::Import,
            "functioncall" => Self::FunctionCall,
            "function_call" => Self::FunctionCall,
            "inheritance" => Self::Inheritance,
            "composition" => Self::Composition,
            "dataflow" => Self::DataFlow,
            "data_flow" => Self::DataFlow,
            "module" => Self::Module,
            _ => Self::Module,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            DependencyType::Import => "import",
            DependencyType::FunctionCall => "function_call",
            DependencyType::Inheritance => "inheritance",
            DependencyType::Composition => "composition",
            DependencyType::DataFlow => "data_flow",
            DependencyType::Module => "module",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{DependencyType, RelationshipAnalysis};

    #[test]
    fn test_relationship_analysis_deserialize_lenient_mixed_types() {
        let payload = serde_json::json!({
            "core_dependencies": [
                {
                    "from": {"module": "reader"},
                    "to": "cache",
                    "dependency_type": "function call",
                    "importance": "4",
                    "description": {"summary": "reader uses cache"}
                },
                "invalid-entry"
            ],
            "architecture_layers": [
                {
                    "name": 101,
                    "components": "reader",
                    "level": "2"
                }
            ],
            "key_insights": ["good", {"note": "check cycle"}]
        });

        let parsed: RelationshipAnalysis =
            serde_json::from_value(payload).expect("should deserialize lenient relationship data");

        assert_eq!(parsed.core_dependencies.len(), 1);
        assert_eq!(
            parsed.core_dependencies[0].dependency_type.as_str(),
            "function_call"
        );
        assert_eq!(parsed.core_dependencies[0].importance, 4);
        assert_eq!(parsed.architecture_layers.len(), 1);
        assert_eq!(parsed.architecture_layers[0].level, 2);
        assert_eq!(parsed.key_insights.len(), 2);
    }

    #[test]
    fn test_dependency_type_map_from_unknown_defaults_to_module() {
        assert!(matches!(
            DependencyType::map_from_raw("strange-link-type"),
            DependencyType::Module
        ));
    }
}
