#include <ros/ros.h>
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
// #include <quick_hull2d/quick_hull2d.h>
#include <visualization_msgs/MarkerArray.h>
#include <random>
using namespace std;

ros::Publisher vis_pub_;
random_device rd_;
default_random_engine eng_;
uniform_real_distribution<double> rand_pos_;

vector<Eigen::Vector2d> pts_;
vector<pair<Eigen::Vector2d, int>> hull_;

void DebugPts(list<pair<Eigen::Vector2d, int>> &pts);
void DebugLine(const pair<Eigen::Vector2d, Eigen::Vector2d> &line);

void QuickHullSearch(const pair<Eigen::Vector2d, Eigen::Vector2d> &line, pair<Eigen::Vector2d, int>  &TopPt, list<pair<Eigen::Vector2d, int>> &restPts, 
                        vector<pair<Eigen::Vector2d, int>> &hull){
    list<pair<Eigen::Vector2d, int>> restPtsLeft, restPtsRight;
    pair<Eigen::Vector2d, Eigen::Vector2d> lineL, lineR;
    pair<Eigen::Vector2d, int> topPtLeft, topPtRight;
    topPtLeft.second = -1, topPtRight.second = -1;
    lineL.first = line.first;
    lineL.second = TopPt.first;
    lineR.first = TopPt.first;
    lineR.second = line.second;
    Eigen::Vector2d nL(lineL.first(1) - lineL.second(1), lineL.second(0) - lineL.first(0));
    Eigen::Vector2d nR(lineR.first(1) - lineR.second(1), lineR.second(0) - lineR.first(0));
    Eigen::Vector2d mL = lineL.second - lineL.first, mR = lineL.second - lineL.first;
    double dl, dr, dlm = 0, drm = 0, ll, lr, llm = mL.norm(), lrm = mR.norm();
    mL.normalize(), mR.normalize();

    for(auto &rp : restPts){
        dl = nL.dot(rp.first - lineL.first);
        if(dl > dlm){
            dlm = dl;
            if(topPtLeft.second != -1) restPtsLeft.emplace_back(topPtLeft);
            topPtLeft = rp;
        }
        else if(dl == dlm){
            ll = mL.dot(rp.first - lineL.first);
            if(ll < llm) {
                llm = ll;
                if(topPtLeft.second != -1) restPtsLeft.emplace_back(topPtLeft);
                topPtLeft = rp;
            }
        }
        else if(dl > 0){
            restPtsLeft.emplace_back(rp);
        }

        dr = nR.dot(rp.first - lineR.first);
        if(dr > drm){
            drm = dr;
            if(topPtRight.second != -1) restPtsRight.emplace_back(topPtRight);
            topPtRight = rp;
        }
        else if(dr == drm){
            lr = mR.dot(rp.first - lineL.first);
            if(lr < lrm) {
                lrm = lr;
                if(topPtRight.second != -1) restPtsRight.emplace_back(topPtRight);
                topPtRight = rp;
            }
        }
        else if(dr > 0){
            restPtsRight.emplace_back(rp);
        }
    }

    restPts.clear();

    if(topPtLeft.second != -1) {
        if(restPtsLeft.size() != 0) QuickHullSearch(lineL, topPtLeft, restPtsLeft, hull);
        else hull.emplace_back(topPtLeft);
    }

    hull.emplace_back(TopPt);

    if(topPtRight.second != -1) {
        if(restPtsRight.size() == 0) hull.emplace_back(topPtRight);
        else QuickHullSearch(lineR, topPtRight, restPtsRight, hull);
    }
}

void QuickHull(vector<Eigen::Vector2d> &pts, vector<pair<Eigen::Vector2d, int>> &hull){
    hull.clear();
    if(pts.size() <= 2){
        for(int i = 0; i < pts.size(); i++){
            // hullIdxs.emplace_back(i);
            hull.push_back({pts[i], i});
        }
        return;
    }

    pair<Eigen::Vector2d, Eigen::Vector2d> line, line2;
    int idx1, idx2;
    for(int i = 0; i < pts.size(); i++){
        if(i == 0){
            line.first = pts[i];
            line.second = pts[i];
            idx1 = 0, idx2 = 0;
        }
        else{
            if(pts[i](0) > line.second(0)) line.second = pts[i], idx2 = i;
            else if(pts[i](0) == line.second(0) && pts[i](1) > line.second(1)) line.second = pts[i], idx2 = i;
            if(pts[i](0) < line.first(0)) line.first = pts[i], idx1 = i;
            else if(pts[i](0) == line.first(0) && pts[i](1) < line.first(1)) line.first = pts[i], idx1 = i;

        }
    }



    list<pair<Eigen::Vector2d, int>> Upts, Dpts;

    pair<Eigen::Vector2d, int> topPtUp, topPtDown;
    topPtUp.second = -1, topPtDown.second = -1;
    
    Eigen::Vector2d Unorm(line.first(1) - line.second(1), line.second(0) - line.first(0));
    Unorm.normalize();
    double d, dmax = 0.0, dmin = 0.0, l, lu = (line.first - line.second).norm(), ld = (line.first - line.second).norm();

    Eigen::Vector2d mU = line.second - line.first, mD = line.first - line.second;
    mU.normalize(), mD.normalize();

    for(int i = 0; i < pts.size(); i++){
        if(i == idx1 || i == idx2) continue;
        else{
            d = Unorm.dot(pts[i] - line.first); 
            if(d > 0) {
                if(d > dmax){
                    if(topPtUp.second != -1) Upts.emplace_back(topPtUp);
                    dmax = d;
                    topPtUp = {pts[i], i};
                }
                else if(d == dmax){
                    l = mU.dot(pts[i] - line.first);
                    if(l < lu){
                        if(topPtUp.second != -1) Upts.emplace_back(topPtUp);
                        lu = l;
                        topPtUp = {pts[i], i};
                    }
                }
                else{
                    Upts.push_back({pts[i], i});
                }
            }
            else if(d < 0){
                if(d < dmin){
                    if(topPtDown.second != -1) Dpts.emplace_back(topPtDown);
                    dmin = d;
                    topPtDown = {pts[i], i};
                }
                else if(d == dmin){
                    l = mD.dot(pts[i] - line.second);
                    if(l < ld){
                        if(topPtDown.second != -1) Dpts.emplace_back(topPtDown);
                        ld = l;
                        topPtDown = {pts[i], i};
                    }
                }
                else{
                    Dpts.push_back({pts[i], i});
                }
            }
        }
    }
    hull.push_back({line.first, idx1});
    if(topPtUp.second != -1) {
        // DebugPts(Upts);
        // DebugLine(line);
        // getchar();
        if(Upts.size() > 0) QuickHullSearch(line, topPtUp, Upts, hull);
        // hull.emplace_back(topPtUp);

    }
    hull.push_back({line.second, idx2});


    if(topPtDown.second != -1) {
        // hull.emplace_back(topPtDown);
        if(Dpts.size() > 0) {
            line2.first = line.second;
            line2.second = line.first;
            // DebugPts(Dpts);
            // DebugLine(line2);
            // getchar();
            QuickHullSearch(line2, topPtDown, Dpts, hull);
        }
    }

    // QuickHullSearch(line, Upts, hull);
    // QuickHullSearch(line2, Dpts, hull);

}



