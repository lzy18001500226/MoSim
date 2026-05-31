package storage

import (
	"context"
	"io"
	"time"
)

type FileInfo struct {
	Key         string
	Size        int64     // File size in bytes
	ContentType string
	ETag        string
	LastModified time.Time
}

type Storage interface {
	Upload(ctx context.Context, key string, reader io.Reader, size int64, contentType string) (*FileInfo, error)

	// Download streams object bytes back. Callers MUST Close() the reader.
	// Returned size is the storage-reported Content-Length (-1 if unknown).
	Download(ctx context.Context, key string) (io.ReadCloser, int64, error)

	Delete(ctx context.Context, key string) error

	GetURL(ctx context.Context, key string, expiry time.Duration) (string, error)

	GetInternalURL(ctx context.Context, key string, expiry time.Duration) (string, error)

	PresignPutURL(ctx context.Context, key string, contentType string, expiry time.Duration) (string, error)

	InternalPresignPutURL(ctx context.Context, key string, contentType string, expiry time.Duration) (string, error)

	Exists(ctx context.Context, key string) (bool, error)
}
