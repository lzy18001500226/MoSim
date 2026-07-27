# MoSim Patch Record

No retained `fixed_formation` source, CMake, package metadata, launch,
configuration, or script file was changed while copying this component into
`src/planning/fixed_formation`.

The imported payload deliberately includes the six pre-existing, uncommitted
MoSim working-tree changes present at capture time:

1. `src/planner/path_searching/include/path_searching/dyn_a_star.h`
2. `src/planner/path_searching/src/dyn_a_star.cpp`
3. `src/planner/plan_manage/include/plan_manage/ego_replan_fsm.h`
4. `src/planner/plan_manage/src/ego_replan_fsm.cpp`
5. `src/planner/traj_opt/include/optimizer/poly_traj_optimizer.h`
6. `src/planner/traj_opt/src/poly_traj_optimizer.cpp`

They are the current collision/replanning working-tree snapshot, not migration
edits. The migration excludes only `fig/` documentation/demo media and
`.vscode/` local editor settings. The only additions are `.gitattributes`,
`UPSTREAM.md`, and this file; they are outside the 525-file payload represented
by the SHA-256 in `UPSTREAM.md`.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact Swarm-Formation source revision and GPL
   redistribution obligations;
2. review and commit the retained collision/replanning worktree patch as an
   explicit planner change, independently from this copy-only migration;
3. update only audited Factory scripts, Profiles, and ROS overlays to the
   canonical path;
4. validate source-audit and workspace-patch assumptions without silently
   reapplying a patch to an already modified canonical copy;
5. run the declared static and ROS1 build/preflight checks; and
6. keep `References/Lab/swarm_coordination/Swarm-Formation` intact as the
   retained legacy source unless a later user-approved archival task says
   otherwise.
