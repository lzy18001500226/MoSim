// Package migrations bundles every backend SQL migration into the
// agentsmesh-backend binary so deployments can apply schema changes via
// `agentsmesh-backend migrate up` without shipping a separate `migrate`
// CLI or mounting an /app/migrations directory.
//
// The deploy pipeline used to depend on the legacy GoReleaser image
// layout (alpine + downloaded `migrate` binary + `COPY --from=builder
// /app/migrations`). The Bazel image cut both. Embedding the SQL into
// the Go binary removes the dependency outright — the binary is the
// migration toolchain.
package migrations

import "embed"

// FS is the migration source for golang-migrate's iofs source driver.
// Every `*.sql` file in this directory is sealed into the binary at
// compile time, in lexicographic order — the same order golang-migrate
// uses to derive version numbers, so the embedded set behaves
// identically to a filesystem-backed source.
//
//go:embed *.sql
var FS embed.FS
