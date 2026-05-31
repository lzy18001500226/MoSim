package envbundle

import (
	"errors"

	"github.com/anthropics/agentsmesh/backend/internal/domain/envbundle"
	"github.com/anthropics/agentsmesh/backend/pkg/crypto"
)

// Standardized errors used by the service. REST handlers map these to HTTP
// status codes.
var (
	ErrNotFound      = errors.New("env bundle not found")
	ErrNameExists    = errors.New("env bundle with this name already exists")
	ErrInvalidKind   = errors.New("invalid env bundle kind")
	ErrInvalidScope  = errors.New("invalid owner scope")
)

// Service owns the encrypt-aware CRUD around the EnvBundle repository.
// Encryption is applied transparently for credential-kind bundles; other
// kinds round-trip data as plaintext.
type Service struct {
	repo      envbundle.Repository
	encryptor *crypto.Encryptor
}

// NewService wires a Service.
func NewService(repo envbundle.Repository, encryptor *crypto.Encryptor) *Service {
	return &Service{repo: repo, encryptor: encryptor}
}
