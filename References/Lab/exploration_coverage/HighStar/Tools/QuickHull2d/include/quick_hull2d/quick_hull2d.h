#ifndef QUICK_HULL_2D_
#define QUICK_HULL_2D_

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Dense>
#include <vector>
#include <fstream>
#include <iostream>
#include <ros/ros.h>
#include <list>
#include <memory>
#include <math.h>
#include <random>

using namespace std;

void QuickHull(vector<Eigen::Vector2d> &pts, vector<pair<Eigen::Vector2d, int>> &hull);

void QuickHullSearch(const pair<Eigen::Vector2d, Eigen::Vector2d> &line, const pair<Eigen::Vector2d, int> &TopPt, list<pair<Eigen::Vector2d, int>> &restPts, 
                        vector<pair<Eigen::Vector2d, int>> &hull);

#endif