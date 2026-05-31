package extension

import "encoding/json"

type RegistryResponse struct {
	Servers  []RegistryServerEntry `json:"servers"`
	Metadata RegistryMetadata      `json:"metadata"`
}

type RegistryServerEntry struct {
	Server RegistryServer  `json:"server"`
	Meta   json.RawMessage `json:"_meta"`
}

type RegistryServer struct {
	Name        string              `json:"name"`
	Description string              `json:"description"`
	Title       string              `json:"title"`
	Version     string              `json:"version"`
	WebsiteURL  string              `json:"websiteUrl"`
	Repository  *RegistryRepository `json:"repository"`
	Packages    []RegistryPackage   `json:"packages"`
	Remotes     []RegistryRemote    `json:"remotes"`
}

type RegistryRepository struct {
	URL       string `json:"url"`
	Source    string `json:"source"`
	Subfolder string `json:"subfolder"`
}

type RegistryPackage struct {
	RegistryType         string            `json:"registryType"`
	Identifier           string            `json:"identifier"`
	Version              string            `json:"version"`
	Transport            RegistryTransport `json:"transport"`
	EnvironmentVariables []RegistryEnvVar  `json:"environmentVariables"`
}

type RegistryRemote struct {
	Type    string           `json:"type"`
	URL     string           `json:"url"`
	Headers []RegistryHeader `json:"headers"`
}

type RegistryTransport struct {
	Type string `json:"type"`
}

type RegistryEnvVar struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	IsRequired  bool   `json:"isRequired"`
	IsSecret    bool   `json:"isSecret"`
	Default     string `json:"default,omitempty"`
	Format      string `json:"format,omitempty"`
}

type RegistryHeader struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Value       string `json:"value,omitempty"`
	IsRequired  bool   `json:"isRequired"`
	IsSecret    bool   `json:"isSecret"`
}

type RegistryMetadata struct {
	NextCursor string `json:"nextCursor"`
	Count      int    `json:"count"`
}

type RegistryOfficialMeta struct {
	Status      string `json:"status"`
	PublishedAt string `json:"publishedAt"`
	UpdatedAt   string `json:"updatedAt"`
	IsLatest    bool   `json:"isLatest"`
}
