# Gazebo Rotary Collection

The Rotary collection is a rolling release of Gazebo libraries built continuously
from their `main` branches. It provides a stable integration target between
versioned Gazebo collection releases, allowing users and CI pipelines to track
the latest development of all Gazebo packages.

https://gazebosim.org/

## Package Naming Convention

The alias naming rule is to inject the collection name (`rotary`) after `gz-`:

| Platform | Original              | Rotary alias                  |
|----------|-----------------------|-------------------------------|
| Ubuntu   | `libgz-cmake-dev`     | `libgz-rotary-cmake-dev`      |
| Ubuntu   | `gz-plugin-cli`       | `gz-rotary-plugin-cli`        |
| Ubuntu   | `python3-gz-math`     | `python3-gz-rotary-math`      |
| Brew     | `gz-mathN`            | `gz-rotary-math`              |

Special case for sdformat (no `gz-` prefix in its package name):
`libsdformat-dev` → `libgz-rotary-sdformat-dev` (Ubuntu),
`gz-rotary-sdformat` (Brew).
