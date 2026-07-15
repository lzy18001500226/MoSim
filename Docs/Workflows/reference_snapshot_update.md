# Reference Snapshot Update Workflow

> Use this workflow for third-party source mirrors under `References/`.
> It keeps upstream freshness checks separate from local snapshot promotion so
> external repositories do not silently change MoSim project truth.

## 1. Goal

MoSim keeps selected open-source projects as pinned local source snapshots.
Those projects continue to change upstream, so the local copy needs a repeatable
freshness workflow:

```text
check upstream -> write update candidates -> review -> promote snapshot -> commit
```

The check phase is read-only against `References/`. The promotion phase is a
separate user-approved or current-goal-approved write task.

This workflow is for source snapshots and manifests. It is not an adoption
decision, not a runtime validation, and not a claim that upstream behavior is
accepted into MoSim.

## 2. Authority Boundary

| Action | Owner | Rule |
|---|---|---|
| Create or refresh manifest metadata | Current active thread / scoped crawler | Allowed when the current task explicitly scopes the reference family. |
| Check upstream HEADs | Current active thread / scoped crawler | Allowed as local freshness work; write only candidate reports. |
| Decide whether an update is worth study | Current active thread with user review when needed | Route deeper learning to the relevant current workflow. |
| Evaluate adopt/adapt/reference-only/reject | Current active thread / scoped research pass | Returns a proposal, not a direct route change. |
| Promote new source snapshot into `References/` | Current active thread under explicit write scope | Requires approved write scope and large-file/Git hygiene gates. |
| Change MoSim technical route | User/current active thread | Never implied by a reference update. |

Reference freshness checks must not auto-update `References/`. They produce
inventory, manifests, and update candidates only unless the current task
explicitly approves promotion.

## 3. Directory Layout

For Gazebo / `gazebosim`, use this layout:

```text
References/Gazebo/
  MANIFEST.gazebosim.json
  gz-sim/
  sdformat/
  gz-physics/
  ...

Results/external_learning/gazebosim_update_YYYYMMDD/
  update_candidates.json
  update_summary.md
  blockers.json
  temp/
```

Do not add an extra organization layer below `References/Gazebo/`. The source
organization belongs in the manifest fields, not in the path:

```text
local_path: References/Gazebo/gz-sim
source_org: gazebosim
source_url: https://github.com/gazebosim/gz-sim
```

For other source families, use the same pattern:

```text
References/<Family>/<repo>/
References/<Family>/MANIFEST.<source_family>.json
Results/external_learning/<source_family>_update_YYYYMMDD/
```

For ROS2 organization snapshots, use:

```text
References/ROS2/
  MANIFEST.ros2.json
  rclcpp/
  rclpy/
  rmw/
  rosbag2/
  ...

Results/external_learning/ros2_crawl_YYYYMMDD/
  inventory.json
  selection_summary.md
  blockers.json
  temp/

Results/external_learning/ros2_update_YYYYMMDD/
  update_candidates.json
  update_summary.md
  blockers.json
  temp/
```

`References/ROS2/<repo>/` is the canonical local path. Do not add another
`ros2/` organization layer below it. The organization belongs in manifest
metadata:

```text
local_path: References/ROS2/rclcpp
source_org: ros2
source_url: https://github.com/ros2/rclcpp
```

## 4. Manifest Contract

Each reference project entry must contain enough metadata to reproduce the
snapshot and check for drift:

```json
{
  "name": "gz-sim",
  "source_org": "gazebosim",
  "source_url": "https://github.com/gazebosim/gz-sim",
  "local_path": "References/Gazebo/gz-sim",
  "default_branch": "main",
  "pinned_sha": "<commit-sha-present-in-local-snapshot>",
  "pinned_at": "YYYY-MM-DD",
  "last_checked": "YYYY-MM-DD",
  "last_upstream_sha": "<last-seen-upstream-sha>",
  "snapshot_status": "present",
  "adoption_status": "reference-only",
  "license": "unknown | Apache-2.0 | BSD-3-Clause | ...",
  "excluded": false,
  "exclude_reason": null,
  "large_file_policy": "blocked_over_100MiB_or_lfs_required",
  "owner_thread": "MoSim｜开源项目探针-R2",
  "notes": "Local source snapshot only; not adopted project truth."
}
```

Allowed `snapshot_status` values:

```text
present
manifest_only
update_candidate
promotion_pending
blocked
retired
```

Allowed `adoption_status` values:

```text
adopt
adapt
reference-only
reject
blocked
unreviewed
```

Probe output should normally use `reference-only` or `unreviewed`. Only a
current active-thread adoption review, with user review when the route changes,
may upgrade adoption status.

## 5. Intake Filter

Before crawling or updating an organization, write the selection rule into the
manifest or task packet.

For `gazebosim`, the current rule is:

