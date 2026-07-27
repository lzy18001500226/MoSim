#ifndef _EXPL_DATA_H_
#define _EXPL_DATA_H_

#include <Eigen/Eigen>
#include <vector>
#include <bspline/Bspline.h>

using std::vector;
using Eigen::Vector3d;

namespace fast_planner {
struct FSMData {
  // FSM data
  bool trigger_, have_odom_, static_state_;
  vector<string> state_str_;

  Eigen::Vector3d odom_pos_, odom_vel_;  // odometry state
  Eigen::Quaterniond odom_orient_;
  double odom_yaw_;

  Eigen::Vector3d start_pt_, start_vel_, start_acc_, start_yaw_;  // start state
  vector<Eigen::Vector3d> start_poss;
  bspline::Bspline newest_traj_;
};

struct FSMParam {
  double replan_thresh1_;
  double replan_thresh2_;
  double replan_thresh3_;
  double replan_time_;  // second
};

struct ExplorationData {
  vector<vector<Vector3d>> frontiers_;
  vector<vector<Vector3d>> dead_frontiers_;
  vector<pair<Vector3d, Vector3d>> frontier_boxes_;
  vector<Vector3d> points_;
  vector<Vector3d> averages_;
  vector<Vector3d> views_;
  vector<double> yaws_;
  vector<Vector3d> global_tour_;

  vector<int> refined_ids_;
  vector<vector<Vector3d>> n_points_;
  vector<Vector3d> unrefined_points_;
  vector<Vector3d> refined_points_;
  vector<Vector3d> refined_views_;  // points + dir(yaw)
  vector<Vector3d> refined_views1_, refined_views2_;
  vector<Vector3d> refined_tour_;

  Vector3d next_goal_;
  vector<Vector3d> path_next_goal_;

  // viewpoint planning
  // vector<Vector4d> views_;
  vector<Vector3d> views_vis1_, views_vis2_;
  vector<Vector3d> centers_, scales_;

  bool coverage_span_initialized_ = false;
  Vector3d coverage_span_min_ = Vector3d::Zero();
  Vector3d coverage_span_max_ = Vector3d::Zero();
  bool coverage_grid_initialized_ = false;
  Vector3d coverage_grid_origin_ = Vector3d::Zero();
  Vector3d coverage_grid_size_ = Vector3d::Zero();
  int coverage_grid_nx_ = 0;
  int coverage_grid_ny_ = 0;
  vector<unsigned char> coverage_grid_;
  bool coverage_uncovered_target_initialized_ = false;
  Vector3d coverage_uncovered_target_ = Vector3d::Zero();
};

struct ExplorationParam {
  // params
  bool refine_local_;
  int refined_num_;
  double refined_radius_;
  int top_view_num_;
  double max_decay_;
  string tsp_dir_;  // resource dir of tsp solver
  double relax_time_;
  bool near_frontier_escape_enable_;
  double near_frontier_escape_distance_;
  double near_frontier_escape_max_speed_;
  double near_frontier_escape_alternative_distance_;
  bool global_expansion_bias_enable_;
  int global_expansion_bias_rank_window_;
  double global_expansion_bias_dist_weight_;
  double global_expansion_bias_lateral_weight_;
  int global_expansion_bias_axis_;
  double global_expansion_bias_min_gain_;
  bool global_expansion_bias_override_refine_;
  bool coverage_expansion_enable_;
  int coverage_expansion_axis_;
  int coverage_expansion_rank_window_;
  double coverage_expansion_min_gain_;
  double coverage_expansion_dist_weight_;
  double coverage_expansion_grid_resolution_;
  double coverage_expansion_sensor_radius_;
  double coverage_expansion_project_horizon_;
  double coverage_expansion_grid_weight_;
  double coverage_expansion_span_weight_;
  double coverage_expansion_uncovered_target_weight_;
  bool coverage_expansion_score_committed_goal_;
  bool coverage_expansion_direct_uncovered_fallback_;
  bool coverage_expansion_global_selector_;
  bool coverage_expansion_log_candidates_;
};

}  // namespace fast_planner

#endif
