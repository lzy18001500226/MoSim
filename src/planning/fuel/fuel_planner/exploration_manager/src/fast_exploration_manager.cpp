// #include <fstream>
#include <exploration_manager/fast_exploration_manager.h>
#include <algorithm>
#include <cmath>
#include <thread>
#include <iostream>
#include <fstream>
#include <chrono>
#include <limits>
#include <set>
#include <lkh_tsp_solver/lkh_interface.h>
#include <active_perception/graph_node.h>
#include <active_perception/graph_search.h>
#include <active_perception/perception_utils.h>
#include <plan_env/raycast.h>
#include <plan_env/sdf_map.h>
#include <plan_env/edt_environment.h>
#include <active_perception/frontier_finder.h>
#include <plan_manage/planner_manager.h>

#include <exploration_manager/expl_data.h>

#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <visualization_msgs/Marker.h>

using namespace Eigen;

namespace fast_planner {
// SECTION interfaces for setup and query

FastExplorationManager::FastExplorationManager() {
}

FastExplorationManager::~FastExplorationManager() {
  ViewNode::astar_.reset();
  ViewNode::caster_.reset();
  ViewNode::map_.reset();
}

void FastExplorationManager::initialize(ros::NodeHandle& nh) {
  planner_manager_.reset(new FastPlannerManager);
  planner_manager_->initPlanModules(nh);
  edt_environment_ = planner_manager_->edt_environment_;
  sdf_map_ = edt_environment_->sdf_map_;
  frontier_finder_.reset(new FrontierFinder(edt_environment_, nh));
  // view_finder_.reset(new ViewFinder(edt_environment_, nh));

  ed_.reset(new ExplorationData);
  ep_.reset(new ExplorationParam);

  nh.param("exploration/refine_local", ep_->refine_local_, true);
  nh.param("exploration/refined_num", ep_->refined_num_, -1);
  nh.param("exploration/refined_radius", ep_->refined_radius_, -1.0);
  nh.param("exploration/top_view_num", ep_->top_view_num_, -1);
  nh.param("exploration/max_decay", ep_->max_decay_, -1.0);
  nh.param("exploration/tsp_dir", ep_->tsp_dir_, string("null"));
  nh.param("exploration/relax_time", ep_->relax_time_, 1.0);
  nh.param(
      "exploration/near_frontier_escape_enable", ep_->near_frontier_escape_enable_, false);
  nh.param(
      "exploration/near_frontier_escape_distance", ep_->near_frontier_escape_distance_, 0.75);
  nh.param(
      "exploration/near_frontier_escape_max_speed", ep_->near_frontier_escape_max_speed_, 0.25);
  nh.param(
      "exploration/near_frontier_escape_alternative_distance",
      ep_->near_frontier_escape_alternative_distance_, 2.0);
  nh.param("exploration/global_expansion_bias_enable", ep_->global_expansion_bias_enable_, false);
  nh.param("exploration/global_expansion_bias_rank_window", ep_->global_expansion_bias_rank_window_, 12);
  nh.param(
      "exploration/global_expansion_bias_dist_weight", ep_->global_expansion_bias_dist_weight_, 0.35);
  nh.param(
      "exploration/global_expansion_bias_lateral_weight", ep_->global_expansion_bias_lateral_weight_, 0.65);
  nh.param("exploration/global_expansion_bias_axis", ep_->global_expansion_bias_axis_, -1);
  nh.param("exploration/global_expansion_bias_min_gain", ep_->global_expansion_bias_min_gain_, 2.0);
  nh.param(
      "exploration/global_expansion_bias_override_refine",
      ep_->global_expansion_bias_override_refine_, false);
  nh.param("exploration/coverage_expansion_enable", ep_->coverage_expansion_enable_, false);
  nh.param("exploration/coverage_expansion_axis", ep_->coverage_expansion_axis_, 1);
  nh.param("exploration/coverage_expansion_rank_window", ep_->coverage_expansion_rank_window_, 20);
  nh.param("exploration/coverage_expansion_min_gain", ep_->coverage_expansion_min_gain_, 1.0);
  nh.param("exploration/coverage_expansion_dist_weight", ep_->coverage_expansion_dist_weight_, 0.05);
  nh.param(
      "exploration/coverage_expansion_grid_resolution",
      ep_->coverage_expansion_grid_resolution_, 2.0);
  nh.param(
      "exploration/coverage_expansion_sensor_radius", ep_->coverage_expansion_sensor_radius_, 8.0);
  nh.param(
      "exploration/coverage_expansion_project_horizon",
      ep_->coverage_expansion_project_horizon_, 5.0);
  nh.param(
      "exploration/coverage_expansion_grid_weight", ep_->coverage_expansion_grid_weight_, 1.0);
  nh.param(
      "exploration/coverage_expansion_span_weight", ep_->coverage_expansion_span_weight_, 0.2);
  nh.param(
      "exploration/coverage_expansion_uncovered_target_weight",
      ep_->coverage_expansion_uncovered_target_weight_, 0.0);
  nh.param(
      "exploration/coverage_expansion_score_committed_goal",
      ep_->coverage_expansion_score_committed_goal_, false);
  nh.param(
      "exploration/coverage_expansion_direct_uncovered_fallback",
      ep_->coverage_expansion_direct_uncovered_fallback_, false);
  nh.param(
      "exploration/coverage_expansion_global_selector",
      ep_->coverage_expansion_global_selector_, false);
  nh.param(
      "exploration/coverage_expansion_log_candidates",
      ep_->coverage_expansion_log_candidates_, false);

  nh.param("exploration/vm", ViewNode::vm_, -1.0);
  nh.param("exploration/am", ViewNode::am_, -1.0);
  nh.param("exploration/yd", ViewNode::yd_, -1.0);
  nh.param("exploration/ydd", ViewNode::ydd_, -1.0);
  nh.param("exploration/w_dir", ViewNode::w_dir_, -1.0);

  ViewNode::astar_.reset(new Astar);
  ViewNode::astar_->init(nh, edt_environment_);
  ViewNode::map_ = sdf_map_;

  double resolution_ = sdf_map_->getResolution();
  Eigen::Vector3d origin, size;
  sdf_map_->getRegion(origin, size);
  ViewNode::caster_.reset(new RayCaster);
  ViewNode::caster_->setParams(resolution_, origin);

  planner_manager_->path_finder_->lambda_heu_ = 1.0;
  // planner_manager_->path_finder_->max_search_time_ = 0.05;
  planner_manager_->path_finder_->max_search_time_ = 1.0;

  // Initialize TSP par file
  ofstream par_file(ep_->tsp_dir_ + "/single.par");
  par_file << "PROBLEM_FILE = " << ep_->tsp_dir_ << "/single.tsp\n";
  par_file << "GAIN23 = NO\n";
  par_file << "OUTPUT_TOUR_FILE =" << ep_->tsp_dir_ << "/single.txt\n";
  par_file << "RUNS = 1\n";

  // Analysis
  // ofstream fout;
  // fout.open("/home/boboyu/Desktop/RAL_Time/frontier.txt");
  // fout.close();
}

int FastExplorationManager::planExploreMotion(
    const Vector3d& pos, const Vector3d& vel, const Vector3d& acc, const Vector3d& yaw) {
  const auto stage_wall = std::chrono::steady_clock::now();
  auto stage = [&](const char* name) {
    ROS_WARN(
        "[FUEL_STAGE] %s wall_s=%.3f", name,
        std::chrono::duration<double>(std::chrono::steady_clock::now() - stage_wall).count());
  };
  ros::Time t1 = ros::Time::now();
  auto t2 = t1;
  ed_->views_.clear();
  ed_->global_tour_.clear();

  std::cout << "start pos: " << pos.transpose() << ", vel: " << vel.transpose()
            << ", acc: " << acc.transpose() << std::endl;

  // Search frontiers and group them into clusters
  frontier_finder_->searchFrontiers();
  stage("after_search_frontiers");

  double frontier_time = (ros::Time::now() - t1).toSec();
  t1 = ros::Time::now();

  // Find viewpoints (x,y,z,yaw) for all frontier clusters and get visible ones' info
  frontier_finder_->computeFrontiersToVisit();
  stage("after_compute_frontiers");
  frontier_finder_->getFrontiers(ed_->frontiers_);
  frontier_finder_->getFrontierBoxes(ed_->frontier_boxes_);
  frontier_finder_->getDormantFrontiers(ed_->dead_frontiers_);

  if (ed_->frontiers_.empty()) {
    ROS_WARN("No coverable frontier.");
    return NO_FRONTIER;
  }
  frontier_finder_->getTopViewpointsInfo(pos, ed_->points_, ed_->yaws_, ed_->averages_);
  if (!ed_->points_.empty()) {
    Vector3d point_min = ed_->points_[0], point_max = ed_->points_[0];
    Vector3d avg_min = ed_->averages_.empty() ? ed_->points_[0] : ed_->averages_[0];
    Vector3d avg_max = avg_min;
    for (int i = 0; i < ed_->points_.size(); ++i) {
      point_min = point_min.array().min(ed_->points_[i].array());
      point_max = point_max.array().max(ed_->points_[i].array());
      if (i < ed_->averages_.size()) {
        avg_min = avg_min.array().min(ed_->averages_[i].array());
        avg_max = avg_max.array().max(ed_->averages_[i].array());
      }
    }
    ROS_WARN(
        "[FUEL_TOUR_DIAG] candidate_pool n=%zu pos=(%.3f, %.3f, %.3f) "
        "view_x=[%.3f, %.3f] view_y=[%.3f, %.3f] view_z=[%.3f, %.3f] "
        "avg_x=[%.3f, %.3f] avg_y=[%.3f, %.3f] avg_z=[%.3f, %.3f]",
        ed_->points_.size(), pos.x(), pos.y(), pos.z(), point_min.x(), point_max.x(),
        point_min.y(), point_max.y(), point_min.z(), point_max.z(), avg_min.x(), avg_max.x(),
        avg_min.y(), avg_max.y(), avg_min.z(), avg_max.z());
  }
  for (int i = 0; i < ed_->points_.size(); ++i)
    ed_->views_.push_back(
        ed_->points_[i] + 2.0 * Vector3d(cos(ed_->yaws_[i]), sin(ed_->yaws_[i]), 0));

  double view_time = (ros::Time::now() - t1).toSec();
  ROS_WARN(
      "Frontier: %zu, t: %lf, viewpoint: %zu, t: %lf", ed_->frontiers_.size(), frontier_time,
      ed_->points_.size(), view_time);

  // Do global and local tour planning and retrieve the next viewpoint
  Vector3d next_pos;
  double next_yaw;
  if (ed_->points_.size() > 1) {
    // Find the global tour passing through all viewpoints
    // Create TSP and solve by LKH
    // Optimal tour is returned as indices of frontier
    vector<int> indices;
    findGlobalTour(pos, vel, yaw, indices);
    stage("after_global_tour");
    const int tour_log_n = std::min(static_cast<int>(indices.size()), 8);
    for (int rank = 0; rank < tour_log_n; ++rank) {
      const int id = indices[rank];
      if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
      const Vector3d avg =
          id < static_cast<int>(ed_->averages_.size()) ? ed_->averages_[id] : ed_->points_[id];
      ROS_WARN(
          "[FUEL_TOUR_DIAG] global_tour rank=%d id=%d view=(%.3f, %.3f, %.3f) "
          "avg=(%.3f, %.3f, %.3f) yaw=%.3f dist_xy=%.3f",
          rank, id, ed_->points_[id].x(), ed_->points_[id].y(), ed_->points_[id].z(), avg.x(),
          avg.y(), avg.z(), ed_->yaws_[id],
          (ed_->points_[id].head<2>() - pos.head<2>()).norm());
    }

    if (ep_->near_frontier_escape_enable_ && indices.size() > 1) {
      const int original_first_id = indices.front();
      if (original_first_id >= 0 && original_first_id < static_cast<int>(ed_->points_.size())) {
        const double first_dist_xy =
            (ed_->points_[original_first_id].head<2>() - pos.head<2>()).norm();
        const double speed_xy = vel.head<2>().norm();
        int alternative_rank = -1;
        double alternative_dist_xy = 0.0;

        if (first_dist_xy <= ep_->near_frontier_escape_distance_ &&
            speed_xy <= ep_->near_frontier_escape_max_speed_) {
          for (int rank = 1; rank < static_cast<int>(indices.size()); ++rank) {
            const int id = indices[rank];
            if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
            const double dist_xy = (ed_->points_[id].head<2>() - pos.head<2>()).norm();
            if (dist_xy >= ep_->near_frontier_escape_alternative_distance_) {
              alternative_rank = rank;
              alternative_dist_xy = dist_xy;
              break;
            }
          }
        }

        if (alternative_rank > 0) {
          const int alternative_id = indices[alternative_rank];
          indices.erase(indices.begin() + alternative_rank);
          indices.insert(indices.begin(), alternative_id);
          frontier_finder_->getPathForTour(pos, indices, ed_->global_tour_);
          ROS_WARN(
              "[FUEL_NEAR_FRONTIER_ESCAPE] original_id=%d original_dist_xy=%.3f "
              "speed_xy=%.3f alternative_rank=%d alternative_id=%d "
              "alternative_dist_xy=%.3f",
              original_first_id, first_dist_xy, speed_xy, alternative_rank, alternative_id,
              alternative_dist_xy);
        }
      }
    }

    if (ep_->global_expansion_bias_enable_ && !indices.empty()) {
      const int original_first_id = indices.front();
      const int rank_window =
          min(static_cast<int>(indices.size()), max(1, ep_->global_expansion_bias_rank_window_));

      Vector3d ref_target = original_first_id < static_cast<int>(ed_->averages_.size())
          ? ed_->averages_[original_first_id]
          : ed_->points_[original_first_id];
      Vector3d ref_dir = ref_target - pos;
      ref_dir.z() = 0.0;
      if (ref_dir.norm() < 1e-3) {
        ref_dir = vel;
        ref_dir.z() = 0.0;
      }
      if (ref_dir.norm() < 1e-3) ref_dir = Vector3d::UnitX();
      ref_dir.normalize();

      int best_rank = 0;
      double best_score = std::numeric_limits<double>::infinity();
      for (int rank = 0; rank < rank_window; ++rank) {
        const int id = indices[rank];
        if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
        const Vector3d target =
            id < static_cast<int>(ed_->averages_.size()) ? ed_->averages_[id] : ed_->points_[id];
        Vector3d diff = target - pos;
        diff.z() = 0.0;
        const double dist_xy = diff.norm();
        const double lateral_xy = fabs(diff.x() * (-ref_dir.y()) + diff.y() * ref_dir.x());
        const double score = static_cast<double>(rank) -
            ep_->global_expansion_bias_dist_weight_ * dist_xy -
            ep_->global_expansion_bias_lateral_weight_ * lateral_xy;

        ROS_WARN(
            "FUEL global expansion candidate rank=%d id=%d avg=(%.3f, %.3f, %.3f) "
            "view=(%.3f, %.3f, %.3f) dist_xy=%.3f lateral_xy=%.3f score=%.3f",
            rank, id, target.x(), target.y(), target.z(), ed_->points_[id].x(), ed_->points_[id].y(),
            ed_->points_[id].z(), dist_xy, lateral_xy, score);

        if (score < best_score) {
          best_score = score;
          best_rank = rank;
        }
      }

      if (best_rank > 0) {
        const int chosen_id = indices[best_rank];
        indices.erase(indices.begin() + best_rank);
        indices.insert(indices.begin(), chosen_id);
        ROS_WARN(
            "FUEL global expansion bias changed first frontier: original_id=%d chosen_id=%d "
            "chosen_rank=%d chosen_score=%.3f window=%d",
            original_first_id, chosen_id, best_rank, best_score, rank_window);
      } else {
        ROS_WARN(
            "FUEL global expansion bias kept first frontier: id=%d score=%.3f window=%d",
            original_first_id, best_score, rank_window);
      }
    }

    if (ep_->refine_local_) {
      // Do refinement for the next few viewpoints in the global tour
      // Idx of the first K frontier in optimal tour
      t1 = ros::Time::now();

      ed_->refined_ids_.clear();
      ed_->unrefined_points_.clear();
      int knum = min(int(indices.size()), ep_->refined_num_);
      for (int i = 0; i < knum; ++i) {
        auto tmp = ed_->points_[indices[i]];
        ed_->unrefined_points_.push_back(tmp);
        ed_->refined_ids_.push_back(indices[i]);
        if ((tmp - pos).norm() > ep_->refined_radius_ && ed_->refined_ids_.size() >= 2) break;
      }

      // Get top N viewpoints for the next K frontiers
      ed_->n_points_.clear();
      vector<vector<double>> n_yaws;
      frontier_finder_->getViewpointsInfo(
          pos, ed_->refined_ids_, ep_->top_view_num_, ep_->max_decay_, ed_->n_points_, n_yaws);

      ed_->refined_points_.clear();
      ed_->refined_views_.clear();
      vector<double> refined_yaws;
      refineLocalTour(pos, vel, yaw, ed_->n_points_, n_yaws, ed_->refined_points_, refined_yaws);
      stage("after_local_refine");
      next_pos = ed_->refined_points_[0];
      next_yaw = refined_yaws[0];
      if (!ed_->refined_points_.empty()) {
        ROS_WARN(
            "[FUEL_TOUR_DIAG] local_refine selected=(%.3f, %.3f, %.3f) yaw=%.3f "
            "unrefined_first_n=%zu refined_n=%zu",
            next_pos.x(), next_pos.y(), next_pos.z(), next_yaw, ed_->unrefined_points_.size(),
            ed_->refined_points_.size());
      }
      if (ep_->global_expansion_bias_enable_ && ep_->global_expansion_bias_override_refine_ &&
          !indices.empty() && !ed_->refined_points_.empty()) {
        const int axis = ep_->global_expansion_bias_axis_;
        const int rank_window =
            min(static_cast<int>(indices.size()), max(1, ep_->global_expansion_bias_rank_window_));
        double current_gain = 0.0;
        if (axis == 0 || axis == 1) {
          current_gain = fabs((next_pos - pos)[axis]);
        }

        int best_rank = -1;
        int best_id = -1;
        double best_score = -std::numeric_limits<double>::infinity();
        for (int rank = 0; rank < rank_window; ++rank) {
          const int id = indices[rank];
          if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
          const Vector3d target =
              id < static_cast<int>(ed_->averages_.size()) ? ed_->averages_[id] : ed_->points_[id];
          const Vector3d view = ed_->points_[id];
          Vector3d diff = target - pos;
          diff.z() = 0.0;
          const double dist_xy = diff.norm();
          double expansion_gain = 0.0;
          if (axis == 0 || axis == 1) {
            expansion_gain = fabs(diff[axis]);
          } else {
            Vector3d cur_dir = next_pos - pos;
            cur_dir.z() = 0.0;
            if (cur_dir.norm() < 1e-3) cur_dir = vel;
            cur_dir.z() = 0.0;
            if (cur_dir.norm() < 1e-3) cur_dir = Vector3d::UnitX();
            cur_dir.normalize();
            expansion_gain = fabs(diff.x() * (-cur_dir.y()) + diff.y() * cur_dir.x());
            current_gain = 0.0;
          }
          const double score = expansion_gain -
              ep_->global_expansion_bias_dist_weight_ * dist_xy -
              0.2 * static_cast<double>(rank);

          ROS_WARN(
              "FUEL refine expansion candidate rank=%d id=%d axis=%d avg=(%.3f, %.3f, %.3f) "
              "view=(%.3f, %.3f, %.3f) expansion_gain=%.3f dist_xy=%.3f score=%.3f",
              rank, id, axis, target.x(), target.y(), target.z(), view.x(), view.y(), view.z(),
              expansion_gain, dist_xy, score);

          if (score > best_score) {
            best_score = score;
            best_rank = rank;
            best_id = id;
          }
        }

        if (best_id >= 0) {
          const Vector3d biased_pos = ed_->points_[best_id];
          const double biased_yaw = ed_->yaws_[best_id];
          double best_gain = 0.0;
          if (axis == 0 || axis == 1) {
            const Vector3d target = best_id < static_cast<int>(ed_->averages_.size())
                ? ed_->averages_[best_id]
                : ed_->points_[best_id];
            best_gain = fabs((target - pos)[axis]);
          } else {
            best_gain = best_score;
          }
          if (best_gain >= current_gain + ep_->global_expansion_bias_min_gain_) {
            ROS_WARN(
                "FUEL refine expansion override: original=(%.3f, %.3f, %.3f) "
                "chosen_rank=%d chosen_id=%d chosen=(%.3f, %.3f, %.3f) axis=%d "
                "current_gain=%.3f chosen_gain=%.3f min_gain=%.3f",
                next_pos.x(), next_pos.y(), next_pos.z(), best_rank, best_id, biased_pos.x(),
                biased_pos.y(), biased_pos.z(), axis, current_gain, best_gain,
                ep_->global_expansion_bias_min_gain_);
            next_pos = biased_pos;
            next_yaw = biased_yaw;
            ed_->refined_points_[0] = next_pos;
            if (!refined_yaws.empty()) refined_yaws[0] = next_yaw;
          } else {
            ROS_WARN(
                "FUEL refine expansion kept local refine: axis=%d current_gain=%.3f "
                "best_gain=%.3f min_gain=%.3f",
                axis, current_gain, best_gain, ep_->global_expansion_bias_min_gain_);
          }
        }
    }

    if (ep_->coverage_expansion_enable_ && !indices.empty() && !ed_->refined_points_.empty()) {
      const int axis = ep_->coverage_expansion_axis_;
      const bool auto_axis = axis < 0;
      if (axis == 0 || axis == 1 || auto_axis) {
        const double local_goal_radius =
            max(0.5, planner_manager_->pp_.local_traj_len_ > 0.0
                         ? planner_manager_->pp_.local_traj_len_
                         : 5.0);
        if (!ed_->coverage_span_initialized_) {
          ed_->coverage_span_initialized_ = true;
          ed_->coverage_span_min_ = pos;
          ed_->coverage_span_max_ = pos;
        }
        for (int k = 0; k < 3; ++k) {
          ed_->coverage_span_min_[k] = min(ed_->coverage_span_min_[k], pos[k]);
          ed_->coverage_span_max_[k] = max(ed_->coverage_span_max_[k], pos[k]);
        }

        const int rank_window =
            min(static_cast<int>(indices.size()), max(1, ep_->coverage_expansion_rank_window_));
        Eigen::Vector3d map_origin, map_size;
        sdf_map_->getRegion(map_origin, map_size);
        const double map_size_x = max(1.0, fabs(map_size.x()));
        const double map_size_y = max(1.0, fabs(map_size.y()));
        const double span_x =
            max(0.0, ed_->coverage_span_max_.x() - ed_->coverage_span_min_.x());
        const double span_y =
            max(0.0, ed_->coverage_span_max_.y() - ed_->coverage_span_min_.y());
        const double coverage_x = min(1.0, span_x / map_size_x);
        const double coverage_y = min(1.0, span_y / map_size_y);
        const double deficit_x = max(0.05, 1.0 - coverage_x);
        const double deficit_y = max(0.05, 1.0 - coverage_y);

        if (auto_axis && !ed_->coverage_grid_initialized_) {
          ed_->coverage_grid_initialized_ = true;
          ed_->coverage_grid_origin_ = map_origin;
          ed_->coverage_grid_size_ = map_size;
          const double grid_res = max(0.2, ep_->coverage_expansion_grid_resolution_);
          ed_->coverage_grid_nx_ = max(1, static_cast<int>(ceil(map_size.x() / grid_res)));
          ed_->coverage_grid_ny_ = max(1, static_cast<int>(ceil(map_size.y() / grid_res)));
          ed_->coverage_grid_.assign(
              static_cast<size_t>(ed_->coverage_grid_nx_ * ed_->coverage_grid_ny_), 0);
          ROS_WARN(
              "[FUEL_COVERAGE_GRID] init origin=(%.3f, %.3f) size=(%.3f, %.3f) res=%.3f cells=%d x %d sensor_radius=%.3f horizon=%.3f",
              map_origin.x(), map_origin.y(), map_size.x(), map_size.y(), grid_res,
              ed_->coverage_grid_nx_, ed_->coverage_grid_ny_,
              ep_->coverage_expansion_sensor_radius_, ep_->coverage_expansion_project_horizon_);
        }

        auto grid_index = [&](const Vector3d& p, int& ix, int& iy) -> bool {
          if (!ed_->coverage_grid_initialized_) return false;
          const double grid_res = max(0.2, ep_->coverage_expansion_grid_resolution_);
          ix = static_cast<int>(floor((p.x() - ed_->coverage_grid_origin_.x()) / grid_res));
          iy = static_cast<int>(floor((p.y() - ed_->coverage_grid_origin_.y()) / grid_res));
          return ix >= 0 && iy >= 0 && ix < ed_->coverage_grid_nx_ && iy < ed_->coverage_grid_ny_;
        };

        auto add_sensor_cells = [&](const Vector3d& p) {
          if (!ed_->coverage_grid_initialized_) return 0;
          const double grid_res = max(0.2, ep_->coverage_expansion_grid_resolution_);
          const int r_cells = max(0, static_cast<int>(ceil(ep_->coverage_expansion_sensor_radius_ / grid_res)));
          int cx = 0;
          int cy = 0;
          if (!grid_index(p, cx, cy)) return 0;
          int added = 0;
          for (int ix = cx - r_cells; ix <= cx + r_cells; ++ix) {
            if (ix < 0 || ix >= ed_->coverage_grid_nx_) continue;
            const double px = ed_->coverage_grid_origin_.x() + (ix + 0.5) * grid_res;
            for (int iy = cy - r_cells; iy <= cy + r_cells; ++iy) {
              if (iy < 0 || iy >= ed_->coverage_grid_ny_) continue;
              const double py = ed_->coverage_grid_origin_.y() + (iy + 0.5) * grid_res;
              if (hypot(px - p.x(), py - p.y()) > ep_->coverage_expansion_sensor_radius_) continue;
              const int flat = iy * ed_->coverage_grid_nx_ + ix;
              if (ed_->coverage_grid_[flat] == 0) {
                ed_->coverage_grid_[flat] = 1;
                ++added;
              }
            }
          }
          return added;
        };

        auto estimate_new_sensor_cells = [&](const Vector3d& target) {
          if (!ed_->coverage_grid_initialized_) return 0;
          const double grid_res = max(0.2, ep_->coverage_expansion_grid_resolution_);
          const Vector3d diff = target - pos;
          const double dist_xy = diff.head<2>().norm();
          const double horizon = min(dist_xy, max(grid_res, ep_->coverage_expansion_project_horizon_));
          const int samples = max(1, static_cast<int>(ceil(horizon / grid_res)));
          const int r_cells = max(0, static_cast<int>(ceil(ep_->coverage_expansion_sensor_radius_ / grid_res)));
          std::set<int> candidate_cells;
          for (int s = 1; s <= samples; ++s) {
            const double ratio = dist_xy < 1e-3 ? 1.0 : (horizon / dist_xy) * static_cast<double>(s) / samples;
            const Vector3d p = pos + ratio * diff;
            int cx = 0;
            int cy = 0;
            if (!grid_index(p, cx, cy)) continue;
            for (int ix = cx - r_cells; ix <= cx + r_cells; ++ix) {
              if (ix < 0 || ix >= ed_->coverage_grid_nx_) continue;
              const double px = ed_->coverage_grid_origin_.x() + (ix + 0.5) * grid_res;
              for (int iy = cy - r_cells; iy <= cy + r_cells; ++iy) {
                if (iy < 0 || iy >= ed_->coverage_grid_ny_) continue;
                const double py = ed_->coverage_grid_origin_.y() + (iy + 0.5) * grid_res;
                if (hypot(px - p.x(), py - p.y()) > ep_->coverage_expansion_sensor_radius_) continue;
                const int flat = iy * ed_->coverage_grid_nx_ + ix;
                if (ed_->coverage_grid_[flat] == 0) candidate_cells.insert(flat);
              }
            }
          }
          return static_cast<int>(candidate_cells.size());
        };

        auto committedGoalForView = [&](const Vector3d& view, Vector3d& committed_goal,
                                        double& path_len) -> bool {
          committed_goal = view;
          path_len = 0.0;
          planner_manager_->path_finder_->reset();
          if (planner_manager_->path_finder_->search(pos, view) != Astar::REACH_END) {
            return false;
          }

          vector<Vector3d> candidate_path = planner_manager_->path_finder_->getPath();
          shortenPath(candidate_path);
          if (candidate_path.empty()) return false;

          path_len = Astar::pathLength(candidate_path);
          if (path_len <= local_goal_radius) return true;

          double len2 = 0.0;
          vector<Vector3d> truncated_path = { candidate_path.front() };
          for (int i = 1; i < static_cast<int>(candidate_path.size()) && len2 < local_goal_radius; ++i) {
            const Vector3d cur_pt = candidate_path[i];
            len2 += (cur_pt - truncated_path.back()).norm();
            truncated_path.push_back(cur_pt);
          }
          committed_goal = truncated_path.back();
          return true;
        };

        const int newly_observed_cells = auto_axis ? add_sensor_cells(pos) : 0;
        int observed_cells = 0;
        if (ed_->coverage_grid_initialized_) {
          observed_cells = static_cast<int>(std::count(ed_->coverage_grid_.begin(), ed_->coverage_grid_.end(), 1));
        }

        Vector3d uncovered_target = pos;
        bool has_uncovered_target = false;
        if (auto_axis && ed_->coverage_grid_initialized_ &&
            ep_->coverage_expansion_uncovered_target_weight_ > 0.0) {
          const double grid_res = max(0.2, ep_->coverage_expansion_grid_resolution_);
          const double local_uncovered_radius = max(
              ep_->coverage_expansion_sensor_radius_ + ep_->coverage_expansion_project_horizon_,
              local_goal_radius + 0.5 * ep_->coverage_expansion_sensor_radius_);
          const double min_uncovered_radius =
              max(grid_res, 0.35 * ep_->coverage_expansion_sensor_radius_);
          int target_ix = 0;
          int target_iy = 0;
          const bool target_in_grid =
              ed_->coverage_uncovered_target_initialized_ &&
              grid_index(ed_->coverage_uncovered_target_, target_ix, target_iy);
          const bool target_observed = target_in_grid &&
              ed_->coverage_grid_[target_iy * ed_->coverage_grid_nx_ + target_ix] != 0;
          const bool target_reached = ed_->coverage_uncovered_target_initialized_ &&
              (ed_->coverage_uncovered_target_.head<2>() - pos.head<2>()).norm() <=
                  ep_->coverage_expansion_sensor_radius_;
          const bool target_stale_far = ed_->coverage_uncovered_target_initialized_ &&
              (ed_->coverage_uncovered_target_.head<2>() - pos.head<2>()).norm() >
                  1.05 * local_uncovered_radius;
          if (!ed_->coverage_uncovered_target_initialized_ || !target_in_grid ||
              target_observed || target_reached || target_stale_far) {
            double best_local_uncovered_score = -std::numeric_limits<double>::infinity();
            double best_global_uncovered_dist_sq = -1.0;
            Vector3d global_uncovered_target = pos;
            bool has_global_uncovered_target = false;
            struct LocalUncoveredCandidate {
              double score;
              Vector3d cell;
            };
            vector<LocalUncoveredCandidate> local_uncovered_candidates;
            int unreachable_local_uncovered = 0;
            for (int iy = 0; iy < ed_->coverage_grid_ny_; ++iy) {
              for (int ix = 0; ix < ed_->coverage_grid_nx_; ++ix) {
                const int flat = iy * ed_->coverage_grid_nx_ + ix;
                if (ed_->coverage_grid_[flat] != 0) continue;
                Vector3d cell = pos;
                cell.x() = ed_->coverage_grid_origin_.x() + (ix + 0.5) * grid_res;
                cell.y() = ed_->coverage_grid_origin_.y() + (iy + 0.5) * grid_res;
                const double dist_xy = (cell.head<2>() - pos.head<2>()).norm();
                const double dist_sq = dist_xy * dist_xy;
                if (dist_sq > best_global_uncovered_dist_sq) {
                  best_global_uncovered_dist_sq = dist_sq;
                  global_uncovered_target = cell;
                  has_global_uncovered_target = true;
                }
                if (dist_xy < min_uncovered_radius || dist_xy > local_uncovered_radius) {
                  continue;
                }
                const double expand_high_x = cell.x() - ed_->coverage_span_max_.x();
                const double expand_low_x = ed_->coverage_span_min_.x() - cell.x();
                const double gain_x = max(0.0, max(expand_high_x, expand_low_x));
                const double expand_high_y = cell.y() - ed_->coverage_span_max_.y();
                const double expand_low_y = ed_->coverage_span_min_.y() - cell.y();
                const double gain_y = max(0.0, max(expand_high_y, expand_low_y));
                const double span_score =
                    100.0 * (gain_x / map_size_x * deficit_x + gain_y / map_size_y * deficit_y);
                const double local_score = span_score + 0.1 * dist_xy;
                if (ep_->coverage_expansion_direct_uncovered_fallback_) {
                  local_uncovered_candidates.push_back({local_score, cell});
                } else if (local_score > best_local_uncovered_score) {
                  best_local_uncovered_score = local_score;
                  uncovered_target = cell;
                  has_uncovered_target = true;
                }
              }
            }
            int reachability_check_limit = 0;
            if (ep_->coverage_expansion_direct_uncovered_fallback_) {
              std::sort(
                  local_uncovered_candidates.begin(), local_uncovered_candidates.end(),
                  [](const LocalUncoveredCandidate& a, const LocalUncoveredCandidate& b) {
                    return a.score > b.score;
                  });
              reachability_check_limit =
                  min(static_cast<int>(local_uncovered_candidates.size()), 20);
              for (int i = 0; i < reachability_check_limit; ++i) {
                Vector3d reachable_committed = local_uncovered_candidates[i].cell;
                double reachable_path_len = 0.0;
                if (!committedGoalForView(
                        local_uncovered_candidates[i].cell, reachable_committed, reachable_path_len)) {
                  ++unreachable_local_uncovered;
                  continue;
                }
                best_local_uncovered_score = local_uncovered_candidates[i].score;
                uncovered_target = local_uncovered_candidates[i].cell;
                has_uncovered_target = true;
                break;
              }
            }
            if (!has_uncovered_target && has_global_uncovered_target &&
                !ep_->coverage_expansion_direct_uncovered_fallback_) {
              uncovered_target = global_uncovered_target;
              has_uncovered_target = true;
            }
            if (has_uncovered_target) {
              ed_->coverage_uncovered_target_ = uncovered_target;
              ed_->coverage_uncovered_target_initialized_ = true;
              ROS_WARN(
                  "[FUEL_COVERAGE_EXPANSION] uncovered_target_refresh mode=%s local_radius=%.3f "
                  "min_radius=%.3f local_score=%.3f global_dist=%.3f target=(%.3f, %.3f) "
                  "unreachable_local=%d local_candidates=%zu reachability_checked=%d",
                  best_local_uncovered_score > -std::numeric_limits<double>::infinity() ? "local" : "global",
                  local_uncovered_radius, min_uncovered_radius, best_local_uncovered_score,
                  sqrt(max(0.0, best_global_uncovered_dist_sq)), uncovered_target.x(),
                  uncovered_target.y(), unreachable_local_uncovered,
                  local_uncovered_candidates.size(), reachability_check_limit);
            } else {
              ROS_WARN(
                  "[FUEL_COVERAGE_EXPANSION] uncovered_target_refresh skipped no_reachable_local "
                  "local_radius=%.3f min_radius=%.3f global_dist=%.3f unreachable_local=%d "
                  "local_candidates=%zu reachability_checked=%d direct_fallback=%s",
                  local_uncovered_radius, min_uncovered_radius,
                  sqrt(max(0.0, best_global_uncovered_dist_sq)), unreachable_local_uncovered,
                  local_uncovered_candidates.size(), reachability_check_limit,
                  ep_->coverage_expansion_direct_uncovered_fallback_ ? "true" : "false");
            }
          } else {
            uncovered_target = ed_->coverage_uncovered_target_;
            has_uncovered_target = true;
          }
          if (has_uncovered_target) {
            ROS_WARN(
                "[FUEL_COVERAGE_EXPANSION] uncovered_target=(%.3f, %.3f) "
                "dist_xy=%.3f observed=%d total=%zu target_weight=%.3f "
                "target_in_grid=%s target_observed=%s target_reached=%s target_stale_far=%s",
                uncovered_target.x(), uncovered_target.y(),
                (uncovered_target.head<2>() - pos.head<2>()).norm(), observed_cells,
                ed_->coverage_grid_.size(), ep_->coverage_expansion_uncovered_target_weight_,
                target_in_grid ? "true" : "false", target_observed ? "true" : "false",
                target_reached ? "true" : "false", target_stale_far ? "true" : "false");
          }
        }

        int best_rank = -1;
        int best_id = -1;
        double best_score = -std::numeric_limits<double>::infinity();
        double best_gain = 0.0;
        int best_new_sensor_cells = 0;
        double best_path_len = 0.0;
        Vector3d best_committed_goal = next_pos;

        for (int rank = 0; rank < rank_window; ++rank) {
            const int id = indices[rank];
            if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
            const Vector3d target =
                id < static_cast<int>(ed_->averages_.size()) ? ed_->averages_[id] : ed_->points_[id];
            Vector3d committed_goal = ed_->points_[id];
            double path_len_to_view = 0.0;
            bool reachable = false;
            if (auto_axis || ep_->coverage_expansion_score_committed_goal_) {
              reachable = committedGoalForView(ed_->points_[id], committed_goal, path_len_to_view);
            }
            const Vector3d score_target =
                (ep_->coverage_expansion_score_committed_goal_ ||
                 ep_->coverage_expansion_global_selector_) ? committed_goal : target;
            const Vector3d motion_score_target =
                (auto_axis && reachable) ? committed_goal : score_target;
            const double expand_high_x = score_target.x() - ed_->coverage_span_max_.x();
            const double expand_low_x = ed_->coverage_span_min_.x() - score_target.x();
            const double gain_x = max(0.0, max(expand_high_x, expand_low_x));
            const double expand_high_y = score_target.y() - ed_->coverage_span_max_.y();
            const double expand_low_y = ed_->coverage_span_min_.y() - score_target.y();
            const double gain_y = max(0.0, max(expand_high_y, expand_low_y));
            const int new_sensor_cells = auto_axis ? estimate_new_sensor_cells(score_target) : 0;
            const double span_gain =
                100.0 * (gain_x / map_size_x * deficit_x + gain_y / map_size_y * deficit_y);
            const double expansion_gain = auto_axis
                ? ep_->coverage_expansion_grid_weight_ * static_cast<double>(new_sensor_cells) +
                      ep_->coverage_expansion_span_weight_ * span_gain
                : (axis == 0 ? gain_x : gain_y);
            const double dist_xy = (score_target.head<2>() - pos.head<2>()).norm();
            double uncovered_target_progress = 0.0;
            if (has_uncovered_target) {
              uncovered_target_progress =
                  (uncovered_target.head<2>() - pos.head<2>()).norm() -
                  (uncovered_target.head<2>() - motion_score_target.head<2>()).norm();
            }
            const double score = expansion_gain -
                ep_->coverage_expansion_dist_weight_ * dist_xy -
                0.05 * static_cast<double>(rank) +
                ep_->coverage_expansion_uncovered_target_weight_ * uncovered_target_progress;
            const double span_min_for_log =
                auto_axis ? ed_->coverage_span_min_.y() : ed_->coverage_span_min_[axis];
            const double span_max_for_log =
                auto_axis ? ed_->coverage_span_max_.y() : ed_->coverage_span_max_[axis];

            if (!ep_->coverage_expansion_score_committed_goal_ &&
                expansion_gain >= ep_->coverage_expansion_min_gain_) {
              planner_manager_->path_finder_->reset();
              reachable =
                  planner_manager_->path_finder_->search(pos, ed_->points_[id]) == Astar::REACH_END;
            }

            if (ep_->coverage_expansion_log_candidates_) {
              ROS_WARN(
                  "[FUEL_COVERAGE_EXPANSION] candidate rank=%d id=%d axis=%d avg=(%.3f, %.3f, %.3f) "
                  "view=(%.3f, %.3f, %.3f) committed=(%.3f, %.3f, %.3f) path_len=%.3f local_radius=%.3f "
                  "sensor=(%.3f, %.3f, %.3f) span=[%.3f, %.3f] gain=%.3f dist_xy=%.3f score=%.3f reachable=%s score_committed=%s "
                  "gain_x=%.3f gain_y=%.3f coverage_x=%.3f coverage_y=%.3f grid_new=%d grid_seen=%d grid_added=%d "
                  "uncovered_progress=%.3f uncovered_weight=%.3f",
                  rank, id, axis, target.x(), target.y(), target.z(), ed_->points_[id].x(),
                  ed_->points_[id].y(), ed_->points_[id].z(), committed_goal.x(), committed_goal.y(),
                  committed_goal.z(), path_len_to_view, local_goal_radius, score_target.x(),
                  score_target.y(), score_target.z(), span_min_for_log,
                  span_max_for_log, expansion_gain, dist_xy, score, reachable ? "true" : "false",
                  ep_->coverage_expansion_score_committed_goal_ ? "true" : "false",
                  gain_x, gain_y, coverage_x, coverage_y,
                  new_sensor_cells, observed_cells, newly_observed_cells,
                  uncovered_target_progress, ep_->coverage_expansion_uncovered_target_weight_);
            }

            if (!reachable) continue;

            if (score > best_score) {
              best_score = score;
              best_rank = rank;
              best_id = id;
              best_gain = expansion_gain;
              best_new_sensor_cells = new_sensor_cells;
              best_path_len = path_len_to_view;
              best_committed_goal = committed_goal;
            }
          }

          if (best_id >= 0 && best_gain >= ep_->coverage_expansion_min_gain_) {
            const Vector3d expanded_pos =
                ep_->coverage_expansion_global_selector_ ? best_committed_goal : ed_->points_[best_id];
            const double expanded_yaw = ed_->yaws_[best_id];
            const double span_before_min_for_log =
                auto_axis ? ed_->coverage_span_min_.y() : ed_->coverage_span_min_[axis];
            const double span_before_max_for_log =
                auto_axis ? ed_->coverage_span_max_.y() : ed_->coverage_span_max_[axis];
            ROS_WARN(
                "[FUEL_COVERAGE_EXPANSION] override: original=(%.3f, %.3f, %.3f) "
                "chosen_rank=%d chosen_id=%d chosen=(%.3f, %.3f, %.3f) axis=%d "
                "gain=%.3f min_gain=%.3f score=%.3f span_before=[%.3f, %.3f]",
                next_pos.x(), next_pos.y(), next_pos.z(), best_rank, best_id, expanded_pos.x(),
                expanded_pos.y(), expanded_pos.z(), axis, best_gain, ep_->coverage_expansion_min_gain_,
                best_score, span_before_min_for_log, span_before_max_for_log);
            next_pos = expanded_pos;
            next_yaw = expanded_yaw;
            ed_->refined_points_[0] = next_pos;
            if (!refined_yaws.empty()) refined_yaws[0] = next_yaw;
            if (ep_->coverage_expansion_global_selector_) {
              ROS_WARN(
                  "[FUEL_GLOBAL_SELECTOR] selected rank=%d id=%d committed=(%.3f, %.3f, %.3f) "
                  "view=(%.3f, %.3f, %.3f) new_sensor_cells=%d path_len=%.3f "
                  "score=%.3f gain=%.3f observed=%d total=%zu",
                  best_rank, best_id, best_committed_goal.x(), best_committed_goal.y(),
                  best_committed_goal.z(), ed_->points_[best_id].x(), ed_->points_[best_id].y(),
                  ed_->points_[best_id].z(), best_new_sensor_cells, best_path_len,
                  best_score, best_gain, observed_cells, ed_->coverage_grid_.size());
            }
          } else {
            ROS_WARN(
                "[FUEL_COVERAGE_EXPANSION] keep local refine: axis=%d best_gain=%.3f min_gain=%.3f "
                "best_score=%.3f span=[%.3f, %.3f]",
                axis, best_gain, ep_->coverage_expansion_min_gain_, best_score,
                auto_axis ? ed_->coverage_span_min_.y() : ed_->coverage_span_min_[axis],
                auto_axis ? ed_->coverage_span_max_.y() : ed_->coverage_span_max_[axis]);
          }

          if (auto_axis && ep_->coverage_expansion_direct_uncovered_fallback_ &&
              has_uncovered_target) {
            Vector3d fallback_goal = uncovered_target;
            fallback_goal.z() = pos.z();
            double fallback_path_len = 0.0;
            Vector3d fallback_committed = fallback_goal;
            if (committedGoalForView(fallback_goal, fallback_committed, fallback_path_len)) {
              const double current_to_uncovered =
                  (uncovered_target.head<2>() - pos.head<2>()).norm();
              const double fallback_to_uncovered =
                  (uncovered_target.head<2>() - fallback_committed.head<2>()).norm();
              const double progress = current_to_uncovered - fallback_to_uncovered;
              if (progress >= ep_->coverage_expansion_min_gain_) {
                ROS_WARN(
                    "[FUEL_COVERAGE_EXPANSION] direct_uncovered_fallback target=(%.3f, %.3f, %.3f) "
                    "committed=(%.3f, %.3f, %.3f) path_len=%.3f progress=%.3f min_gain=%.3f",
                    fallback_goal.x(), fallback_goal.y(), fallback_goal.z(),
                    fallback_committed.x(), fallback_committed.y(), fallback_committed.z(),
                    fallback_path_len, progress, ep_->coverage_expansion_min_gain_);
                next_pos = fallback_committed;
                next_yaw = atan2(uncovered_target.y() - pos.y(), uncovered_target.x() - pos.x());
                ed_->refined_points_[0] = next_pos;
                if (!refined_yaws.empty()) refined_yaws[0] = next_yaw;
              } else {
                ROS_WARN(
                    "[FUEL_COVERAGE_EXPANSION] direct_uncovered_fallback_skip progress=%.3f min_gain=%.3f "
                    "target=(%.3f, %.3f, %.3f) committed=(%.3f, %.3f, %.3f)",
                    progress, ep_->coverage_expansion_min_gain_, fallback_goal.x(), fallback_goal.y(),
                    fallback_goal.z(), fallback_committed.x(), fallback_committed.y(),
                    fallback_committed.z());
              }
            } else {
              ROS_WARN(
                  "[FUEL_COVERAGE_EXPANSION] direct_uncovered_fallback_no_path target=(%.3f, %.3f, %.3f)",
                  fallback_goal.x(), fallback_goal.y(), fallback_goal.z());
            }
          }
        }
      }

      ROS_WARN(
          "[FUEL_COVERAGE_EXPANSION] selected_without_span_commit x=[%.3f, %.3f] y=[%.3f, %.3f] selected=(%.3f, %.3f, %.3f)",
          ed_->coverage_span_min_.x(), ed_->coverage_span_max_.x(), ed_->coverage_span_min_.y(),
          ed_->coverage_span_max_.y(), next_pos.x(), next_pos.y(), next_pos.z());

      // Get marker for view visualization
      for (int i = 0; i < ed_->refined_points_.size(); ++i) {
        Vector3d view =
            ed_->refined_points_[i] + 2.0 * Vector3d(cos(refined_yaws[i]), sin(refined_yaws[i]), 0);
        ed_->refined_views_.push_back(view);
      }
      ed_->refined_views1_.clear();
      ed_->refined_views2_.clear();
      for (int i = 0; i < ed_->refined_points_.size(); ++i) {
        vector<Vector3d> v1, v2;
        frontier_finder_->percep_utils_->setPose(ed_->refined_points_[i], refined_yaws[i]);
        frontier_finder_->percep_utils_->getFOV(v1, v2);
        ed_->refined_views1_.insert(ed_->refined_views1_.end(), v1.begin(), v1.end());
        ed_->refined_views2_.insert(ed_->refined_views2_.end(), v2.begin(), v2.end());
      }
      double local_time = (ros::Time::now() - t1).toSec();
      ROS_WARN("Local refine time: %lf", local_time);

    } else {
      // Choose the next viewpoint from global tour
      next_pos = ed_->points_[indices[0]];
      next_yaw = ed_->yaws_[indices[0]];
    }
  } else if (ed_->points_.size() == 1) {
    // Only 1 destination, no need to find global tour through TSP
    frontier_finder_->updateFrontierCostMatrix();
    ed_->global_tour_ = { pos, ed_->points_[0] };
    ed_->refined_tour_.clear();
    ed_->refined_views1_.clear();
    ed_->refined_views2_.clear();

    if (ep_->refine_local_) {
      // Find the min cost viewpoint for next frontier
      ed_->refined_ids_ = { 0 };
      ed_->unrefined_points_ = { ed_->points_[0] };
      ed_->n_points_.clear();
      vector<vector<double>> n_yaws;
      frontier_finder_->getViewpointsInfo(
          pos, { 0 }, ep_->top_view_num_, ep_->max_decay_, ed_->n_points_, n_yaws);

      double min_cost = 100000;
      int min_cost_id = -1;
      vector<Vector3d> tmp_path;
      for (int i = 0; i < ed_->n_points_[0].size(); ++i) {
        auto tmp_cost = ViewNode::computeCost(
            pos, ed_->n_points_[0][i], yaw[0], n_yaws[0][i], vel, yaw[1], tmp_path);
        if (tmp_cost < min_cost) {
          min_cost = tmp_cost;
          min_cost_id = i;
        }
      }
      next_pos = ed_->n_points_[0][min_cost_id];
      next_yaw = n_yaws[0][min_cost_id];
      ed_->refined_points_ = { next_pos };
      ed_->refined_views_ = { next_pos + 2.0 * Vector3d(cos(next_yaw), sin(next_yaw), 0) };
    } else {
      next_pos = ed_->points_[0];
      next_yaw = ed_->yaws_[0];
    }
  } else
    ROS_ERROR("Empty destination.");

  std::cout << "Next view: " << next_pos.transpose() << ", " << next_yaw << std::endl;
  stage("before_trajectory_generation");

  // Plan trajectory (position and yaw) to the next viewpoint
  t1 = ros::Time::now();

  // Compute time lower bound of yaw and use in trajectory generation
  double diff = fabs(next_yaw - yaw[0]);
  double time_lb = min(diff, 2 * M_PI - diff) / ViewNode::yd_;

  // Generate trajectory of x,y,z
  planner_manager_->path_finder_->reset();
  if (planner_manager_->path_finder_->search(pos, next_pos) != Astar::REACH_END) {
    ROS_ERROR("No path to next viewpoint");
    return FAIL;
  }
  ed_->path_next_goal_ = planner_manager_->path_finder_->getPath();
  shortenPath(ed_->path_next_goal_);
  if (ed_->path_next_goal_.empty()) {
    ROS_ERROR("[FUEL_REPLAN_CONTINUITY] A* returned an empty path after shortening");
    return FAIL;
  }
  const double start_gap = (ed_->path_next_goal_.front() - pos).norm();
  if (start_gap > 1e-4) {
    ROS_WARN("[FUEL_REPLAN_CONTINUITY] Prepending predicted start; A* gap=%.6f m", start_gap);
    ed_->path_next_goal_.insert(ed_->path_next_goal_.begin(), pos);
  }

  const double radius_far =
      max(0.5, planner_manager_->pp_.local_traj_len_ > 0.0 ? planner_manager_->pp_.local_traj_len_ : 5.0);
  const double radius_close = 1.5;
  const double len = Astar::pathLength(ed_->path_next_goal_);
  if (len < radius_close) {
    // Next viewpoint is very close, no need to search kinodynamic path, just use waypoints-based
    // optimization
    planner_manager_->planExploreTraj(ed_->path_next_goal_, vel, acc, time_lb);
    stage("after_waypoint_trajectory");
    ed_->next_goal_ = next_pos;

  } else if (len > radius_far) {
    // Next viewpoint is far away, select intermediate goal on geometric path (this also deal with
    // dead end)
    std::cout << "Far goal." << std::endl;
    double len2 = 0.0;
    vector<Eigen::Vector3d> truncated_path = { ed_->path_next_goal_.front() };
    for (int i = 1; i < ed_->path_next_goal_.size() && len2 < radius_far; ++i) {
      auto cur_pt = ed_->path_next_goal_[i];
      len2 += (cur_pt - truncated_path.back()).norm();
      truncated_path.push_back(cur_pt);
    }
    ed_->next_goal_ = truncated_path.back();
    planner_manager_->planExploreTraj(truncated_path, vel, acc, time_lb);
    stage("after_truncated_trajectory");
    // if (!planner_manager_->kinodynamicReplan(
    //         pos, vel, acc, ed_->next_goal_, Vector3d(0, 0, 0), time_lb))
    //   return FAIL;
    // ed_->kino_path_ = planner_manager_->kino_path_finder_->getKinoTraj(0.02);
  } else {
    // Search kino path to exactly next viewpoint and optimize
    std::cout << "Mid goal" << std::endl;
    ed_->next_goal_ = next_pos;

    if (!planner_manager_->kinodynamicReplan(
            pos, vel, acc, ed_->next_goal_, Vector3d(0, 0, 0), time_lb))
      return FAIL;
    stage("after_kinodynamic_replan");
  }

  if (ep_->coverage_expansion_enable_ && ed_->coverage_span_initialized_) {
    for (int k = 0; k < 3; ++k) {
      ed_->coverage_span_min_[k] = min(ed_->coverage_span_min_[k], ed_->next_goal_[k]);
      ed_->coverage_span_max_[k] = max(ed_->coverage_span_max_[k], ed_->next_goal_[k]);
    }
    ROS_WARN(
        "[FUEL_COVERAGE_EXPANSION] span_after_goal x=[%.3f, %.3f] y=[%.3f, %.3f] "
        "selected=(%.3f, %.3f, %.3f) committed_goal=(%.3f, %.3f, %.3f)",
        ed_->coverage_span_min_.x(), ed_->coverage_span_max_.x(), ed_->coverage_span_min_.y(),
        ed_->coverage_span_max_.y(), next_pos.x(), next_pos.y(), next_pos.z(), ed_->next_goal_.x(),
        ed_->next_goal_.y(), ed_->next_goal_.z());
  }

  if (planner_manager_->local_data_.position_traj_.getTimeSum() < time_lb - 0.1)
    ROS_ERROR("Lower bound not satified!");

  planner_manager_->planYawExplore(yaw, next_yaw, true, ep_->relax_time_);
  stage("after_yaw_plan");

  double traj_plan_time = (ros::Time::now() - t1).toSec();
  t1 = ros::Time::now();

  double yaw_time = (ros::Time::now() - t1).toSec();
  ROS_WARN("Traj: %lf, yaw: %lf", traj_plan_time, yaw_time);
  double total = (ros::Time::now() - t2).toSec();
  ROS_WARN("Total time: %lf", total);
  ROS_ERROR_COND(total > 0.1, "Total time too long!!!");

  return SUCCEED;
}

void FastExplorationManager::shortenPath(vector<Vector3d>& path) {
  if (path.empty()) {
    ROS_ERROR("Empty path to shorten");
    return;
  }
  // Shorten the tour, only critical intermediate points are reserved.
  const double dist_thresh = 3.0;
  vector<Vector3d> short_tour = { path.front() };
  for (int i = 1; i < path.size() - 1; ++i) {
    if ((path[i] - short_tour.back()).norm() > dist_thresh)
      short_tour.push_back(path[i]);
    else {
      // Add waypoints to shorten path only to avoid collision
      ViewNode::caster_->input(short_tour.back(), path[i + 1]);
      Eigen::Vector3i idx;
      while (ViewNode::caster_->nextId(idx) && ros::ok()) {
        if (edt_environment_->sdf_map_->getInflateOccupancy(idx) == 1 ||
            edt_environment_->sdf_map_->getOccupancy(idx) == SDFMap::UNKNOWN) {
          short_tour.push_back(path[i]);
          break;
        }
      }
    }
  }
  if ((path.back() - short_tour.back()).norm() > 1e-3) short_tour.push_back(path.back());

  // Ensure at least three points in the path
  if (short_tour.size() == 2)
    short_tour.insert(short_tour.begin() + 1, 0.5 * (short_tour[0] + short_tour[1]));
  path = short_tour;
}

void FastExplorationManager::findGlobalTour(
    const Vector3d& cur_pos, const Vector3d& cur_vel, const Vector3d cur_yaw,
    vector<int>& indices) {
  auto t1 = ros::Time::now();

  // Get cost matrix for current state and clusters
  Eigen::MatrixXd cost_mat;
  frontier_finder_->updateFrontierCostMatrix();
  frontier_finder_->getFullCostMatrix(cur_pos, cur_vel, cur_yaw, cost_mat);
  const int dimension = cost_mat.rows();

  double mat_time = (ros::Time::now() - t1).toSec();
  t1 = ros::Time::now();

  // Write params and cost matrix to problem file
  ofstream prob_file(ep_->tsp_dir_ + "/single.tsp");
  // Problem specification part, follow the format of TSPLIB

  string prob_spec = "NAME : single\nTYPE : ATSP\nDIMENSION : " + to_string(dimension) +
      "\nEDGE_WEIGHT_TYPE : "
      "EXPLICIT\nEDGE_WEIGHT_FORMAT : FULL_MATRIX\nEDGE_WEIGHT_SECTION\n";

  // string prob_spec = "NAME : single\nTYPE : TSP\nDIMENSION : " + to_string(dimension) +
  //     "\nEDGE_WEIGHT_TYPE : "
  //     "EXPLICIT\nEDGE_WEIGHT_FORMAT : LOWER_ROW\nEDGE_WEIGHT_SECTION\n";

  prob_file << prob_spec;
  // prob_file << "TYPE : TSP\n";
  // prob_file << "EDGE_WEIGHT_FORMAT : LOWER_ROW\n";
  // Problem data part
  const int scale = 100;
  if (false) {
    // Use symmetric TSP
    for (int i = 1; i < dimension; ++i) {
      for (int j = 0; j < i; ++j) {
        int int_cost = cost_mat(i, j) * scale;
        prob_file << int_cost << " ";
      }
      prob_file << "\n";
    }

  } else {
    // Use Asymmetric TSP
    for (int i = 0; i < dimension; ++i) {
      for (int j = 0; j < dimension; ++j) {
        int int_cost = cost_mat(i, j) * scale;
        prob_file << int_cost << " ";
      }
      prob_file << "\n";
    }
  }

  prob_file << "EOF";
  prob_file.close();

  // Call LKH TSP solver
  solveTSPLKH((ep_->tsp_dir_ + "/single.par").c_str());

  // Read optimal tour from the tour section of result file
  ifstream res_file(ep_->tsp_dir_ + "/single.txt");
  string res;
  while (getline(res_file, res)) {
    // Go to tour section
    if (res.compare("TOUR_SECTION") == 0) break;
  }

  if (false) {
    // Read path for Symmetric TSP formulation
    getline(res_file, res);  // Skip current pose
    getline(res_file, res);
    int id = stoi(res);
    bool rev = (id == dimension);  // The next node is virutal depot?

    while (id != -1) {
      indices.push_back(id - 2);
      getline(res_file, res);
      id = stoi(res);
    }
    if (rev) reverse(indices.begin(), indices.end());
    indices.pop_back();  // Remove the depot

  } else {
    // Read path for ATSP formulation
    while (getline(res_file, res)) {
      // Read indices of frontiers in optimal tour
      int id = stoi(res);
      if (id == 1)  // Ignore the current state
        continue;
      if (id == -1) break;
      indices.push_back(id - 2);  // Idx of solver-2 == Idx of frontier
    }
  }

  res_file.close();

  // Get the path of optimal tour from path matrix
  frontier_finder_->getPathForTour(cur_pos, indices, ed_->global_tour_);

  double tsp_time = (ros::Time::now() - t1).toSec();
  ROS_WARN("Cost mat: %lf, TSP: %lf", mat_time, tsp_time);
}

void FastExplorationManager::refineLocalTour(
    const Vector3d& cur_pos, const Vector3d& cur_vel, const Vector3d& cur_yaw,
    const vector<vector<Vector3d>>& n_points, const vector<vector<double>>& n_yaws,
    vector<Vector3d>& refined_pts, vector<double>& refined_yaws) {
  double create_time, search_time, parse_time;
  auto t1 = ros::Time::now();

  // Create graph for viewpoints selection
  GraphSearch<ViewNode> g_search;
  vector<ViewNode::Ptr> last_group, cur_group;

  // Add the current state
  ViewNode::Ptr first(new ViewNode(cur_pos, cur_yaw[0]));
  first->vel_ = cur_vel;
  g_search.addNode(first);
  last_group.push_back(first);
  ViewNode::Ptr final_node;

  // Add viewpoints
  std::cout << "Local tour graph: ";
  for (int i = 0; i < n_points.size(); ++i) {
    // Create nodes for viewpoints of one frontier
    for (int j = 0; j < n_points[i].size(); ++j) {
      ViewNode::Ptr node(new ViewNode(n_points[i][j], n_yaws[i][j]));
      g_search.addNode(node);
      // Connect a node to nodes in last group
      for (auto nd : last_group)
        g_search.addEdge(nd->id_, node->id_);
      cur_group.push_back(node);

      // Only keep the first viewpoint of the last local frontier
      if (i == n_points.size() - 1) {
        final_node = node;
        break;
      }
    }
    // Store nodes for this group for connecting edges
    std::cout << cur_group.size() << ", ";
    last_group = cur_group;
    cur_group.clear();
  }
  std::cout << "" << std::endl;
  create_time = (ros::Time::now() - t1).toSec();
  t1 = ros::Time::now();

  // Search optimal sequence
  vector<ViewNode::Ptr> path;
  g_search.DijkstraSearch(first->id_, final_node->id_, path);

  search_time = (ros::Time::now() - t1).toSec();
  t1 = ros::Time::now();

  // Return searched sequence
  for (int i = 1; i < path.size(); ++i) {
    refined_pts.push_back(path[i]->pos_);
    refined_yaws.push_back(path[i]->yaw_);
  }

  // Extract optimal local tour (for visualization)
  ed_->refined_tour_.clear();
  ed_->refined_tour_.push_back(cur_pos);
  ViewNode::astar_->lambda_heu_ = 1.0;
  ViewNode::astar_->setResolution(0.2);
  for (auto pt : refined_pts) {
    vector<Vector3d> path;
    if (ViewNode::searchPath(ed_->refined_tour_.back(), pt, path))
      ed_->refined_tour_.insert(ed_->refined_tour_.end(), path.begin(), path.end());
    else
      ed_->refined_tour_.push_back(pt);
  }
  ViewNode::astar_->lambda_heu_ = 10000;

  parse_time = (ros::Time::now() - t1).toSec();
  // ROS_WARN("create: %lf, search: %lf, parse: %lf", create_time, search_time, parse_time);
}

}  // namespace fast_planner
