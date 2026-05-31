package envbundle

import (
	"fmt"

	"github.com/anthropics/agentsmesh/backend/internal/domain/envbundle"
)

// encryptData encrypts every value when the kind demands it; for non-encrypted
// kinds the map is returned as-is (still backed by JSONB at the DB layer).
func (s *Service) encryptData(kind string, data map[string]string) (envbundle.BundleData, error) {
	if !envbundle.IsEncryptedKind(kind) {
		out := make(envbundle.BundleData, len(data))
		for k, v := range data {
			out[k] = v
		}
		return out, nil
	}
	out := make(envbundle.BundleData, len(data))
	for k, v := range data {
		enc, err := s.encryptor.Encrypt(v)
		if err != nil {
			return nil, err
		}
		out[k] = enc
	}
	return out, nil
}

// decryptData reverses encryptData. Returns plaintext KV regardless of kind.
// For encrypted kinds, ANY value that fails to decrypt aborts the whole bundle —
// the previous "silently treat ciphertext as plaintext" fallback would leak
// ciphertext into Pod env, which is a security and observability hazard.
// Bundles with corrupt rows must be rotated by the operator, not transparently
// degraded by this layer.
func (s *Service) decryptData(kind string, data envbundle.BundleData) (map[string]string, error) {
	out := make(map[string]string, len(data))
	if !envbundle.IsEncryptedKind(kind) {
		for k, v := range data {
			out[k] = v
		}
		return out, nil
	}
	for k, v := range data {
		dec, err := s.encryptor.Decrypt(v)
		if err != nil {
			return nil, fmt.Errorf("envbundle: failed to decrypt key %q: %w", k, err)
		}
		out[k] = dec
	}
	return out, nil
}