```text
include:
  non-archived source/tool/library/doc/test/template repos relevant to Gazebo
  simulator architecture, ROS bridge, SDFormat, sensors, rendering, physics,
  transport, messages, GUI, tools, or build infrastructure

exclude:
  archived=true
  demo-only repos, including *_demo or obvious demo/tutorial-party repos
  release metapackages, including gz-citadel, gz-fortress, gz-harmonic,
    gz-ionic, gz-jetty, gz-kura and similar umbrella release repos
  private, unavailable, deleted, or 404 repos
```

Excluded repositories still belong in the manifest with:

```text
excluded: true
exclude_reason: archived | demo_only | release_metapackage | unavailable | out_of_scope
```

This makes later audits explicit instead of rediscovering the same repository
family.

For `ros2`, the current rule is:

```text
include P0 source snapshots:
  ros2
  rcl
  rclcpp
  rclpy
  rcutils
  rcpputils
  rmw
  rmw_implementation
  rmw_dds_common
  rmw_cyclonedds
  rmw_fastrtps
  common_interfaces
  rcl_interfaces
  example_interfaces
  rosidl
  rosidl_core
  rosidl_defaults
  rosidl_typesupport
  rosidl_typesupport_fastrtps
  rosidl_runtime_py
  rosidl_python
  launch
  launch_ros
  ros2cli
  ros2cli_common_extensions
  geometry2
  message_filters
  rviz
  rosbag2
  rosbag2_bag_v2
  ros1_bridge
  ros2_tracing
  domain_bridge

include P1 on-demand snapshots:
  cartographer
  cartographer_ros
  performance_test
  performance_test_fixture
  ros2-performance
  ros2-benchmark-container
  system_tests
  ros_testing
  ros2_dds_profiles_examples
  realtime_support
  sros2
  urdf
  unique_identifier
  unique_identifier_msgs
  test_interface_files

include documentation/design snapshots:
  design
  ros2_documentation
  tutorials
  cookbook
  examples

exclude:
  archived=true
  *_tutorial_party and *_tutorial_party_old
  demo-only repositories, including *_demo and obvious demo-only repos
  buildfarm, CI, packaging, release tracking, and organization metadata repos
  pure website repositories
  vendor packages unless a later build or source-analysis task requires them
```

Current examples of active ROS2 repositories that are excluded by policy:

```text
.github
apex_rostest
buildfarm_perf_tests
choco-packages
ci
darknet_vendor
demos
detection_visualizer
kilted_tutorial_party
lyrical_tutorial_party
lyrical_tutorial_party_old
Mimick
mimick_vendor
netperf
openrobotics_darknet_ros
orocos_kdl_vendor
orocos_kinematics_dynamics
release-tracking
ros_buildfarm_config
ros_network_viz
ros_workspace
ros2.github.io
slide_show
teleop_twist_joy
teleop_twist_keyboard
tsc_working_group_governance_template
variants
*_vendor unless required
```

ROS2 crawl output must not say that these repositories are adopted MoSim
runtime dependencies. The default status is `reference-only` or `unreviewed`;
The current active thread routes any deeper learning to the relevant current
workflow.

## 6. Freshness Check

The freshness check compares local `pinned_sha` with the current upstream
default-branch HEAD. It does not modify source snapshots.

Preferred check:

```powershell
git ls-remote https://github.com/gazebosim/gz-sim.git refs/heads/main
```

If the default branch is unknown, discover it with the GitHub API or a scoped
repository metadata call, then record it in the manifest.

State classification:

| State | Meaning | Action |
|---|---|---|
| `up_to_date` | upstream HEAD equals `pinned_sha` | Update `last_checked` only if the task permits manifest writes. |
| `update_available` | upstream HEAD differs from `pinned_sha` | Write candidate entry; do not update `References/`. |
| `branch_missing` | recorded branch no longer exists | Write blocker. |
| `repo_unavailable` | 404, deleted, moved, private, or network-auth blocked | Write blocker; do not remove local snapshot automatically. |
| `metadata_changed` | archived/license/default branch changed | Write candidate or blocker depending on risk. |

Candidate reports live under:

```text
Results/external_learning/<source_family>_update_YYYYMMDD/update_candidates.json
Results/external_learning/<source_family>_update_YYYYMMDD/update_summary.md
Results/external_learning/<source_family>_update_YYYYMMDD/blockers.json
```

## 7. Candidate Report Contract

Each candidate entry should include:

```json
{
  "name": "gz-sim",
  "local_path": "References/Gazebo/gz-sim",
  "source_url": "https://github.com/gazebosim/gz-sim",
  "old_sha": "<manifest-pinned-sha>",
  "new_sha": "<upstream-head-sha>",
  "default_branch": "main",
  "state": "update_available",
  "candidate_only": true,
  "changed_files_count": null,
  "license_changed": "unknown",
  "large_file_risk": "unknown",
  "recommended_next_owner": "MoSim｜开源项目学习部-R2",
  "manual_review_required": true,
  "notes": "Needs scoped clone/diff before promotion."
}
```

