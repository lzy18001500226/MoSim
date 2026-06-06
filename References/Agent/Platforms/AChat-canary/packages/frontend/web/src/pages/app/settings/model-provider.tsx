import React from "react";

// Mock data structure based on backend schema
const mockProviders = [
  {
    id: "1",
    providerName: "OpenAI",
    providerType: "llm",
    quotaType: "message_credits",
    quotaLimit: 200,
    quotaUsed: 50,
    isValid: true,
    models: [
      { id: "m1", modelName: "gpt-3.5-turbo", modelType: "llm", isValid: true },
      { id: "m2", modelName: "gpt-4", modelType: "llm", isValid: true },
    ],
  },
  {
    id: "2",
    providerName: "Anthropic",
    providerType: "llm",
    quotaType: "tokens",
    quotaLimit: 0,
    quotaUsed: 0,
    isValid: true,
    models: [
      { id: "m3", modelName: "claude-3", modelType: "llm", isValid: true },
    ],
  },
];

export default function ModelProviderPage() {
  return (
    <div style={{ padding: 24 }}>
      <h2>Model Providers</h2>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 16 }}>
        <thead>
          <tr>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>Provider Name</th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>Type</th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>Quota</th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>Models</th>
          </tr>
        </thead>
        <tbody>
          {mockProviders.map((provider) => (
            <tr key={provider.id}>
              <td style={{ padding: "8px 0" }}>{provider.providerName}</td>
              <td>{provider.providerType}</td>
              <td>
                {provider.quotaType ? `${provider.quotaUsed} / ${provider.quotaLimit} (${provider.quotaType})` : "-"}
              </td>
              <td>
                <ul style={{ margin: 0, paddingLeft: 16 }}>
                  {provider.models.map((model) => (
                    <li key={model.id}>
                      {model.modelName} <span style={{ color: "#888" }}>({model.modelType})</span>
                    </li>
                  ))}
                </ul>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}