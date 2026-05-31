package grpc

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"google.golang.org/grpc"
)

func TestLoggingUnaryInterceptor(t *testing.T) {
	logger := newTestLogger()
	interceptor := loggingUnaryInterceptor(logger)

	// Create mock handler
	handlerCalled := false
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		handlerCalled = true
		return "response", nil
	}

	// Create mock server info
	info := &grpc.UnaryServerInfo{
		FullMethod: "/test.Service/Method",
	}

	// Call interceptor
	resp, err := interceptor(context.Background(), "request", info, handler)

	require.NoError(t, err)
	assert.True(t, handlerCalled)
	assert.Equal(t, "response", resp)
}

func TestLoggingStreamInterceptor(t *testing.T) {
	logger := newTestLogger()
	interceptor := loggingStreamInterceptor(logger)

	// Create mock handler
	handlerCalled := false
	handler := func(srv interface{}, stream grpc.ServerStream) error {
		handlerCalled = true
		return nil
	}

	// Create mock server info
	info := &grpc.StreamServerInfo{
		FullMethod: "/test.Service/StreamMethod",
	}

	// Call interceptor
	err := interceptor("server", nil, info, handler)

	require.NoError(t, err)
	assert.True(t, handlerCalled)
}

func TestExtractCNFromDN_EdgeCases(t *testing.T) {
	tests := []struct {
		name     string
		dn       string
		expected string
	}{
		{
			name:     "empty DN",
			dn:       "",
			expected: "",
		},
		{
			name:     "CN only",
			dn:       "CN=test",
			expected: "test",
		},
		{
			name:     "CN with spaces",
			dn:       "CN=test node",
			expected: "test node",
		},
		{
			name:     "CN in middle",
			dn:       "O=Org,CN=middle,OU=Unit",
			expected: "middle",
		},
		{
			name:     "OpenSSL format CN in middle",
			dn:       "/O=Org/CN=middle/OU=Unit",
			expected: "middle",
		},
		{
			name:     "no CN",
			dn:       "O=Org,OU=Unit",
			expected: "",
		},
		{
			name:     "OpenSSL format no CN",
			dn:       "/O=Org/OU=Unit",
			expected: "",
		},
		{
			name:     "CN= at end",
			dn:       "O=Org,CN=",
			expected: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := extractCNFromDN(tt.dn)
			assert.Equal(t, tt.expected, result)
		})
	}
}
