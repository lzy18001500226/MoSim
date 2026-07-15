#ifndef GRAPH_MANAGER_H_
#define GRAPH_MANAGER_H_

#include <fstream>
#include <iostream>
#include <unordered_map>

#include <eigen3/Eigen/Dense>
#include <kdtree/kdtree.h>
#include <planner_msgs/Edge.h>
#include <planner_msgs/Graph.h>
#include <planner_msgs/Vertex.h>
#include <tf/transform_datatypes.h>

#include "planner_common/graph.h"
#include "planner_common/graph_base.h"
#include "planner_common/params.h"

class GraphManager {
 public:
  GraphManager();

  // Initialize a fresh graph.
  void reset();
  
  // sets the robot of the robot.
  void setRobotId(int robot_id);

  // Could change an index to break down the graph into sug-graphs.
  int generateSubgraphIndex();
  // Generate ID for new vertex.
  int generateVertexID();

  // Basic functions on graph including add new vertex and edge.
  void addVertex(Vertex* v);
  void addNeighbourVertex(Vertex* v, int neighbour_vertex_id);
  void addEdge(Vertex* v, Vertex* u, double weight);
  void addNeighbourEdge(Vertex* v, Vertex* u, double weight);
  void removeEdge(Vertex* v, Vertex* u);

  int getNumVertices() { return graph_->getNumVertices(); }
  int getNumEdges() { return graph_->getNumEdges(); }

  Vertex* getVertex(int id) {
     return vertices_map_[id]; 
    }
  
  Vertex* getNeighbourVertex(int neighbour_vertex_id, int robot_id) {
    return vertex_by_robot_id_[robot_id][neighbour_vertex_id];
  }
  void getLeafVertices(std::vector<Vertex*>& leaf_vertices);
  void findLeafVertices(const ShortestPathsReport& rep);

  bool findShortestPaths(ShortestPathsReport& rep);
  bool findShortestPaths(int source_id, ShortestPathsReport& rep);

  void getShortestPath(int target_id, const ShortestPathsReport& rep,
                       bool source_to_target_order, std::vector<int>& path);
  void getShortestPath(int target_id, const ShortestPathsReport& rep,
                       bool source_to_target_order, std::vector<Vertex*>& path);
  void getShortestPath(int target_id, const ShortestPathsReport& rep,
                       bool source_to_target_order,
                       std::vector<Eigen::Vector3d>& path);
  void getShortestPath(int target_id, const ShortestPathsReport& rep,
                       bool source_to_target_order,
                       std::vector<StateVec>& path);
  double getShortestDistance(int target_id, const ShortestPathsReport& rep);
  int getParentIDFromShortestPath(int target_id,
                                  const ShortestPathsReport& rep);

  // Nearest neigbor lookup.
  bool getNearestVertex(const StateVec* state, Vertex** v_res);
  bool getNearestVertexInRange(const StateVec* state, double range,
                               Vertex** v_res);
  bool getNearestVertices(const StateVec* state, double range,
                          std::vector<Vertex*>* v_res);
  bool updatePoseIdToNearestVertices(const StateVec* state,
                           double range, int pose_id);
  bool existVertexInRange(const StateVec* state, double range);

  void updateVertexTypeInRange(StateVec& state, double range);

  void convertGraphToMsg(planner_msgs::Graph& graph_msg);
  void convertThisRobotGraphNodesToMsg(planner_msgs::Graph& graph_msg);
  void convertMsgToGraph(const planner_msgs::Graph& graph_msg);

  // Neighour graph merge functions

  void UpdateNeighbourGraph(const planner_msgs::Graph& msg);

  void saveGraph(const std::string& path);
  void loadGraph(const std::string& path);

  // A wrapper on top of Boost Graph Lib.
  // Maintain a simple graph with IDs and weights.
  std::shared_ptr<Graph> graph_;
  // Mapping from vertex id to vertex property.
  std::unordered_map<int, Vertex*> vertices_map_;
  std::map<int, std::vector<std::pair<int, double>>>
      edge_map_;  // id:  <neighbor id, edge cost>

  // Other robots graph. <Robot id, <other robot vertex id, this robot vertex>>
  std::unordered_map<int, std::unordered_map<int, Vertex*>> vertex_by_robot_id_;

  // other robot graph merged status
  std::unordered_map<int, bool> merged_graphs_; 

 private:
  // Kd-tree for nearest neigbor lookup, also keep all vertices.
  kdtree* kd_tree_;
  // IDs are non-negative integer from 0 (root node)
  // and increased as adding new sub-graph or new vertices.
  int subgraph_ind_;
  int id_count_;
  int robot_id_;

  // Map from local id for Boost Graph Lib to global ID including
  // <sub-graph-id,vertex-id>. This is mainly for debug purpose.
  std::unordered_map<int, std::pair<int, int>> local_id_map_;
};

#endif