void HullVis(){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(2);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 0;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::SPHERE_LIST;
    mka.markers[0].scale.x = 0.4;
    mka.markers[0].scale.y = 0.4;
    mka.markers[0].scale.z = 0.2;
    mka.markers[0].color.a = 0.7;
    mka.markers[0].color.g = 0.9;

    mka.markers[1] = mka.markers[0];
    mka.markers[1].id = 1;
    mka.markers[1].scale.x = 0.05;
    mka.markers[1].scale.y = 0.05;
    mka.markers[1].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[1].color.g = 0.5;
    mka.markers[1].color.r = 0.9;
    mka.markers[1].color.a = 0.9;


    geometry_msgs::Point pt, pt1, pt2;
    for(auto &p : pts_){
        pt.x = p(0);
        pt.y = p(1);
        pt.z = 0.0;
        mka.markers[0].points.emplace_back(pt);
    }


    for(int i = 0; i < hull_.size(); i++){
        pt.x = hull_[i].first(0);
        pt.y = hull_[i].first(1);
        cout<< hull_[i].first.transpose()<<endl;
        pt.z = 0.3;
        mka.markers[1].points.emplace_back(pt);
    }
    vis_pub_.publish(mka);
}

void DebugPts(list<pair<Eigen::Vector2d, int>> &pts){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(2);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 10;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::SPHERE_LIST;
    mka.markers[0].scale.x = 0.4;
    mka.markers[0].scale.y = 0.4;
    mka.markers[0].scale.z = 0.2;
    mka.markers[0].color.a = 0.7;
    mka.markers[0].color.b = 0.9;
    // mka.markers
    geometry_msgs::Point pt;
    for(auto &p : pts){
        pt.x = p.first(0);
        pt.y = p.first(1);
        pt.z = 0.3;
        mka.markers[0].points.emplace_back(pt);
    }

    vis_pub_.publish(mka);
}

void DebugLine(const pair<Eigen::Vector2d, Eigen::Vector2d> &line){
    visualization_msgs::MarkerArray mka;
    mka.markers.resize(2);
    mka.markers[0].header.frame_id = "world";
    mka.markers[0].header.stamp = ros::Time::now();
    mka.markers[0].id = 11;
    mka.markers[0].action = visualization_msgs::Marker::ADD;
    mka.markers[0].type = visualization_msgs::Marker::LINE_STRIP;
    mka.markers[0].scale.x = 0.1;
    mka.markers[0].scale.y = 0.1;
    mka.markers[0].scale.z = 0.2;
    mka.markers[0].color.a = 0.9;
    mka.markers[0].color.b = 0.9;
    mka.markers[0].color.r = 0.9;

    geometry_msgs::Point pt;

    pt.x = line.first(0);
    pt.y = line.first(1);
    pt.z = 0;
    mka.markers[0].points.emplace_back(pt);

    pt.x = line.second(0);
    pt.y = line.second(1);
    pt.z = 0;
    mka.markers[0].points.emplace_back(pt);

    vis_pub_.publish(mka);
}

int main(int argc, char** argv){
    ros::init(argc, argv, "demo");
    ros::NodeHandle nh;

    vis_pub_ = nh.advertise<visualization_msgs::MarkerArray>("demo_vis", 100);
    eng_ = default_random_engine(rd_());
    rand_pos_ = uniform_real_distribution<double>(-20.0, 20.0);

    while(1){
        getchar();
        ROS_WARN("generte");
        pts_.clear();
        hull_.clear();
        for(int i = 0; i < 50; i++){
            Eigen::Vector2d p;
            p(0) = rand_pos_(eng_);
            p(0) = 1.0;
            p(1) = rand_pos_(eng_);
            pts_.emplace_back(p);
        }
        ROS_WARN("sample");
        double t = ros::WallTime::now().toSec();
        QuickHull(pts_, hull_);
        cout<<"cost:"<<ros::WallTime::now().toSec() - t<<endl;
        cout<<"hull_:"<<hull_.size()<<endl;
        HullVis();
    }

    return 0;
}

