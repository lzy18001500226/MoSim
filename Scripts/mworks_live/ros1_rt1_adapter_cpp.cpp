#include <arpa/inet.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <deque>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include <mavros_msgs/AttitudeTarget.h>
#include <mavros_msgs/State.h>
#include <nav_msgs/Odometry.h>
#include <quadrotor_msgs/PositionCommand.h>
#include <ros/ros.h>
#include <rosgraph_msgs/Clock.h>
#include <sensor_msgs/Imu.h>
#include <std_msgs/String.h>

#include <gazebo/common/Time.hh>
#include <gazebo/gazebo_client.hh>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/transport/transport.hh>

namespace {

constexpr uint32_t kStateMagic = 0x4D525431;
constexpr uint32_t kCommandMagic = 0x4D524331;
constexpr uint16_t kProtocolVersion = 1;
constexpr uint16_t kFlagArmed = 1U << 0U;
constexpr uint16_t kFlagStateValid = 1U << 1U;
constexpr uint16_t kFlagReferenceValid = 1U << 2U;
constexpr uint16_t kFlagOutputValid = 1U << 3U;
constexpr size_t kRunIdSize = 64;
constexpr size_t kMaxSamples = 20000;
constexpr size_t kIpv4UdpHeaderBytes = 28;

#pragma pack(push, 1)
struct WireHeader {
  uint32_t magic;
  uint16_t version;
  uint16_t flags;
  uint32_t sequence;
  uint32_t related_sequence;
  uint64_t source_stamp_ns;
  uint64_t produced_or_receive_ns;
  uint64_t valid_until_ns;
  char run_id[kRunIdSize];
};

struct StateReferenceWire {
  WireHeader header;
  double values[24];
};

struct CommandWire {
  WireHeader header;
  double q_xyzw[4];
  double collective_thrust_n;
  uint32_t saturation_mask;
  uint32_t controller_status;
};
#pragma pack(pop)

static_assert(sizeof(WireHeader) == 104, "RT1 header contract drift");
static_assert(sizeof(StateReferenceWire) == 296, "RT1 state frame contract drift");
static_assert(sizeof(CommandWire) == 152, "RT1 command frame contract drift");

uint64_t monotonicNs() {
  timespec value{};
  clock_gettime(CLOCK_MONOTONIC, &value);
  return static_cast<uint64_t>(value.tv_sec) * 1000000000ULL + value.tv_nsec;
}

double unixSeconds() {
  return std::chrono::duration<double>(
             std::chrono::system_clock::now().time_since_epoch())
      .count();
}

std::string jsonEscape(const std::string& value) {
  std::ostringstream out;
  for (const char ch : value) {
    switch (ch) {
      case '\\': out << "\\\\"; break;
      case '"': out << "\\\""; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default: out << ch;
    }
  }
  return out.str();
}

template <typename T>
void appendBounded(std::deque<T>& values, T value) {
  if (values.size() >= kMaxSamples) values.pop_front();
  values.push_back(value);
}

std::optional<double> percentile(const std::deque<double>& values, double q) {
  if (values.empty()) return std::nullopt;
  std::vector<double> ordered(values.begin(), values.end());
  std::sort(ordered.begin(), ordered.end());
  const size_t index = std::min(
      ordered.size() - 1,
      static_cast<size_t>(std::max(0.0, std::ceil(q * ordered.size()) - 1.0)));
  return ordered[index];
}

std::optional<double> populationStddev(const std::deque<double>& values) {
  if (values.size() < 2) return std::nullopt;
  double sum = 0.0;
  for (const double value : values) sum += value;
  const double mean = sum / values.size();
  double squares = 0.0;
  for (const double value : values) {
    const double delta = value - mean;
    squares += delta * delta;
  }
  return std::sqrt(squares / values.size());
}

std::string optionalNumber(const std::optional<double>& value) {
  if (!value.has_value()) return "null";
  std::ostringstream out;
  out << std::setprecision(12) << *value;
  return out.str();
}

// Mirrors Config/plant/sunray150_virtual_px4_classic_profile.json. C++ keeps
// compile-time defaults because the ROS1 runtime does not load project JSON.
constexpr double kSunray150VirtualPx4ClassicMassKg = 1.0;
constexpr double kSunray150VirtualPx4ClassicGravityMps2 = 9.80665;
constexpr double kSunray150VirtualPx4ClassicHoverPercentage = 0.37;

struct Args {
  std::string run_id;
  std::string result_dir;
  std::string mworks_host = "127.0.0.1";
  int mworks_port = 49020;
  std::string bind_host = "0.0.0.0";
  double rate_hz = 200.0;
  double status_rate_hz = 2.0;
  double deadline_ms = 10.0;
  double command_stale_ms = 50.0;
  double failsafe_escalation_ms = 100.0;
  int consecutive_deadline_misses = 3;
  int minimum_shadow_commands = 250;
  int max_receive_batch = 32;
  double trace_sample_rate_hz = 10.0;
  std::string time_mode = "wall_clock";
  int gazebo_steps_per_command = 5;
  uint64_t gazebo_step_size_ns = 1000000;
  double gazebo_bootstrap_timeout_s = 30.0;
  double sync_state_resend_ms = 25.0;
  bool allow_active_takeover = false;
  bool auto_activate_ground = false;
  bool allow_ground_hold_reference = false;
  double mass_kg = kSunray150VirtualPx4ClassicMassKg;
  double gravity_mps2 = kSunray150VirtualPx4ClassicGravityMps2;
  double hover_percentage = kSunray150VirtualPx4ClassicHoverPercentage;
  std::string odom_topic = "/uav1/mavros/local_position/odom";
  std::string imu_topic = "/uav1/mavros/imu/data";
  std::string flight_state_topic = "/uav1/mavros/state";
  std::string reference_topic = "/position_cmd";
  std::string px4_candidate_topic = "/mosim/mworks_live/px4ctrl_attitude_candidate";
  std::string mworks_candidate_topic = "/mosim/mworks_live/mworks_attitude_candidate";
  std::string final_topic = "/uav1/mavros/setpoint_raw/attitude";
  std::string owner_state_topic = "/mosim/mworks_live/control_owner_state";
};

Args parseArgs(int argc, char** argv) {
  Args args;
  auto requireValue = [&](int& index) -> std::string {
    if (++index >= argc) throw std::runtime_error("missing argument value");
    return argv[index];
  };
  for (int i = 1; i < argc; ++i) {
    const std::string key = argv[i];
    if (key == "--run-id") args.run_id = requireValue(i);
    else if (key == "--result-dir") args.result_dir = requireValue(i);
    else if (key == "--mworks-host") args.mworks_host = requireValue(i);
    else if (key == "--mworks-port") args.mworks_port = std::stoi(requireValue(i));
    else if (key == "--bind-host") args.bind_host = requireValue(i);
    else if (key == "--rate-hz") args.rate_hz = std::stod(requireValue(i));
    else if (key == "--status-rate-hz") args.status_rate_hz = std::stod(requireValue(i));
    else if (key == "--deadline-ms") args.deadline_ms = std::stod(requireValue(i));
    else if (key == "--command-stale-ms") args.command_stale_ms = std::stod(requireValue(i));
    else if (key == "--failsafe-escalation-ms") args.failsafe_escalation_ms = std::stod(requireValue(i));
    else if (key == "--consecutive-deadline-misses") args.consecutive_deadline_misses = std::stoi(requireValue(i));
    else if (key == "--minimum-shadow-commands") args.minimum_shadow_commands = std::stoi(requireValue(i));
    else if (key == "--max-receive-batch") args.max_receive_batch = std::stoi(requireValue(i));
    else if (key == "--trace-sample-rate-hz") args.trace_sample_rate_hz = std::stod(requireValue(i));
    else if (key == "--time-mode") args.time_mode = requireValue(i);
    else if (key == "--gazebo-steps-per-command") args.gazebo_steps_per_command = std::stoi(requireValue(i));
    else if (key == "--gazebo-step-size-ns") args.gazebo_step_size_ns = std::stoull(requireValue(i));
    else if (key == "--gazebo-bootstrap-timeout-s") args.gazebo_bootstrap_timeout_s = std::stod(requireValue(i));
    else if (key == "--sync-state-resend-ms") args.sync_state_resend_ms = std::stod(requireValue(i));
    else if (key == "--mass-kg") args.mass_kg = std::stod(requireValue(i));
    else if (key == "--gravity-mps2") args.gravity_mps2 = std::stod(requireValue(i));
    else if (key == "--hover-percentage") args.hover_percentage = std::stod(requireValue(i));
    else if (key == "--odom-topic") args.odom_topic = requireValue(i);
    else if (key == "--imu-topic") args.imu_topic = requireValue(i);
    else if (key == "--flight-state-topic") args.flight_state_topic = requireValue(i);
    else if (key == "--reference-topic") args.reference_topic = requireValue(i);
    else if (key == "--px4-candidate-topic") args.px4_candidate_topic = requireValue(i);
    else if (key == "--mworks-candidate-topic") args.mworks_candidate_topic = requireValue(i);
    else if (key == "--final-topic") args.final_topic = requireValue(i);
    else if (key == "--owner-state-topic") args.owner_state_topic = requireValue(i);
    else if (key == "--allow-active-takeover") args.allow_active_takeover = true;
    else if (key == "--auto-activate-ground") args.auto_activate_ground = true;
    else if (key == "--allow-ground-hold-reference") args.allow_ground_hold_reference = true;
    else throw std::runtime_error("unknown argument: " + key);
  }
  if (args.run_id.empty() || args.run_id.size() >= kRunIdSize || args.result_dir.empty())
    throw std::runtime_error("run-id and result-dir are required");
  if (args.rate_hz <= 0 || args.status_rate_hz <= 0 || args.max_receive_batch <= 0)
    throw std::runtime_error("rates and receive batch must be positive");
  if (args.auto_activate_ground && !args.allow_active_takeover)
    throw std::runtime_error("auto ground activation requires active takeover");
  if (args.time_mode != "wall_clock" && args.time_mode != "gazebo_step")
    throw std::runtime_error("time-mode must be wall_clock or gazebo_step");
  if (args.gazebo_steps_per_command <= 0 || args.gazebo_step_size_ns == 0 ||
      args.gazebo_bootstrap_timeout_s <= 0 || args.sync_state_resend_ms <= 0)
    throw std::runtime_error("Gazebo step parameters must be positive");
  if (args.time_mode == "gazebo_step" && args.allow_active_takeover)
    throw std::runtime_error("gazebo_step v1 is ground shadow only");
  if (args.allow_active_takeover && args.px4_candidate_topic == args.final_topic)
    throw std::runtime_error("active takeover requires distinct candidate and final topics");
  return args;
}

class Adapter {
 public:
  Adapter(ros::NodeHandle& node, Args args) : node_(node), args_(std::move(args)) {
    std::filesystem::create_directories(args_.result_dir);
    status_path_ = std::filesystem::path(args_.result_dir) / "RT1_STATUS.json";
    trace_.open(std::filesystem::path(args_.result_dir) / "rt1_trace.jsonl", std::ios::app);
    socket_ = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_ < 0) throw std::runtime_error("socket creation failed");
    fcntl(socket_, F_SETFL, fcntl(socket_, F_GETFL, 0) | O_NONBLOCK);
    sockaddr_in bind_address{};
    bind_address.sin_family = AF_INET;
    bind_address.sin_port = htons(0);
    if (inet_pton(AF_INET, args_.bind_host.c_str(), &bind_address.sin_addr) != 1 ||
        bind(socket_, reinterpret_cast<sockaddr*>(&bind_address), sizeof(bind_address)) != 0)
      throw std::runtime_error("UDP bind failed");
    peer_.sin_family = AF_INET;
    peer_.sin_port = htons(args_.mworks_port);
    if (inet_pton(AF_INET, args_.mworks_host.c_str(), &peer_.sin_addr) != 1)
      throw std::runtime_error("MWORKS host must be an IPv4 address");
    final_pub_ = node_.advertise<mavros_msgs::AttitudeTarget>(args_.final_topic, 10);
    mworks_candidate_pub_ = node_.advertise<mavros_msgs::AttitudeTarget>(args_.mworks_candidate_topic, 10);
    owner_pub_ = node_.advertise<std_msgs::String>(args_.owner_state_topic, 2, true);
    odom_sub_ = node_.subscribe(args_.odom_topic, 20, &Adapter::onOdom, this);
    imu_sub_ = node_.subscribe(args_.imu_topic, 40, &Adapter::onImu, this);
    state_sub_ = node_.subscribe(args_.flight_state_topic, 20, &Adapter::onState, this);
    reference_sub_ = node_.subscribe(args_.reference_topic, 20, &Adapter::onReference, this);
    px4_sub_ = node_.subscribe(args_.px4_candidate_topic, 40, &Adapter::onPx4Candidate, this);
    clock_sub_ = node_.subscribe("/clock", 100, &Adapter::onClock, this);
    if (args_.time_mode == "gazebo_step") {
      gazebo_node_.reset(new gazebo::transport::Node());
      gazebo_node_->Init();
      world_stats_sub_ = gazebo_node_->Subscribe(
          "~/world_stats", &Adapter::onWorldStats, this);
      world_control_pub_ =
          gazebo_node_->Advertise<gazebo::msgs::WorldControl>("~/world_control");
      if (!world_control_pub_->WaitForConnection(gazebo::common::Time(5, 0)))
        throw std::runtime_error("Gazebo world_control subscriber unavailable");
      publishWorldPause(true);
    }
    started_ns_ = monotonicNs();
    publishStatus("shadow_started", true);
  }

