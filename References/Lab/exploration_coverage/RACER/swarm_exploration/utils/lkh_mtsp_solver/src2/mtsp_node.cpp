#include <ros/ros.h>
#include <std_msgs/Empty.h>
#include <string>
#include <cstdlib>
#include <limits.h>
#include <sys/wait.h>
#include <unistd.h>

#include <lkh_mtsp_solver/SolveMTSP.h>

using std::string;

std::string mtsp_dir1_;
std::string mtsp_dir2_;
std::string mtsp_dir3_;
int drone_id_, problem_id_;

std::string shellQuote(const std::string& value) {
  std::string quoted = "'";
  for (const char ch : value) {
    if (ch == '\'') {
      quoted += "'\\''";
    } else {
      quoted += ch;
    }
  }
  quoted += "'";
  return quoted;
}

std::string executableDir() {
  char path[PATH_MAX];
  const ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1);
  if (len <= 0) return ".";
  path[len] = '\0';
  std::string exe_path(path);
  const std::size_t slash = exe_path.find_last_of('/');
  if (slash == std::string::npos) return ".";
  return exe_path.substr(0, slash);
}

bool runLKHProcess(const std::string& parameter_file) {
  const std::string executable = executableDir() + "/lkh_mtsp_solver_lkh3";
  const std::string command = shellQuote(executable) + " " + shellQuote(parameter_file);
  const int status = std::system(command.c_str());
  if (status == -1) {
    ROS_ERROR("Failed to start LKH3 process for %s", parameter_file.c_str());
    return false;
  }
  if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
    ROS_ERROR("LKH3 process failed for %s with status %d", parameter_file.c_str(), status);
    return false;
  }
  return true;
}

bool mtspCallback(
    lkh_mtsp_solver::SolveMTSP::Request& req, lkh_mtsp_solver::SolveMTSP::Response& res) {

  bool ok = false;
  if (req.prob == 1)
    ok = runLKHProcess(mtsp_dir1_);
  else if (req.prob == 2)
    ok = runLKHProcess(mtsp_dir2_);
  else if (req.prob == 3)
    ok = runLKHProcess(mtsp_dir3_);
  else
    ROS_ERROR("Unsupported LKH problem id %u", req.prob);

  // ROS_INFO("MTSP server %d solve prob", drone_id_);
  res.empty = ok ? 0 : 1;
  return ok;
}

int main(int argc, char** argv) {
  ros::init(argc, argv, "mtsp_node");
  ros::NodeHandle nh("~");

  // Read mtsp file dir
  std::string mtsp_dir;
  nh.param("exploration/mtsp_dir", mtsp_dir, std::string("null"));
  nh.param("exploration/drone_id", drone_id_, 1);
  nh.param("exploration/problem_id", problem_id_, 1);

  mtsp_dir1_ = mtsp_dir + "/amtsp_" + std::to_string(drone_id_) + ".par";
  mtsp_dir2_ = mtsp_dir + "/amtsp2_" + std::to_string(drone_id_) + ".par";
  mtsp_dir3_ = mtsp_dir + "/amtsp3_" + std::to_string(drone_id_) + ".par";

  string service_name;
  if (problem_id_ == 1) {  // TSP
    service_name = "/solve_tsp_" + std::to_string(drone_id_);
  } else if (problem_id_ == 2) {  // ACVRP
    service_name = "/solve_acvrp_" + std::to_string(drone_id_);
  }
  ros::ServiceServer mtsp_server = nh.advertiseService(service_name, mtspCallback);

  ROS_WARN("MTSP server %d is ready.", drone_id_);
  ros::spin();

  return 1;
}
