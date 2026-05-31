package fileconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	fileservice "github.com/anthropics/agentsmesh/backend/internal/service/file"
	filev1 "github.com/anthropics/agentsmesh/proto/gen/go/file/v1"
)

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

func TestPresignUpload_NoOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.PresignUpload(context.Background(),
		connect.NewRequest(&filev1.PresignUploadRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestMapFileError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"file_too_large", fileservice.ErrFileTooLarge, connect.CodeResourceExhausted},
		{"invalid_file_type", fileservice.ErrInvalidFileType, connect.CodeInvalidArgument},
		{"storage_error", fileservice.ErrStorageError, connect.CodeUnavailable},
		{"generic", errors.New("boom"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			err := mapFileError(context.Background(), tc.in, &filev1.PresignUploadRequest{})
			assert.Equal(t, tc.want, connectCodeOf(t, err))
		})
	}
}

func TestProcedureConstants(t *testing.T) {
	assert.Equal(t, "/proto.file.v1.FileService/PresignUpload", PresignUploadProcedure)
}
