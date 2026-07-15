#include <quick_hull2d/quick_hull2d.h>
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

void QuickHullSearch(const pair<Eigen::Vector2d, Eigen::Vector2d> &line, const pair<Eigen::Vector2d, int>  &TopPt, list<pair<Eigen::Vector2d, int>> &restPts, 
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