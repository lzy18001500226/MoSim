# Static Parser Boundary

## Parser Correction

R2 017 treated a fully qualified target as unresolved when it was not an embedded declaration and was not listed in `package.order`. That is too narrow for this package surface.

The corrected 021 parser resolves these classes in order:

1. embedded declarations in `package.mo`;
2. child package directories containing `package.mo`;
3. sibling `.mo` files declaring the target class.

When a sibling `.mo` class is not in `package.order`, 021 classifies it as `resolved_hidden_sibling_mo_target`. That means it is statically present in source but intentionally omitted from the public ordered browser surface.

## Remaining Boundary

This parser does not execute MWORKS, does not load the package browser, does not run `check_model`, and does not validate diagram layout or equations. Any Modelica semantic, GUI browser, equation balance, or simulation claim remains a future live gate.