If a scoped temporary clone is authorized, enrich the candidate with:

```text
changed_files_count:
added_count:
deleted_count:
renamed_count:
large_files:
license_changed:
cmake_or_package_changed:
public_api_changed:
ros_interface_changed:
recommended_next_owner:
risk_level: low | medium | high | blocked
```

Do not use candidate reports as accepted technical evidence. They are routing
inputs for the current active thread and focused research passes.

## 8. Scoped Temporary Clone

When the current task authorizes deeper candidate inspection, clone into `Results/`, not
directly into `References/`:

```powershell
git clone --depth 1 --filter=blob:none --single-branch `
  https://github.com/gazebosim/gz-sim.git `
  Results/external_learning/gazebosim_update_YYYYMMDD/temp/gz-sim
```

If a repository needs file-level comparison, materialize only the selected
paths. Prefer sparse checkout when the repository is large.

Never keep the upstream `.git/` directory in `References/`. MoSim stores source
snapshots, not nested upstream repositories.

## 9. Snapshot Promotion

Promotion means replacing or adding `References/<Family>/<repo>/` with a
cleaned source snapshot and updating the manifest `pinned_sha`.

Promotion requires an explicit user/current-task write scope naming:

```text
References/Gazebo/<repo>/
References/Gazebo/MANIFEST.gazebosim.json
Results/external_learning/<source_family>_update_YYYYMMDD/
```

Promotion steps:

1. Confirm approved repo list and write scope.
2. Clone to a temporary directory under `Results/external_learning/.../temp/`.
3. Remove upstream `.git/`.
4. Remove generated/build/cache/dependency outputs.
5. Check for single files at or above GitHub's 100 MiB hard limit.
6. Compare old and new snapshot.
7. Update `References/<Family>/<repo>/`.
8. Update manifest `pinned_sha`, `pinned_at`, `last_checked`, license and notes.
9. Stage and commit in repo-sized or small batches.

Default cleanup rules:

```text
.git/
build/
install/
log/
.venv/
node_modules/
__pycache__/
.pytest_cache/
dist/
out/
coverage/
*.pyc
```

Keep ordinary source, docs, examples, configs, package files, model files,
world files, launch files and tests unless a task-specific large-file or
license blocker says otherwise.

## 10. Git And Large-File Gates

Before staging:

```text
no nested .git directories under References
no credentials, tokens, local user configs or browser/cache data
no generated dependency trees unless explicitly required
no single file >= 100 MiB in normal Git
license files preserved
manifest updated
```

Before commit:

```powershell
git diff --cached --check
```

Commit in bounded batches:

```text
one repository per commit, or a small related group
avoid broad git add -A
avoid hiding ordinary source behind broad temporary .gitignore rules
record blockers instead of forcing huge binary or dependency payloads
```

If a temporary `.gitignore` throttle is used during a large import, it is a
drain queue. The task is not complete until the broad rule is removed, narrowed
to durable class guards, or recorded as a blocker.

## 11. Recurring Cadence

Recommended cadence for known local reference families:

| Family | Cadence | Owner |
|---|---|---|
| `References/Gazebo/` | Weekly or before ROS/Gazebo integration work | Current active thread / scoped reference audit |
| `References/ROS2/` | Only when ROS2 lane is explicitly reopened | Current active thread / scoped reference audit |
| `References/PX4/` | Before PX4/MAVROS bridge work | Current active thread / scoped reference audit |
| `References/Sunray/` | Before Sunray structural comparison tasks | Current active thread / scoped reference audit |
| `References/Lab/` | Before planner/perception route decisions | Current active thread / scoped reference audit |
| `References/Agent/` | Before legacy agent architecture or tooling cleanup | Current active thread / scoped reference audit |

Recurring checks should write candidate reports only. Promotion remains a
separate approved task.

## 12. Blocker Conditions

Write a blocker packet or blocker report when any of these occur:

```text
network access unavailable or rate-limited
repository moved, deleted, private, or branch missing
license changed or license absent
single file >= 100 MiB
large generated/dependency tree dominates the snapshot
submodule required for meaningful source but not authorized
Git index/staging becomes too large or slow for a bounded batch
task would modify References without approved promotion scope
task would require adoption or technical-route decision
```

Do not delete local snapshots just because upstream is unavailable. Mark the
manifest entry as `repo_unavailable` or `blocked` and ask for a route decision.

## 13. Completion Evidence

Freshness-check completion should report:

```text
manifest path:
candidate report path:
repos checked:
up_to_date:
update_available:
blocked:
excluded:
next owner suggestions:
```

Promotion completion should report:

```text
repos promoted:
old_sha -> new_sha:
manifest path:
large-file checks:
cleanup applied:
commit hash:
remaining blockers:
claim boundary:
```

Always include the claim boundary:

```text
These are external source snapshots or update candidates.
They are not adopted MoSim technical truth unless the current active thread documents a
separate adopt/adapt decision with evidence.
```
