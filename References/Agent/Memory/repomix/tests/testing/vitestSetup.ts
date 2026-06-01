// Disable the token-count disk cache by default for the entire test suite so
// that (a) test runs do not read or write the developer's real cache file in
// $TMPDIR and (b) tests asserting on worker dispatch behavior are not skewed
// by entries left behind by a previous run. Tests that exercise the cache
// directly explicitly clear this variable in their own setup.
if (process.env.REPOMIX_TOKEN_CACHE === undefined) {
  process.env.REPOMIX_TOKEN_CACHE = '0';
}
