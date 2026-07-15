#!/usr/bin/env python3
"""Enforce RACER swarm clearance and keep stationary UAVs in collision checks."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    if old not in text:
        raise RuntimeError(f"{path}: expected patch anchor not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def apply(root: Path) -> bool:
    container_h = root / "plan_manage/include/plan_manage/plan_container.hpp"
    manager_h = root / "plan_manage/include/plan_manage/planner_manager.h"
    manager_cpp = root / "plan_manage/src/planner_manager.cpp"
    fsm_cpp = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    for path in (container_h, manager_h, manager_cpp, fsm_cpp):
        if not path.is_file():
            raise FileNotFoundError(f"RACER source missing: {path}")

    changed = False
    changed |= replace_once(
        container_h,
        "  double relax_time1_, relax_time2_;\n",
        "  double relax_time1_, relax_time2_;\n"
        "  double swarm_clearance_;  // Hard XY clearance used by trajectory arbitration.\n",
        "swarm_clearance_;",
    )
    changed |= replace_once(
        manager_h,
        "  bool checkSwarmCollision(const int& drone_id);\n",
        "  bool checkSwarmCollision(const int& drone_id);\n"
        "  bool isSwarmTrajectoryStationary(const int& drone_id);\n",
        "isSwarmTrajectoryStationary",
    )
    changed |= replace_once(
        manager_cpp,
        '  nh.param("manager/relax_time2", pp_.relax_time2_, 0.5);\n',
        '  nh.param("manager/relax_time2", pp_.relax_time2_, 0.5);\n'
        '  nh.param("optimization/swarm_safe_dist", pp_.swarm_clearance_, 0.5);\n',
        'pp_.swarm_clearance_, 0.5',
    )
    changed |= replace_once(
        manager_cpp,
        "  double self_t = 0.02 + (ros::Time::now() - local_data_.start_time_).toSec();\n"
        "  double other_t = 0.02 + ros::Time::now().toSec() - traj.start_time_;\n"
        "\n"
        "  while (self_t < local_data_.duration_ && self_t > 0 && other_t < traj.duration_) {\n"
        "    auto self_pos = local_data_.position_traj_.evaluateDeBoorT(self_t);\n"
        "    auto other_pos = traj.evaluateDeBoorT(other_t);\n"
        "    // if ((self_pos - other_pos).norm() < 0.6) return false;\n"
        "    // if ((self_pos - other_pos).head<2>().norm() < 0.2) return false;\n"
        "    if ((self_pos - other_pos).head<2>().norm() < 0.5) return false;\n"
        "\n"
        "    self_t += 0.02;\n"
        "    other_t += 0.02;\n"
        "  }\n",
        "  // MoSim: compare both splines on one absolute timeline, including future starts.\n"
        "  const double self_start = local_data_.start_time_.toSec();\n"
        "  const double other_start = traj.start_time_;\n"
        "  double sample_t = std::max(ros::Time::now().toSec() + 0.02,\n"
        "      std::max(self_start, other_start));\n"
        "  const double end_t = std::min(self_start + local_data_.duration_,\n"
        "      other_start + traj.duration_);\n"
        "\n"
        "  while (sample_t < end_t) {\n"
        "    auto self_pos = local_data_.position_traj_.evaluateDeBoorT(sample_t - self_start);\n"
        "    auto other_pos = traj.evaluateDeBoorT(sample_t - other_start);\n"
        "    if ((self_pos - other_pos).head<2>().norm() < pp_.swarm_clearance_) return false;\n"
        "    sample_t += 0.02;\n"
        "  }\n",
        "MoSim: compare both splines on one absolute timeline",
    )
    changed |= replace_once(
        manager_cpp,
        "  return true;\n"
        "}\n"
        "\n"
        "}  // namespace fast_planner\n",
        "  return true;\n"
        "}\n"
        "\n"
        "bool FastPlannerManager::isSwarmTrajectoryStationary(const int& id) {\n"
        "  if (id < 1 || id > swarm_traj_data_.drone_num_ ||\n"
        "      !swarm_traj_data_.receive_flags_[id - 1])\n"
        "    return false;\n"
        "\n"
        "  const Eigen::MatrixXd ctrl_pts =\n"
        "      swarm_traj_data_.swarm_trajs_[id - 1].getControlPoint();\n"
        "  if (ctrl_pts.rows() == 0) return false;\n"
        "  for (int i = 1; i < ctrl_pts.rows(); ++i) {\n"
        "    if ((ctrl_pts.row(i) - ctrl_pts.row(0)).head<2>().norm() > 0.05)\n"
        "      return false;\n"
        "  }\n"
        "  return true;\n"
        "}\n"
        "\n"
        "}  // namespace fast_planner\n",
        "FastPlannerManager::isSwarmTrajectoryStationary",
    )
    changed |= replace_once(
        fsm_cpp,
        "    bspline.traj_id = info->traj_id_;\n"
        "    Eigen::MatrixXd pos_pts = info->position_traj_.getControlPoint();\n",
        "    bspline.traj_id = info->traj_id_;\n"
        "    // Set the sender identity before newest_traj_ can be broadcast by the timer.\n"
        "    bspline.drone_id = expl_manager_->ep_->drone_id_;\n"
        "    Eigen::MatrixXd pos_pts = info->position_traj_.getControlPoint();\n",
        "Set the sender identity before newest_traj_",
    )
    changed |= replace_once(
        fsm_cpp,
        "  // Ignore self trajectory\n"
        "  if (msg->drone_id == sdat.drone_id_) return;\n"
        "\n"
        "  // Ignore outdated trajectory\n",
        "  // Reject malformed swarm messages before indexing per-UAV storage.\n"
        "  const int expected_knots = int(msg->pos_pts.size()) + msg->order + 1;\n"
        "  if (msg->drone_id < 1 || msg->drone_id > sdat.drone_num_ ||\n"
        "      msg->order < 1 || int(msg->pos_pts.size()) <= msg->order ||\n"
        "      int(msg->knots.size()) != expected_knots) {\n"
        "    ROS_ERROR_THROTTLE(1.0,\n"
        "        \"Reject malformed swarm trajectory: sender=%d self=%d drones=%d \"\n"
        "        \"order=%d pos_pts=%zu knots=%zu expected_knots=%d\",\n"
        "        msg->drone_id, sdat.drone_id_, sdat.drone_num_, msg->order,\n"
        "        msg->pos_pts.size(), msg->knots.size(), expected_knots);\n"
        "    return;\n"
        "  }\n"
        "\n"
        "  // Ignore self trajectory\n"
        "  if (msg->drone_id == sdat.drone_id_) return;\n"
        "\n"
        "  // Ignore outdated trajectory\n",
        "Reject malformed swarm trajectory",
    )
    changed |= replace_once(
        fsm_cpp,
        "    info->start_time_ = (ros::Time::now() - time_r).toSec() > 0 ? ros::Time::now() : time_r;\n"
        "\n"
        "    bspline::Bspline bspline;\n",
        "    info->start_time_ = (ros::Time::now() - time_r).toSec() > 0 ? ros::Time::now() : time_r;\n"
        "\n"
        "    // MoSim: higher-ID UAVs yield to already published lower-ID trajectories.\n"
        "    for (int peer_id = 1; peer_id < expl_manager_->ep_->drone_id_; ++peer_id) {\n"
        "      if (!planner_manager_->checkSwarmCollision(peer_id)) {\n"
        "        ROS_WARN(\"MoSim reject pre-publication trajectory for drone %d: \"\n"
        "                 \"clearance conflict with priority drone %d\",\n"
        "            expl_manager_->ep_->drone_id_, peer_id);\n"
        "        return FAIL;\n"
        "      }\n"
        "    }\n"
        "\n"
        "    bspline::Bspline bspline;\n",
        "MoSim reject pre-publication trajectory",
    )
    changed |= replace_once(
        fsm_cpp,
        "    if (!planner_manager_->checkSwarmCollision(msg->drone_id)) {\n"
        "      ROS_ERROR(\"Drone %d collide with drone %d.\", sdat.drone_id_, msg->drone_id);\n"
        "      fd_->avoid_collision_ = true;\n"
        "      transitState(PLAN_TRAJ, \"swarmTrajCallback\");\n"
        "    }\n",
        "    if (!planner_manager_->checkSwarmCollision(msg->drone_id)) {\n"
        "      if (sdat.drone_id_ > msg->drone_id) {\n"
        "        ROS_ERROR(\"Drone %d yields to priority drone %d for swarm clearance.\",\n"
        "            sdat.drone_id_, msg->drone_id);\n"
        "        fd_->avoid_collision_ = true;\n"
        "        transitState(PLAN_TRAJ, \"swarmTrajCallback\");\n"
        "      } else {\n"
        "        ROS_WARN_THROTTLE(1.0,\n"
        "            \"Drone %d keeps priority over drone %d during swarm clearance conflict.\",\n"
        "            sdat.drone_id_, msg->drone_id);\n"
        "      }\n"
        "    }\n",
        "keeps priority over drone",
    )
    changed |= replace_once(
        fsm_cpp,
        "    // MoSim: higher-ID UAVs yield to already published lower-ID trajectories.\n"
        "    for (int peer_id = 1; peer_id < expl_manager_->ep_->drone_id_; ++peer_id) {\n"
        "      if (!planner_manager_->checkSwarmCollision(peer_id)) {\n"
        "        ROS_WARN(\"MoSim reject pre-publication trajectory for drone %d: \"\n"
        "                 \"clearance conflict with priority drone %d\",\n"
        "            expl_manager_->ep_->drone_id_, peer_id);\n"
        "        return FAIL;\n"
        "      }\n"
        "    }\n",
        "    // MoSim: moving peers use ID priority; stationary peers always keep occupancy.\n"
        "    const int self_id = expl_manager_->ep_->drone_id_;\n"
        "    for (int peer_id = 1; peer_id <= expl_manager_->ep_->drone_num_; ++peer_id) {\n"
        "      if (peer_id == self_id) continue;\n"
        "      const bool peer_stationary =\n"
        "          planner_manager_->isSwarmTrajectoryStationary(peer_id);\n"
        "      if ((peer_id < self_id || peer_stationary) &&\n"
        "          !planner_manager_->checkSwarmCollision(peer_id)) {\n"
        "        ROS_WARN(\"MoSim reject pre-publication trajectory for drone %d: \"\n"
        "                 \"clearance conflict with %s drone %d\",\n"
        "            self_id, peer_stationary ? \"stationary\" : \"priority\", peer_id);\n"
        "        return FAIL;\n"
        "      }\n"
        "    }\n",
        "MoSim: moving peers use ID priority; stationary peers always keep occupancy.",
    )
    changed |= replace_once(
        fsm_cpp,
        "      if (sdat.drone_id_ > msg->drone_id) {\n"
        "        ROS_ERROR(\"Drone %d yields to priority drone %d for swarm clearance.\",\n"
        "            sdat.drone_id_, msg->drone_id);\n",
        "      const bool peer_stationary =\n"
        "          planner_manager_->isSwarmTrajectoryStationary(msg->drone_id);\n"
        "      if (sdat.drone_id_ > msg->drone_id || peer_stationary) {\n"
        "        ROS_ERROR(\"Drone %d yields to %s drone %d for swarm clearance.\",\n"
        "            sdat.drone_id_, peer_stationary ? \"stationary\" : \"priority\",\n"
        "            msg->drone_id);\n",
        "peer_stationary ? \"stationary\" : \"priority\"",
    )
    changed |= replace_once(
        fsm_cpp,
        "  } else if (state_ == WAIT_TRIGGER) {\n"
        "    // Publish a virtual traj at current pose, to avoid collision\n",
        "  } else if (state_ == WAIT_TRIGGER || state_ == IDLE) {\n"
        "    // MoSim: waiting and idle UAVs remain stationary collision obstacles.\n",
        "failed-planning UAVs remain collision obstacles",
    )
    changed |= replace_once(
        fsm_cpp,
        "  if (state_ == EXEC_TRAJ) {\n"
        "    swarm_traj_pub_.publish(fd_->newest_traj_);\n"
        "\n"
        "  } else if (state_ == WAIT_TRIGGER || state_ == IDLE) {\n"
        "    // MoSim: waiting and idle UAVs remain stationary collision obstacles.\n",
        "  if (state_ == EXEC_TRAJ ||\n"
        "      ((state_ == PLAN_TRAJ || state_ == PUB_TRAJ) && !fd_->static_state_)) {\n"
        "    // Keep the current spline visible while a moving UAV replans.\n"
        "    swarm_traj_pub_.publish(fd_->newest_traj_);\n"
        "\n"
        "  } else if (state_ == WAIT_TRIGGER || state_ == IDLE ||\n"
        "             ((state_ == PLAN_TRAJ || state_ == PUB_TRAJ) && fd_->static_state_)) {\n"
        "    // MoSim: waiting, idle, and failed-planning UAVs remain collision obstacles.\n",
        "failed-planning UAVs remain collision obstacles",
    )
    changed |= replace_once(
        fsm_cpp,
        "    NonUniformBspline tmp(pos_pts, planner_manager_->pp_.bspline_degree_, 1.0);\n",
        "    // A long stationary horizon gives moving peers enough time to yield safely.\n"
        "    NonUniformBspline tmp(pos_pts, planner_manager_->pp_.bspline_degree_, 10.0);\n",
        "A long stationary horizon gives moving peers enough time to yield safely.",
    )

    print(
        "RACER hard swarm-clearance and stationary-occupancy arbitration "
        f"{'applied' if changed else 'already present'}: {root}"
    )
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("racer_source_root", type=Path)
    args = parser.parse_args()
    apply(args.racer_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
