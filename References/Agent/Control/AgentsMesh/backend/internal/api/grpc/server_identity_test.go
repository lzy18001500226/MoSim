package grpc

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"google.golang.org/grpc/metadata"
)

func TestExtractClientIdentity(t *testing.T) {
	tests := []struct {
		name        string
		metadata    map[string]string
		wantErr     bool
		errContains string
		checkFunc   func(t *testing.T, identity *ClientIdentity)
	}{
		{
			name: "valid identity with RFC 2253 DN format",
			metadata: map[string]string{
				MetadataKeyClientCertDN:          "CN=test-node-123,O=AgentsMesh,OU=Runner",
				MetadataKeyOrgSlug:               "test-org",
				MetadataKeyClientCertSerial:      "ABCD1234",
				MetadataKeyClientCertFingerprint: "sha256:xyz",
				MetadataKeyRealIP:                "192.168.1.100",
			},
			wantErr: false,
			checkFunc: func(t *testing.T, identity *ClientIdentity) {
				assert.Equal(t, "test-node-123", identity.NodeID)
				assert.Equal(t, "test-org", identity.OrgSlug)
				assert.Equal(t, "ABCD1234", identity.CertSerialNumber)
				assert.Equal(t, "sha256:xyz", identity.CertFingerprint)
				assert.Equal(t, "192.168.1.100", identity.RealIP)
			},
		},
		{
			name: "valid identity with OpenSSL DN format",
			metadata: map[string]string{
				MetadataKeyClientCertDN: "/CN=test-node-456/O=AgentsMesh/OU=Runner",
				MetadataKeyOrgSlug:      "test-org",
			},
			wantErr: false,
			checkFunc: func(t *testing.T, identity *ClientIdentity) {
				assert.Equal(t, "test-node-456", identity.NodeID)
				assert.Equal(t, "test-org", identity.OrgSlug)
			},
		},
		{
			name: "missing node_id (empty DN)",
			metadata: map[string]string{
				MetadataKeyOrgSlug: "test-org",
			},
			wantErr:     true,
			errContains: "missing client certificate CN",
		},
		{
			name: "missing org_slug",
			metadata: map[string]string{
				MetadataKeyClientCertDN: "CN=test-node",
			},
			wantErr:     true,
			errContains: "missing org slug",
		},
		{
			name: "minimal valid identity",
			metadata: map[string]string{
				MetadataKeyClientCertDN: "CN=test-node",
				MetadataKeyOrgSlug:      "test-org",
			},
			wantErr: false,
			checkFunc: func(t *testing.T, identity *ClientIdentity) {
				assert.Equal(t, "test-node", identity.NodeID)
				assert.Equal(t, "test-org", identity.OrgSlug)
				assert.Empty(t, identity.CertSerialNumber)
				assert.Empty(t, identity.CertFingerprint)
				assert.Empty(t, identity.RealIP)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create context with metadata
			md := metadata.New(tt.metadata)
			ctx := metadata.NewIncomingContext(context.Background(), md)

			identity, err := ExtractClientIdentity(ctx)

			if tt.wantErr {
				require.Error(t, err)
				if tt.errContains != "" {
					assert.Contains(t, err.Error(), tt.errContains)
				}
				return
			}

			require.NoError(t, err)
			require.NotNil(t, identity)
			if tt.checkFunc != nil {
				tt.checkFunc(t, identity)
			}
		})
	}
}

func TestExtractClientIdentity_NoMetadata(t *testing.T) {
	ctx := context.Background()

	_, err := ExtractClientIdentity(ctx)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "no metadata in context")
}
