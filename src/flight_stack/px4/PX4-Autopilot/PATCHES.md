# Local Patch Record

The 2026-07-29 migration itself copied no PX4 source patch from the
Ubuntu-20.04 Sunray runtime snapshot.

## Source Activation Compatibility

- `CMakeLists.txt`: a snapshot without `.git` now falls back to the recorded
  `v1.14.0`, PX4 commit, and MAVLink submodule commit before PX4 parses its
  major/minor/patch fields. `src/lib/version/build_git_version_snapshot.h.in`
  emits the corresponding PX4 and MAVLink macros, preserving the version symbol
  expected by the stock final link. This changes build metadata only; it does
  not alter flight code, board configuration, or SITL behavior.
- `Scripts/sunray/build_local_px4_sitl.sh` (outside this source tree) uses the
  explicit project-local `build/px4/python_deps` directory for the minimal
  `kconfiglib` and `future` PX4 generator dependencies, while explicitly
  retaining the declared ROS Noetic Python package path for `genmsg`. It never
  installs into the WSL global Python environment.

Validation is pending the project-local PX4 configuration and `px4` target
build. Future PX4 source changes must be recorded here with their purpose,
affected files, and validation evidence.