  ~Adapter() { if (socket_ >= 0) close(socket_); }

  void run() {
    if (args_.time_mode == "gazebo_step") {
      runGazeboStep();
      return;
    }
    const uint64_t period_ns = static_cast<uint64_t>(std::llround(1e9 / args_.rate_hz));
    timespec next{};
    clock_gettime(CLOCK_MONOTONIC, &next);
    while (ros::ok()) {
      tick();
      uint64_t next_ns = static_cast<uint64_t>(next.tv_sec) * 1000000000ULL + next.tv_nsec + period_ns;
      const uint64_t now_ns = monotonicNs();
      if (next_ns + 4 * period_ns < now_ns) next_ns = now_ns + period_ns;
      next.tv_sec = next_ns / 1000000000ULL;
      next.tv_nsec = next_ns % 1000000000ULL;
      clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, nullptr);
    }
    publishStatus("shutdown", true);
  }

 private:
  enum class State { SHADOW, READY, ACTIVE, FALLBACK_HOVER, DEGRADED };
  void onOdom(const nav_msgs::Odometry::ConstPtr& m) { std::lock_guard<std::mutex> l(data_mutex_); odom_=*m; have_odom_=true; }
  void onImu(const sensor_msgs::Imu::ConstPtr& m) { std::lock_guard<std::mutex> l(data_mutex_); imu_=*m; have_imu_=true; }
  void onState(const mavros_msgs::State::ConstPtr& m) { std::lock_guard<std::mutex> l(data_mutex_); flight_state_=*m; have_state_=true; }
  void onReference(const quadrotor_msgs::PositionCommand::ConstPtr& m) { std::lock_guard<std::mutex> l(data_mutex_); reference_=*m; have_reference_=true; }
  void onPx4Candidate(const mavros_msgs::AttitudeTarget::ConstPtr& m) { std::lock_guard<std::mutex> l(data_mutex_); px4_candidate_=*m; have_px4_candidate_=true; }
  void onClock(const rosgraph_msgs::Clock::ConstPtr& m) { std::lock_guard<std::mutex> l(data_mutex_); sim_time_ns_=m->clock.toNSec();have_clock_=true; }
  void onWorldStats(ConstWorldStatisticsPtr& m) {
    std::lock_guard<std::mutex> lock(data_mutex_);
    sim_time_ns_ = static_cast<uint64_t>(m->sim_time().sec()) * 1000000000ULL +
                   static_cast<uint64_t>(m->sim_time().nsec());
    have_clock_ = true;
  }

  void runGazeboStep() {
    timespec sleep_value{};
    sleep_value.tv_nsec = 1000000;
    while (ros::ok()) {
      tickGazeboStep();
      nanosleep(&sleep_value, nullptr);
    }
    publishStatus("shutdown", true);
  }

  uint64_t currentSimTimeNs() const {
    std::lock_guard<std::mutex> lock(data_mutex_);
    return sim_time_ns_;
  }

  bool haveSimTime() const {
    std::lock_guard<std::mutex> lock(data_mutex_);
    return have_clock_;
  }

  void publishWorldPause(bool paused) {
    gazebo::msgs::WorldControl message;
    message.set_pause(paused);
    world_control_pub_->Publish(message);
  }

  void publishWorldSteps() {
    gazebo::msgs::WorldControl message;
    message.set_multi_step(static_cast<uint32_t>(args_.gazebo_steps_per_command));
    world_control_pub_->Publish(message);
    ++step_request_count_;
  }

  void publishBootstrapSteps() {
    gazebo::msgs::WorldControl message;
    message.set_multi_step(static_cast<uint32_t>(args_.gazebo_steps_per_command));
    world_control_pub_->Publish(message);
    ++bootstrap_step_request_count_;
  }

  bool bootstrapGazeboStep(uint64_t now_ns, uint64_t sim_ns) {
    if (bootstrap_waiting_for_sim_advance_) {
      if (sim_ns < bootstrap_target_sim_time_ns_) {
        publishStatus("bootstrap_waiting_for_sim_advance", false);
        return false;
      }
      bootstrap_waiting_for_sim_advance_ = false;
      ++bootstrap_step_completion_count_;
      traceSyncEvent("bootstrap_step_completed", sim_ns);
    }

    StateReferenceWire probe{};
    if (snapshot(probe, now_ns)) {
      bootstrap_complete_ = true;
      traceSyncEvent("bootstrap_complete", sim_ns);
      publishStatus("bootstrap_complete", true);
      return true;
    }

    const uint64_t timeout_ns =
        static_cast<uint64_t>(args_.gazebo_bootstrap_timeout_s * 1e9);
    if (now_ns - started_ns_ >= timeout_ns) {
      ++bootstrap_timeout_count_;
      state_ = State::DEGRADED;
      traceSyncEvent("bootstrap_state_timeout", sim_ns);
      publishStatus("bootstrap_state_timeout", true);
      ros::shutdown();
      return false;
    }

    const uint64_t step_span_ns =
        static_cast<uint64_t>(args_.gazebo_steps_per_command) * args_.gazebo_step_size_ns;
    bootstrap_target_sim_time_ns_ = sim_ns + step_span_ns;
    bootstrap_waiting_for_sim_advance_ = true;
    publishBootstrapSteps();
    traceSyncEvent("bootstrap_step_requested", sim_ns);
    publishStatus("bootstrap_waiting_for_state", false);
    return false;
  }

  void tickGazeboStep() {
    const uint64_t now_ns = monotonicNs();
    const uint64_t sim_ns = currentSimTimeNs();
    if (!haveSimTime()) {
      publishStatus("waiting_for_clock", false);
      return;
    }
    if (!bootstrap_complete_ && !bootstrapGazeboStep(now_ns, sim_ns)) return;
    if (waiting_for_sim_advance_) {
      if (sim_ns >= target_sim_time_ns_) {
        waiting_for_sim_advance_ = false;
        ++step_completion_count_;
        traceSyncEvent("step_completed", sim_ns);
      } else {
        receiveCommands();
        publishStatus("waiting_for_sim_advance", false);
        return;
      }
    }
    if (!awaiting_command_) {
      StateReferenceWire state{};
      if (!snapshot(state, now_ns)) {
        publishStatus("waiting_for_state", false);
        return;
      }
      const uint32_t sent_sequence = sequence_;
      sendState(state, now_ns);
      awaiting_state_sequence_ = sent_sequence;
      awaiting_command_ = true;
      awaiting_command_since_ns_ = now_ns;
    }
    const auto accepted_state_sequence = receiveCommands();
    if (accepted_state_sequence.has_value() &&
        *accepted_state_sequence == awaiting_state_sequence_) {
      const uint64_t step_span_ns =
          static_cast<uint64_t>(args_.gazebo_steps_per_command) * args_.gazebo_step_size_ns;
      target_sim_time_ns_ = sim_ns + step_span_ns;
      awaiting_command_ = false;
      waiting_for_sim_advance_ = true;
      publishWorldSteps();
      traceSyncEvent("step_requested", sim_ns);
      publishStatus("step_requested", false);
      return;
    }
    const uint64_t resend_ns = static_cast<uint64_t>(args_.sync_state_resend_ms * 1e6);
    if (awaiting_command_ && now_ns - awaiting_command_since_ns_ >= resend_ns) {
      ++sync_wait_timeout_count_;
      awaiting_command_ = false;
      traceSyncEvent("command_wait_timeout", sim_ns);
      publishStatus("sync_command_wait_timeout", true);
    } else {
      publishStatus("waiting_for_command", false);
    }
  }

  bool snapshot(StateReferenceWire& frame, uint64_t now_ns) {
    std::lock_guard<std::mutex> lock(data_mutex_);
    if (!have_odom_ || !have_imu_ || !have_state_) return false;
    if (!have_reference_ && !(args_.allow_ground_hold_reference && !flight_state_.armed)) return false;
    frame = {};
    frame.header.magic=kStateMagic; frame.header.version=kProtocolVersion;
    frame.header.flags=kFlagStateValid|kFlagReferenceValid|(flight_state_.armed?kFlagArmed:0);
    frame.header.sequence=sequence_;
    frame.header.source_stamp_ns=odom_.header.stamp.isZero()?now_ns:odom_.header.stamp.toNSec();
    frame.header.produced_or_receive_ns=now_ns;
    frame.header.valid_until_ns=now_ns+static_cast<uint64_t>(args_.command_stale_ms*1e6);
    std::memcpy(frame.header.run_id,args_.run_id.data(),args_.run_id.size());
    const auto&p=odom_.pose.pose.position;const auto&v=odom_.twist.twist.linear;const auto&q=odom_.pose.pose.orientation;const auto&w=imu_.angular_velocity;double*x=frame.values;
    x[0]=p.x;x[1]=p.y;x[2]=p.z;x[3]=v.x;x[4]=v.y;x[5]=v.z;x[6]=q.x;x[7]=q.y;x[8]=q.z;x[9]=q.w;x[10]=w.x;x[11]=w.y;x[12]=w.z;
    if(have_reference_){x[13]=reference_.position.x;x[14]=reference_.position.y;x[15]=reference_.position.z;x[16]=reference_.velocity.x;x[17]=reference_.velocity.y;x[18]=reference_.velocity.z;x[19]=reference_.acceleration.x;x[20]=reference_.acceleration.y;x[21]=reference_.acceleration.z;x[22]=reference_.yaw;x[23]=reference_.yaw_dot;}
    else{x[13]=p.x;x[14]=p.y;x[15]=p.z;x[22]=std::atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z));}
    return true;
  }

  void tick() {
    const uint64_t now_ns=monotonicNs();StateReferenceWire state{};if(snapshot(state,now_ns))sendState(state,now_ns);receiveCommands();
    if(state_==State::ACTIVE&&(!last_command_receive_ns_||now_ns-last_command_receive_ns_>staleNs()))fallback(now_ns);
    if(state_==State::FALLBACK_HOVER&&fallback_started_ns_&&now_ns-fallback_started_ns_>=static_cast<uint64_t>(args_.failsafe_escalation_ms*1e6))state_=State::DEGRADED;
    maybeActivateOnGround();if(state_!=State::ACTIVE)publishFallback();publishStatus("tick",false);
  }

  void sendState(const StateReferenceWire& frame,uint64_t now_ns){
    const ssize_t bytes=sendto(socket_,&frame,sizeof(frame),0,reinterpret_cast<const sockaddr*>(&peer_),sizeof(peer_));if(bytes!=static_cast<ssize_t>(sizeof(frame))){++send_error_count_;return;}
    if(last_send_ns_)appendBounded(send_intervals_ms_,(now_ns-last_send_ns_)/1e6);if(!first_send_ns_)first_send_ns_=now_ns;last_send_ns_=now_ns;++sent_frame_count_;sent_payload_bytes_+=bytes;state_send_times_[sequence_]=now_ns;if(state_send_times_.size()>4096)state_send_times_.erase(sequence_-4096);++sequence_;
  }

  std::string validateCommand(const CommandWire& c,uint64_t now_ns)const{
    if(c.header.magic!=kCommandMagic)return"invalid_magic";if(c.header.version!=kProtocolVersion)return"unsupported_protocol_version";if(std::string(c.header.run_id,strnlen(c.header.run_id,kRunIdSize))!=args_.run_id)return"run_id_mismatch";if(last_command_sequence_&&c.header.sequence<=last_command_sequence_)return"sequence_regression";if(sequence_&&c.header.related_sequence>sequence_-1)return"state_sequence_ahead";if(!(c.header.flags&kFlagOutputValid)||c.controller_status!=1)return"controller_output_invalid";
    double norm=0;for(double value:c.q_xyzw){if(!std::isfinite(value))return"non_finite_output";norm+=value*value;}if(!std::isfinite(c.collective_thrust_n))return"non_finite_output";if(std::abs(std::sqrt(norm)-1.0)>1e-6)return"quaternion_not_normalized";if(c.collective_thrust_n<=0)return"command_out_of_bounds";if(now_ns>c.header.valid_until_ns||now_ns-c.header.source_stamp_ns>staleNs())return"output_stale";return"";
  }

  std::optional<uint32_t> receiveCommands(){
    std::optional<uint32_t> accepted_state_sequence;
    for(int i=0;i<args_.max_receive_batch;++i){CommandWire c{};const ssize_t bytes=recvfrom(socket_,&c,sizeof(c),0,nullptr,nullptr);if(bytes<0)break;const uint64_t now=monotonicNs();if(!first_receive_ns_)first_receive_ns_=now;if(last_receive_ns_)appendBounded(receive_intervals_ms_,(now-last_receive_ns_)/1e6);last_receive_ns_=now;++received_frame_count_;received_payload_bytes_+=std::max<ssize_t>(0,bytes);
      if(bytes!=static_cast<ssize_t>(sizeof(c))){++rejected_count_;++invalid_size_count_;traceDecision(false,"invalid_command_size",0,0,now);continue;}if(last_received_sequence_){if(c.header.sequence==last_received_sequence_)++duplicate_count_;else if(c.header.sequence<last_received_sequence_)++out_of_order_count_;else missing_count_+=c.header.sequence-last_received_sequence_-1;}last_received_sequence_=std::max(last_received_sequence_,c.header.sequence);
      const auto sent=state_send_times_.find(c.header.related_sequence);if(sent!=state_send_times_.end()){appendBounded(rtt_ms_,(now-sent->second)/1e6);state_send_times_.erase(sent);}std::string reason=validateCommand(c,now);if(reason.empty()&&args_.time_mode=="gazebo_step"&&(!awaiting_command_||c.header.related_sequence!=awaiting_state_sequence_))reason="sync_state_sequence_mismatch";const double age=(now-c.header.source_stamp_ns)/1e6;last_observed_command_age_ms_=age;appendBounded(command_age_ms_,age);command_age_max_ms_=std::max(command_age_max_ms_,age);if(age>args_.deadline_ms)++deadline_miss_count_;last_command_receive_ns_=now;const bool accepted=reason.empty();
      if(accepted){last_command_sequence_=c.header.sequence;++accepted_count_;accepted_state_sequence=c.header.related_sequence;consecutive_deadline_misses_=age>args_.deadline_ms?consecutive_deadline_misses_+1:0;if(state_==State::ACTIVE&&consecutive_deadline_misses_>=args_.consecutive_deadline_misses){fallback(now);++rejected_count_;++consecutive_deadline_rejection_count_;traceDecision(false,"consecutive_deadline_miss",c.header.sequence,c.header.related_sequence,now);continue;}auto m=toAttitudeTarget(c);mworks_candidate_pub_.publish(m);if(state_==State::ACTIVE)final_pub_.publish(m);}else{++rejected_count_;if(reason=="output_stale")++output_stale_count_;else ++other_rejection_count_;if(state_==State::ACTIVE)fallback(now);}
      const uint64_t trace_period=static_cast<uint64_t>(1e9/args_.trace_sample_rate_hz);if(!accepted||now-last_accepted_trace_ns_>=trace_period){traceDecision(accepted,accepted?"command_accepted":reason,c.header.sequence,c.header.related_sequence,now);if(accepted){last_accepted_trace_ns_=now;++accepted_trace_count_;}}
    }
    return accepted_state_sequence;
  }

  mavros_msgs::AttitudeTarget toAttitudeTarget(const CommandWire& c)const{mavros_msgs::AttitudeTarget m;m.header.stamp=ros::Time::now();m.header.frame_id="FCU";m.type_mask=mavros_msgs::AttitudeTarget::IGNORE_ROLL_RATE|mavros_msgs::AttitudeTarget::IGNORE_PITCH_RATE|mavros_msgs::AttitudeTarget::IGNORE_YAW_RATE;m.orientation.x=c.q_xyzw[0];m.orientation.y=c.q_xyzw[1];m.orientation.z=c.q_xyzw[2];m.orientation.w=c.q_xyzw[3];m.thrust=std::clamp(c.collective_thrust_n/(args_.mass_kg*args_.gravity_mps2/args_.hover_percentage),0.0,1.0);return m;}
  void maybeActivateOnGround(){if(!args_.auto_activate_ground||state_!=State::SHADOW||accepted_count_<static_cast<uint64_t>(args_.minimum_shadow_commands))return;std::lock_guard<std::mutex>l(data_mutex_);if(!have_state_||flight_state_.armed)return;state_=State::READY;state_=State::ACTIVE;publishStatus("active",true);}
  void fallback(uint64_t now){state_=State::FALLBACK_HOVER;if(!fallback_started_ns_)fallback_started_ns_=now;}
  void publishFallback(){std::lock_guard<std::mutex>l(data_mutex_);if(have_px4_candidate_)final_pub_.publish(px4_candidate_);}
  uint64_t staleNs()const{return static_cast<uint64_t>(args_.command_stale_ms*1e6);}
  std::string stateName()const{switch(state_){case State::SHADOW:return"SHADOW";case State::READY:return"READY";case State::ACTIVE:return"ACTIVE";case State::FALLBACK_HOVER:return"FALLBACK_HOVER";case State::DEGRADED:return"DEGRADED";}return"FAILED";}
  void traceDecision(bool accepted,const std::string&reason,uint32_t command_sequence,uint32_t state_sequence,uint64_t received_ns){trace_<<"{\"event\":\"command_decision\",\"sequence\":"<<command_sequence<<",\"state_sequence\":"<<state_sequence<<",\"accepted\":"<<(accepted?"true":"false")<<",\"reason_code\":\""<<jsonEscape(reason)<<"\",\"control_state\":\""<<stateName()<<"\",\"command_age_ms\":"<<optionalNumber(last_observed_command_age_ms_)<<",\"received_ns\":"<<received_ns<<"}\n";trace_.flush();}
  void traceSyncEvent(const std::string& event, uint64_t sim_time_ns) {
    trace_ << "{\"event\":\"" << jsonEscape(event)
           << "\",\"monotonic_ns\":" << monotonicNs()
           << ",\"sim_time_ns\":" << sim_time_ns
           << ",\"step_request_count\":" << step_request_count_
           << ",\"step_completion_count\":" << step_completion_count_
           << ",\"bootstrap_step_request_count\":" << bootstrap_step_request_count_
           << ",\"bootstrap_step_completion_count\":" << bootstrap_step_completion_count_
           << "}\n";
    trace_.flush();
  }

  std::string syncStatusJson(const std::string& reason, uint64_t now) const {
    const double process_s = std::max(1e-9, (now - started_ns_) / 1e9);
    const double state_s = first_send_ns_ ? std::max(1e-9, (now - first_send_ns_) / 1e9) : 0;
    const double command_s = first_receive_ns_ ? std::max(1e-9, (now - first_receive_ns_) / 1e9) : 0;
    const uint64_t command_total = received_frame_count_ + missing_count_;
    std::ostringstream o;
    o << std::setprecision(12);
    o << "{\n  \"schema\": \"mosim.mworks_live_rt1_status.v1\",\n"
      << "  \"adapter_backend\": \"cpp_gazebo_step_v1\",\n"
      << "  \"time_mode\": \"gazebo_step\",\n"
      << "  \"run_id\": \"" << jsonEscape(args_.run_id) << "\",\n"
      << "  \"state\": \"" << stateName() << "\",\n"
      << "  \"reason\": \"" << jsonEscape(reason) << "\",\n"
      << "  \"shadow_only\": true,\n"
      << "  \"state_reference_count\": " << sequence_ << ",\n"
      << "  \"accepted_command_count\": " << accepted_count_ << ",\n"
      << "  \"rejected_command_count\": " << rejected_count_ << ",\n"
      << "  \"last_command_sequence\": " << last_command_sequence_ << ",\n"
      << "  \"deadline_miss_count\": " << deadline_miss_count_ << ",\n"
      << "  \"command_age_ms\": " << (command_age_ms_.empty() ? "null" : optionalNumber(command_age_ms_.back())) << ",\n"
      << "  \"command_age_ms_max\": " << optionalNumber(command_age_max_ms_) << ",\n"
      << "  \"synchronization\": {\n"
      << "    \"sim_time_ns\": " << currentSimTimeNs() << ",\n"
      << "    \"gazebo_steps_per_command\": " << args_.gazebo_steps_per_command << ",\n"
      << "    \"gazebo_step_size_ns\": " << args_.gazebo_step_size_ns << ",\n"
      << "    \"bootstrap_complete\": " << (bootstrap_complete_ ? "true" : "false") << ",\n"
      << "    \"bootstrap_step_request_count\": " << bootstrap_step_request_count_ << ",\n"
      << "    \"bootstrap_step_completion_count\": " << bootstrap_step_completion_count_ << ",\n"
      << "    \"bootstrap_timeout_count\": " << bootstrap_timeout_count_ << ",\n"
      << "    \"step_request_count\": " << step_request_count_ << ",\n"
      << "    \"step_completion_count\": " << step_completion_count_ << ",\n"
      << "    \"command_wait_timeout_count\": " << sync_wait_timeout_count_ << "\n  },\n"
      << "  \"rejection_counts\": {\n"
      << "    \"output_stale\": " << output_stale_count_ << ",\n"
      << "    \"consecutive_deadline_miss\": " << consecutive_deadline_rejection_count_ << ",\n"
      << "    \"invalid_size\": " << invalid_size_count_ << ",\n"
      << "    \"other\": " << other_rejection_count_ << "\n  },\n"
      << "  \"mworks_peer\": \"" << jsonEscape(args_.mworks_host) << ":" << args_.mworks_port << "\",\n"
      << "  \"transport\": {\n"
      << "    \"state_frame_bytes\": " << sizeof(StateReferenceWire) << ",\n"
      << "    \"command_frame_bytes\": " << sizeof(CommandWire) << ",\n"
      << "    \"process_window_s\": " << process_s << ",\n"
      << "    \"state_measurement_window_s\": " << state_s << ",\n"
      << "    \"command_measurement_window_s\": " << command_s << ",\n"
      << "    \"state_send_rate_hz\": " << (state_s ? sent_frame_count_ / state_s : 0) << ",\n"
      << "    \"command_receive_rate_hz\": " << (command_s ? received_frame_count_ / command_s : 0) << ",\n"
      << "    \"send_error_count\": " << send_error_count_ << ",\n"
      << "    \"missing_command_count\": " << missing_count_ << ",\n"
      << "    \"duplicate_command_count\": " << duplicate_count_ << ",\n"
      << "    \"out_of_order_command_count\": " << out_of_order_count_ << ",\n"
      << "    \"estimated_command_drop_rate\": " << (command_total ? static_cast<double>(missing_count_) / command_total : 0) << ",\n"
      << "    \"rtt_ms_p50\": " << optionalNumber(percentile(rtt_ms_, .50)) << ",\n"
      << "    \"rtt_ms_p95\": " << optionalNumber(percentile(rtt_ms_, .95)) << ",\n"
      << "    \"rtt_ms_p99\": " << optionalNumber(percentile(rtt_ms_, .99)) << "\n  },\n"
      << "  \"updated_at_unix\": " << unixSeconds() << "\n}\n";
    return o.str();
  }

  std::string statusJson(const std::string&reason,uint64_t now)const{
    if (args_.time_mode == "gazebo_step") return syncStatusJson(reason, now);
    const double process_s=std::max(1e-9,(now-started_ns_)/1e9),state_s=first_send_ns_?std::max(1e-9,(now-first_send_ns_)/1e9):0,command_s=first_receive_ns_?std::max(1e-9,(now-first_receive_ns_)/1e9):0;const uint64_t command_total=received_frame_count_+missing_count_;std::ostringstream o;o<<std::setprecision(12);
    o<<"{\n  \"schema\": \"mosim.mworks_live_rt1_status.v1\",\n  \"adapter_backend\": \"cpp_wall_clock_v1\",\n  \"run_id\": \""<<jsonEscape(args_.run_id)<<"\",\n  \"state\": \""<<stateName()<<"\",\n  \"reason\": \""<<jsonEscape(reason)<<"\",\n  \"shadow_only\": "<<(args_.allow_active_takeover?"false":"true")<<",\n  \"state_reference_count\": "<<sequence_<<",\n  \"accepted_command_count\": "<<accepted_count_<<",\n  \"rejected_command_count\": "<<rejected_count_<<",\n  \"accepted_trace_sample_count\": "<<accepted_trace_count_<<",\n  \"last_command_sequence\": "<<last_command_sequence_<<",\n  \"consecutive_deadline_misses\": "<<consecutive_deadline_misses_<<",\n  \"deadline_miss_count\": "<<deadline_miss_count_<<",\n  \"command_age_ms\": "<<(command_age_ms_.empty()?"null":optionalNumber(command_age_ms_.back()))<<",\n  \"command_age_ms_max\": "<<optionalNumber(command_age_max_ms_)<<",\n  \"rejection_counts\": {\n    \"output_stale\": "<<output_stale_count_<<",\n    \"consecutive_deadline_miss\": "<<consecutive_deadline_rejection_count_<<",\n    \"invalid_size\": "<<invalid_size_count_<<",\n    \"other\": "<<other_rejection_count_<<"\n  },\n  \"mworks_peer\": \""<<jsonEscape(args_.mworks_host)<<":"<<args_.mworks_port<<"\",\n  \"transport\": {\n    \"state_frame_bytes\": "<<sizeof(StateReferenceWire)<<",\n    \"command_frame_bytes\": "<<sizeof(CommandWire)<<",\n    \"process_window_s\": "<<process_s<<",\n    \"startup_wait_before_first_state_s\": "<<(first_send_ns_?std::to_string((first_send_ns_-started_ns_)/1e9):"null")<<",\n    \"state_measurement_window_s\": "<<state_s<<",\n    \"command_measurement_window_s\": "<<command_s<<",\n    \"state_send_rate_hz\": "<<(state_s?sent_frame_count_/state_s:0)<<",\n    \"command_receive_rate_hz\": "<<(command_s?received_frame_count_/command_s:0)<<",\n    \"state_payload_bytes_per_s\": "<<(state_s?sent_payload_bytes_/state_s:0)<<",\n    \"command_payload_bytes_per_s\": "<<(command_s?received_payload_bytes_/command_s:0)<<",\n    \"bidirectional_payload_bytes_per_s\": "<<((state_s?sent_payload_bytes_/state_s:0)+(command_s?received_payload_bytes_/command_s:0))<<",\n    \"estimated_ipv4_udp_wire_bytes_per_s\": "<<((state_s?(sent_payload_bytes_+sent_frame_count_*kIpv4UdpHeaderBytes)/state_s:0)+(command_s?(received_payload_bytes_+received_frame_count_*kIpv4UdpHeaderBytes)/command_s:0))<<",\n    \"send_error_count\": "<<send_error_count_<<",\n    \"missing_command_count\": "<<missing_count_<<",\n    \"duplicate_command_count\": "<<duplicate_count_<<",\n    \"out_of_order_command_count\": "<<out_of_order_count_<<",\n    \"estimated_command_drop_rate\": "<<(command_total?static_cast<double>(missing_count_)/command_total:0)<<",\n    \"send_interval_jitter_ms\": "<<optionalNumber(populationStddev(send_intervals_ms_))<<",\n    \"receive_interval_jitter_ms\": "<<optionalNumber(populationStddev(receive_intervals_ms_))<<",\n    \"rtt_ms_p50\": "<<optionalNumber(percentile(rtt_ms_,.50))<<",\n    \"rtt_ms_p95\": "<<optionalNumber(percentile(rtt_ms_,.95))<<",\n    \"rtt_ms_p99\": "<<optionalNumber(percentile(rtt_ms_,.99))<<",\n    \"command_age_ms_p50\": "<<optionalNumber(percentile(command_age_ms_,.50))<<",\n    \"command_age_ms_p95\": "<<optionalNumber(percentile(command_age_ms_,.95))<<",\n    \"command_age_ms_p99\": "<<optionalNumber(percentile(command_age_ms_,.99))<<"\n  },\n  \"updated_at_unix\": "<<unixSeconds()<<"\n}\n";return o.str();
  }
  void publishStatus(const std::string&reason,bool force){const uint64_t now=monotonicNs(),period=static_cast<uint64_t>(1e9/args_.status_rate_hz);if(!force&&now-last_status_ns_<period)return;last_status_ns_=now;const std::string value=statusJson(reason,now),temp=status_path_.string()+".tmp";{std::ofstream s(temp);s<<value;}std::filesystem::rename(temp,status_path_);std_msgs::String m;m.data=value;owner_pub_.publish(m);}

  ros::Subscriber clock_sub_;
  gazebo::transport::NodePtr gazebo_node_;
  gazebo::transport::PublisherPtr world_control_pub_;
  gazebo::transport::SubscriberPtr world_stats_sub_;
  bool have_clock_=false,awaiting_command_=false,waiting_for_sim_advance_=false;
  bool bootstrap_complete_=false,bootstrap_waiting_for_sim_advance_=false;
  uint32_t awaiting_state_sequence_=0;
  uint64_t sim_time_ns_=0,target_sim_time_ns_=0,awaiting_command_since_ns_=0;
  uint64_t bootstrap_target_sim_time_ns_=0;
  uint64_t step_request_count_=0,step_completion_count_=0,sync_wait_timeout_count_=0;
  uint64_t bootstrap_step_request_count_=0,bootstrap_step_completion_count_=0,bootstrap_timeout_count_=0;
  ros::NodeHandle&node_;Args args_;int socket_=-1;sockaddr_in peer_{};std::filesystem::path status_path_;std::ofstream trace_;ros::Publisher final_pub_,mworks_candidate_pub_,owner_pub_;ros::Subscriber odom_sub_,imu_sub_,state_sub_,reference_sub_,px4_sub_;mutable std::mutex data_mutex_;nav_msgs::Odometry odom_;sensor_msgs::Imu imu_;mavros_msgs::State flight_state_;quadrotor_msgs::PositionCommand reference_;mavros_msgs::AttitudeTarget px4_candidate_;bool have_odom_=false,have_imu_=false,have_state_=false,have_reference_=false,have_px4_candidate_=false;State state_=State::SHADOW;uint32_t sequence_=0,last_command_sequence_=0,last_received_sequence_=0;uint64_t started_ns_=0,first_send_ns_=0,last_send_ns_=0,first_receive_ns_=0,last_receive_ns_=0,last_command_receive_ns_=0,last_status_ns_=0,last_accepted_trace_ns_=0,fallback_started_ns_=0;uint64_t sent_frame_count_=0,sent_payload_bytes_=0,received_frame_count_=0,received_payload_bytes_=0,send_error_count_=0,missing_count_=0,duplicate_count_=0,out_of_order_count_=0,accepted_count_=0,rejected_count_=0,accepted_trace_count_=0,deadline_miss_count_=0,output_stale_count_=0,consecutive_deadline_rejection_count_=0,invalid_size_count_=0,other_rejection_count_=0;double command_age_max_ms_=0.0,last_observed_command_age_ms_=0.0;int consecutive_deadline_misses_=0;std::unordered_map<uint32_t,uint64_t>state_send_times_;std::deque<double>send_intervals_ms_,receive_intervals_ms_,rtt_ms_,command_age_ms_;
};
}  // namespace

int main(int argc,char**argv){try{Args args=parseArgs(argc,argv);const bool gazebo_step=args.time_mode=="gazebo_step";ros::init(argc,argv,"mosim_mworks_live_rt1_adapter_cpp",ros::init_options::NoSigintHandler);if(gazebo_step&&!gazebo::client::setup())throw std::runtime_error("Gazebo client setup failed");ros::NodeHandle node;Adapter adapter(node,std::move(args));ros::AsyncSpinner spinner(2);spinner.start();adapter.run();spinner.stop();if(gazebo_step)gazebo::client::shutdown();return 0;}catch(const std::exception&error){std::cerr<<error.what()<<std::endl;return 2;}}
