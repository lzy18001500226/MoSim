/*
    MIT License

    Copyright (c) 2021 Zhepei Wang (wangzhepei@live.com)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
*/

#ifndef GCOPTER_COVER_HPP
#define GCOPTER_COVER_HPP

#include "gcopter/minco.hpp"
#include "gcopter/geo_utils.hpp"
#include "gcopter/lbfgs.hpp"

#include <Eigen/Eigen>

#include <cmath>
#include <cfloat>
#include <iostream>
#include <vector>

namespace gcopter
{

    class GCOPTER_COVER_PolytopeSFC
    {
    public:
        typedef Eigen::Matrix3Xd PolyhedronV;
        typedef Eigen::MatrixX4d PolyhedronH;
        typedef std::vector<Eigen::Matrix3Xd> CoverTargets;
        typedef std::vector<PolyhedronV> PolyhedraV;
        typedef std::vector<PolyhedronH> PolyhedraH;
        Eigen::Matrix3Xd debugpts;
    private:
        minco::MINCO_S3NU_PY minco;
        // minco::MINCO_S3NU minco;
        // flatness::FlatnessMap flatmap;

        Eigen::MatrixX4d cameraFOV;
        CoverTargets targets;
        double rho;// phi;
        // double minT;
        Eigen::Matrix<double, 4, 3> headPVA;
        Eigen::Matrix<double, 4, 3> tailPVA;

        Eigen::Matrix3Xd vEndVel;
        PolyhedraV vPolytopes;
        Eigen::Vector2d EndDy;
        std::vector<std::pair<double, double>> yawRange;
        PolyhedraH hPolytopes;
        // Eigen::Matrix3Xd shortPath;
        // Eigen::VectorXd yawPath;

        Eigen::VectorXi pieceIdx;
        Eigen::VectorXi vPolyIdx;
        Eigen::VectorXi hPolyIdx;
        // Eigen::VectorXi fixYpIdx; // fix pt, yaw free

        int polyN;
        int pieceN;

        int endVelDim;
        int spatialDim;
        int temporalDim;
        int yawDim;

        double smoothEps;
        int integralRes;
        Eigen::VectorXd magnitudeBd;
        Eigen::VectorXd penaltyWt;
        // Eigen::VectorXd physicalPm;
        // double allocSpeed;
        double allocSpeed, allocYawSpeed;

        lbfgs::lbfgs_parameter_t lbfgs_params;

        Eigen::Matrix4Xd points; //interpoints
        Eigen::VectorXd times;
        Eigen::Matrix4Xd gradByPoints; //interpoints grad
        Eigen::VectorXd gradByTimes;
        Eigen::VectorXd gradByEndVel;
        Eigen::MatrixX4d partialGradByCoeffs; 
        Eigen::VectorXd partialGradByTimes; 

    private:
        /**
         * @brief get T from tau
         * 
         * @param tau \in R^n
         * @param T   the interval of each segment
         */
        static inline void forwardT(const Eigen::VectorXd &tau,
                                    Eigen::VectorXd &T)
        {
            const int sizeTau = tau.size();
            T.resize(sizeTau);
            for (int i = 0; i < sizeTau; i++)
            {
                T(i) = tau(i) > 0.0
                           ? ((0.5 * tau(i) + 1.0) * tau(i) + 1.0)
                           : 1.0 / ((0.5 * tau(i) - 1.0) * tau(i) + 1.0);
            }
            return;
        }

        /**
         * @brief  map T to tau
         *      since optimizer wishes to optimize tau without constraints, while T >= 0.
         *      tau > 0: T = 1/2 tau^2 + tau + 1; tau <= 0: T = 2/(tau^2 - tau + 1); R ---> R+
         * @tparam EIGENVEC 
         * @param T   the interval of each segment
         * @param tau \in R^n
         */
        template <typename EIGENVEC>
        static inline void backwardT(const Eigen::VectorXd &T,
                                     EIGENVEC &tau)
        {
            const int sizeT = T.size();
            tau.resize(sizeT);
            for (int i = 0; i < sizeT; i++)
            {
                tau(i) = T(i) > 1.0
                             ? (sqrt(2.0 * T(i) - 1.0) - 1.0)
                             : (1.0 - sqrt(2.0 / T(i) - 1.0));
            }

            return;
        }

        /**
         * @brief get the grad of tau using grad of T
         * 
         * @tparam EIGENVEC 
         * @param tau 
         * @param gradT 
         * @param gradTau 
         */
        template <typename EIGENVEC>
        static inline void backwardGradT(const Eigen::VectorXd &tau,
                                         const Eigen::VectorXd &gradT,
                                         EIGENVEC &gradTau)
        {
            const int sizeTau = tau.size();
            gradTau.resize(sizeTau);
            double denSqrt;
            for (int i = 0; i < sizeTau; i++)
            {
                if (tau(i) > 0)
                {
                    gradTau(i) = gradT(i) * (tau(i) + 1.0);
                }
                else
                {
                    denSqrt = (0.5 * tau(i) - 1.0) * tau(i) + 1.0;
                    gradTau(i) = gradT(i) * (1.0 - tau(i)) / (denSqrt * denSqrt);
                }
            }
            return;
        }

        static inline void forwardV(const Eigen::Matrix3Xd &vEndVelocity,
                                    const Eigen::VectorXd &evi,
                                    const Eigen::Vector2d &vEndyaw,
                                    const Eigen::VectorXd &eyawi,
                                    Eigen::Vector3d &endv,
                                    double &endDy){
            const int k = vEndVelocity.cols();
            Eigen::VectorXd q = evi.normalized().head(k-1);
            endv = vEndVelocity.rightCols(k-1) * q.cwiseProduct(q) + vEndVelocity.col(0);
            double qy = eyawi.normalized()(0);
            endDy = vEndyaw(0) + vEndyaw(1) * qy * qy;
        }

        /**
         * @brief get mid points(mid points are neccessary for formulating MINCO)
         * 
         * @param xi        the weight of each vector 
         * @param vIdx      the index of corresponding vPolys(path is shortten, some vPolys are abandoned)
         * @param vPolys    the vector expression of polytopes([start vetex, vector_1, ..., vectorn_n)
         * @param P         the out put mid points
         */
        static inline void forwardP(const Eigen::VectorXd &xi,
                                    const Eigen::VectorXi &vIdx,
                                    const PolyhedraV &vPolys,
                                    const std::vector<std::pair<double, double>> &yRange,
                                    const Eigen::VectorXd &yi,
                                    Eigen::Matrix4Xd &P)
        {
            const int sizeP = vIdx.size();
            // std::cout<<"forwardP0"<<std::endl;
            P.resize(4, sizeP);
            // std::cout<<"sizeP:"<<sizeP<<std::endl;

            Eigen::VectorXd q;
            double qy;
            for (int i = 0, j = 0, k, l; i < sizeP; i++, j += k)
            {
                l = vIdx(i);
                // std::cout<<"l:"<<l<<std::endl;
                // std::cout<<"vPolys:"<<vPolys.size()<<std::endl;
                k = vPolys[l].cols();
                // std::cout<<"xi:"<<xi.size()<<std::endl;
                // std::cout<<"j:"<<j<<" k:"<<k<<std::endl;
                q = xi.segment(j, k).normalized().head(k - 1);
                // std::cout<<"P:"<<P.cols()<<std::endl;
                P.col(i).head(3) = vPolys[l].rightCols(k - 1) * q.cwiseProduct(q) +
                           vPolys[l].col(0);
                // std::cout<<"yi:"<<yi.size()<<std::endl;
                qy = yi.segment(i * 2, 2).normalized()(0);
                // P.col(i)(3) = yi(i);
                // if(i >= yRange.size()) std::cout<<"???"<<std::endl;
                P.col(i)(3) = yRange[i].second * qy * qy + yRange[i].first;
            }
            return;
        }
        // static inline void forwardP(const Eigen::VectorXd &xi,
        //                             const Eigen::VectorXi &vIdx,
        //                             const PolyhedraV &vPolys,
        //                             const std::vector<std::pair<double, double>> &yRange,
        //                             const Eigen::VectorXd &yi,
        //                             const Eigen::VectorXi &fixIdx,
        //                             Eigen::Matrix4Xd &P)
        // {
        //     const int sizeP = vIdx.size();
        //     // std::cout<<"forwardP0"<<std::endl;
        //     P.resize(4, sizeP);
        //     // std::cout<<"sizeP:"<<sizeP<<std::endl;
        //     int f_size = fixIdx.size();

        //     Eigen::VectorXd q;
        //     double qy;
        //     for (int i = 0, j = 0, m = 0, k, l; i < sizeP; i++)
        //     {

        //         if(m < f_size && i == fixIdx(m)){
        //             m++;
        //             continue;
        //         }
        //         l = vIdx(i);
        //         // std::cout<<"l:"<<l<<std::endl;
        //         // std::cout<<"vPolys:"<<vPolys.size()<<std::endl;
        //         k = vPolys[l].cols();
        //         // std::cout<<"xi:"<<xi.size()<<std::endl;
        //         // std::cout<<"j:"<<j<<" k:"<<k<<std::endl;
        //         q = xi.segment(j, k).normalized().head(k - 1);
        //         // std::cout<<"P:"<<P.cols()<<std::endl;
        //         P.col(i).head(3) = vPolys[l].rightCols(k - 1) * q.cwiseProduct(q) +
        //                    vPolys[l].col(0);
        //         // // std::cout<<"yi:"<<yi.size()<<std::endl;
        //         // qy = yi.segment(i * 2, 2).normalized()(0);
        //         // // P.col(i)(3) = yi(i);
        //         // // if(i >= yRange.size()) std::cout<<"???"<<std::endl;
        //         // P.col(i)(3) = yRange[i].second * qy * qy + yRange[i].first;
        //         // j += k;
        //     }
        //     for (int i = 0, j = 0, k; i < sizeP; i++, j += k)
        //     {
        //         qy = yi.segment(i * 2, 2).normalized()(0);
        //         // P.col(i)(3) = yi(i);
        //         // if(i >= yRange.size()) std::cout<<"???"<<std::endl;
        //         P.col(i)(3) = yRange[i].second * qy * qy + yRange[i].first;
        //         // j += k;
        //     }
        //     return;
        // }

        /**
         * @brief the interface of BFGS
         * 
         * @param ptr 
         * @param xi     optimization variable
         * @param gradXi 
         * @return objective cost 
         */
        static inline double costTinyNLS(void *ptr,
                                         const Eigen::VectorXd &xi,
                                         Eigen::VectorXd &gradXi)
        {
            const int n = xi.size();
            const Eigen::Matrix3Xd &ovPoly = *(Eigen::Matrix3Xd *)ptr;

            const double sqrNormXi = xi.squaredNorm();
            const double invNormXi = 1.0 / sqrt(sqrNormXi);
            const Eigen::VectorXd unitXi = xi * invNormXi;
            const Eigen::VectorXd r = unitXi.head(n - 1);
            const Eigen::Vector3d delta = ovPoly.rightCols(n - 1) * r.cwiseProduct(r) +
                                          ovPoly.col(1) - ovPoly.col(0);

            double cost = delta.squaredNorm();
            gradXi.head(n - 1) = (ovPoly.rightCols(n - 1).transpose() * (2 * delta)).array() *
                                 r.array() * 2.0;
            gradXi(n - 1) = 0.0;
            gradXi = (gradXi - unitXi.dot(gradXi) * unitXi).eval() * invNormXi;

            const double sqrNormViolation = sqrNormXi - 1.0;
            if (sqrNormViolation > 0.0)
            {
                double c = sqrNormViolation * sqrNormViolation;
                const double dc = 3.0 * c;
                c *= sqrNormViolation;
                cost += c;
                gradXi += dc * 2.0 * xi; 
            }

            return cost; 
        }

        /**
         * @brief map mid points to weights of polytope vectors
         * since mid points are constrained in convex hulls, while optimizer wish free optimization, square weights are used
         * besides, polytope may not be a simplex，optimization is used in this function
         * 
         * @tparam EIGENVEC 
         * @param P         mid points
         * @param vIdx      index of corresponding polytope
         * @param vPolys    all the polytopes
         * @param xi        weights
         */
        template <typename EIGENVEC>
        static inline void backwardP(const Eigen::Matrix4Xd &P,
                                     const Eigen::VectorXi &vIdx,
                                     const PolyhedraV &vPolys,
                                     EIGENVEC &xi)
        {
            const int sizeP = P.cols();

            double minSqrD;
            lbfgs::lbfgs_parameter_t tiny_nls_params;
            tiny_nls_params.past = 0;
            tiny_nls_params.delta = 1.0e-5;
            tiny_nls_params.g_epsilon = FLT_EPSILON;
            tiny_nls_params.max_iterations = 128;

            Eigen::Matrix3Xd ovPoly;
            for (int i = 0, j = 0, k, l; i < sizeP; i++, j += k)
            {
                l = vIdx(i);
                k = vPolys[l].cols(); 
                //ovPoly: [pathpoint vertex1 ... vertexk]
                ovPoly.resize(3, k + 1);
                ovPoly.col(0) = P.col(i).head(3);
                ovPoly.rightCols(k) = vPolys[l];
                Eigen::VectorXd x(k);
                x.setConstant(sqrt(1.0 / k));
                lbfgs::lbfgs_optimize(x,
                                      minSqrD,
                                      &GCOPTER_PolytopeSFC::costTinyNLS,
                                      nullptr,
                                      nullptr,
                                      &ovPoly,
                                      tiny_nls_params);

                xi.segment(j, k) = x;
            }

            return;
        }

        /**
         * @brief get the grad of weights
         * 
         * @tparam EIGENVEC 
         * @param xi        weights 
         * @param vIdx      index of corresponding polytope
         * @param vPolys    all the polytopes
         * @param gradP     grad of mid points
         * @param gradXi    grad of weights
         */
        template <typename EIGENVEC>
        static inline void backwardGradP(const Eigen::VectorXd &xi,
                                         const Eigen::VectorXi &vIdx,
                                         const PolyhedraV &vPolys,
                                         const Eigen::VectorXd &yi,
                                         const std::vector<std::pair<double, double>> &yRange,
                                         const Eigen::Matrix4Xd &gradP,
                                         EIGENVEC &gradXi,
                                         EIGENVEC &gradYi)
        {
            const int sizeP = vIdx.size();
            gradXi.resize(xi.size());

            double normInv;
            Eigen::VectorXd q, gradQ, unitQ;
            for (int i = 0, j = 0, k, l; i < sizeP; i++, j += k)
            {
                l = vIdx(i);
                k = vPolys[l].cols();
                q = xi.segment(j, k);
                normInv = 1.0 / q.norm();
                unitQ = q * normInv;
                gradQ.resize(k);
                gradQ.head(k - 1) = (vPolys[l].rightCols(k - 1).transpose() * gradP.col(i).head(3)).array() *
                                    unitQ.head(k - 1).array() * 2.0;
                gradQ(k - 1) = 0.0;
                gradXi.segment(j, k) = (gradQ - unitQ * unitQ.dot(gradQ)) * normInv;

                q = yi.segment(i*2, 2);
                normInv = 1.0 / q.norm();
                unitQ = q * normInv;
                gradQ.resize(2);
                gradQ(0) = (yRange[i].second * gradP.col(i)(3)) *
                                    unitQ(0) * 2.0;
                gradQ(1) = 0.0;
                gradYi.segment(i * 2, 2) = (gradQ - unitQ * unitQ.dot(gradQ)) * normInv;
                // gradYi(i) = gradP.col(i)(3);
                // if(i >= gradYi.size()) std::cout<<"gradYi out!!!!!!!!"<<std::endl;
            }

            return;
        }

        template <typename EIGENVEC>
        static inline void backwardGradV(const Eigen::VectorXd &gradv,
                                         const Eigen::VectorXd &evi,
                                         const Eigen::Matrix3Xd &vEndVelocity,
                                         const Eigen::VectorXd &edyi,
                                         const Eigen::Vector2d &vEndDy,
                                         EIGENVEC &gradEvi,
                                         EIGENVEC &gradDy){
            gradEvi.resize(evi.size());
            Eigen::VectorXd q, gradQ, unitQ;
            double normInv;
            int k = vEndVelocity.cols();
            q = evi;
            normInv = 1.0 / q.norm();
            unitQ = q * normInv;
            gradQ.resize(k);
            gradQ.head(k - 1) = (vEndVelocity.rightCols(k - 1).transpose() * gradv.head(3)).array() *
                                unitQ.head(k - 1).array() * 2.0;
            gradQ(k - 1) = 0.0;
            gradEvi = (gradQ - unitQ * unitQ.dot(gradQ)) * normInv;

            gradDy.resize(edyi.size());
            k = 2;
            q = edyi;
            normInv = 1.0 / q.norm();
            unitQ = q * normInv;
            gradQ.resize(k);
            gradQ(0) = (vEndDy(1) * gradv(3)) *
                                unitQ(0) * 2.0;
            gradQ(1) = 0.0;
            gradDy = (gradQ - unitQ * unitQ.dot(gradQ)) * normInv;

        }

        /**
         * @brief a special cost function,  stabilize the norm of xi at 1 
         * 
         * @tparam EIGENVEC 
         * @param xi 
         * @param vIdx 
         * @param vPolys 
         * @param cost 
         * @param gradXi 
         */
        template <typename EIGENVEC>
        static inline void normRetrictionLayer(const Eigen::VectorXd &xi,
                                               const Eigen::VectorXi &vIdx,
                                               const PolyhedraV &vPolys,
                                               const Eigen::VectorXd &yi,
                                               double &cost,
                                               EIGENVEC &gradXi, 
                                               EIGENVEC &gradYi)
        {
            const int sizeP = vIdx.size();
            gradXi.resize(xi.size());

            double sqrNormQ, sqrNormViolation, c, dc;
            Eigen::VectorXd q;
            Eigen::VectorXd qy;
            for (int i = 0, j = 0, k; i < sizeP; i++, j += k)
            {
                k = vPolys[vIdx(i)].cols();

                q = xi.segment(j, k);
                sqrNormQ = q.squaredNorm();
                sqrNormViolation = sqrNormQ - 1.0;
                if (sqrNormViolation > 0.0)
                {
                    c = sqrNormViolation * sqrNormViolation;
                    dc = 3.0 * c;
                    c *= sqrNormViolation;
                    cost += c;
                    gradXi.segment(j, k) += dc * 2.0 * q;
                }

                qy = yi.segment(i*2, 2);
                sqrNormQ = qy.squaredNorm();
                sqrNormViolation = sqrNormQ - 1.0;
                if (sqrNormViolation > 0.0)
                {
                    c = sqrNormViolation * sqrNormViolation;
                    dc = 3.0 * c;
                    c *= sqrNormViolation;
                    cost += c;
                    gradYi.segment(i*2, 2) += dc * 2.0 * qy;
                }
            }

            return;
        }

        template <typename EIGENVEC>
        static inline void normRetrictionLayerV(const Eigen::VectorXd &evi,
                                                const Eigen::VectorXd &edyi,
                                               double &cost,
                                               EIGENVEC &gradEvi,
                                               EIGENVEC &gradEdyi)
        {
            double sqrNormQ, sqrNormViolation, c, dc;
            Eigen::VectorXd q;
            q = evi;
            sqrNormQ = q.squaredNorm();
            sqrNormViolation = sqrNormQ - 1.0;
            if (sqrNormViolation > 0.0)
            {
                c = sqrNormViolation * sqrNormViolation;
                dc = 3.0 * c;
                c *= sqrNormViolation;
                cost += c;
                gradEvi += dc * 2.0 * q;
            }

            q = edyi;
            sqrNormQ = q.squaredNorm();
            sqrNormViolation = sqrNormQ - 1.0;
            if (sqrNormViolation > 0.0)
            {
                c = sqrNormViolation * sqrNormViolation;
                dc = 3.0 * c;
                c *= sqrNormViolation;
                cost += c;
                gradEdyi += dc * 2.0 * q;
            }
            return;
        }
        /**
         * @brief a smooth punish function, punish if x > mu
         * 
         * @param x 
         * @param mu    the punish threshold
         * @param f     punish cost
         * @param df    grad of x
         * @return true 
         * @return false 
         */
        static inline bool smoothedL1(const double &x,
                                      const double &mu,
                                      double &f,
                                      double &df)
        {
            if (x < 0.0)
            {
                return false;
            }
            else if (x > mu)
            {
                f = x - 0.5 * mu;
                df = 1.0;
                return true;
            }
            else
            {
                const double xdmu = x / mu;
                const double sqrxdmu = xdmu * xdmu;
                const double mumxd2 = mu - 0.5 * x;
                f = mumxd2 * sqrxdmu * xdmu;
                df = sqrxdmu * ((-0.5) * xdmu + 3.0 * mumxd2 / mu);
                return true;
            }
        }


        static inline void coverCost(   const Eigen::VectorXd &T,
                                        const Eigen::MatrixX4d &coeffs,
                                        const Eigen::VectorXi &coverIdx,
                                        const Eigen::MatrixX4d &cameraFov,
                                        const CoverTargets &coverTargets,
                                        const double &smoothFactor,
                                        const double &penaltyWeight,
                                        double &cost,
                                        Eigen::VectorXd &gradT,
                                        Eigen::MatrixX4d &gradC){
            const int coverNum = coverIdx.size();
            double s1, s2, s3, s4, s5;
            Eigen::Matrix<double, 6, 1> beta0, beta1, beta2, beta3;
            Eigen::Vector4d pos, vel, acc, jer;
            Eigen::Vector3d z, az;

            Eigen::Vector3d outerNormal;
            Eigen::Vector3d pc; //target point in camera frame
            Eigen::Vector3d dps;
            Eigen::Matrix3d W2C; // world to camera
            Eigen::Vector4d q;
            Eigen::Vector3d gradPc, gradZ, gradPos;
            Eigen::Vector4d gradQ, gradP, gradA;
            double gradYaw;
            double violaPc, violaPcPena, violaPcPenaD;
            Eigen::Matrix<double, 4, 3> Pc_d_q;
            Eigen::Matrix<double, 3, 4> q_d_z;
            Eigen::Vector4d y_d_q;
            Eigen::Matrix3d z_d_a;
            //Pc_d_q==>pcx_d_qw, pcy_d_qw, pcz_d_qw,
            //         pcx_d_qx, pcy_d_qx, pcz_d_qx,
            //         pcx_d_qy, pcy_d_qy, pcz_d_qy,
            //         pcx_d_qz, pcy_d_qz, pcz_d_qz;
            double pena;
            // double sqrt_2 = sqrt(2);
            // double sqrt_2_inv = 1.0 / sqrt(2);

            for(int i = 0; i < coverNum; i++){
                // Eigen::Matrix3d R;
                // Eigen::MatrixX4d rotatedFov; 
                int seg = coverIdx(i);
                const Eigen::Matrix<double, 6, 4> &c = coeffs.block<6, 4>(seg * 6, 0);
                const double t = T(seg);
                s1 = t;
                s2 = s1 * s1;
                s3 = s2 * s1;
                s4 = s2 * s2;
                s5 = s4 * s1;
                beta0(0) = 1.0, beta0(1) = s1, beta0(2) = s2, beta0(3) = s3, beta0(4) = s4, beta0(5) = s5;
                beta1(0) = 0.0, beta1(1) = 1.0, beta1(2) = 2.0 * s1, beta1(3) = 3.0 * s2, beta1(4) = 4.0 * s3, beta1(5) = 5.0 * s4;
                beta2(0) = 0.0, beta2(1) = 0.0, beta2(2) = 2.0, beta2(3) = 6.0 * s1, beta2(4) = 12.0 * s2, beta2(5) = 20.0 * s3;
                beta3(0) = 0.0, beta3(1) = 0.0, beta3(2) = 0.0, beta3(3) = 6.0, beta3(4) = 24.0 * s1, beta3(5) = 60.0 * s2;

                pos = c.transpose() * beta0;
                vel = c.transpose() * beta1;
                acc = c.transpose() * beta2;
                jer = c.transpose() * beta3;
                az = acc.head(3);
                az(2) += 9.8;
                z = az.normalized();

                double sqrt_2_1pz2 = sqrt(2*(1 + z(2)));
                double sqrt_2_1pz2_inv = 1.0 / sqrt_2_1pz2;
                double yaw2 = pos(3) * 0.5;
                double siny2 = sin(yaw2);
                double cosy2 = cos(yaw2);
                q(0) = (1 + z(2))*cosy2;
                q(1) = -z(1)*cosy2 + z(0)*siny2;
                q(2) = z(0)*cosy2 + z(1)*siny2;
                q(3) = (1 + z(2))*siny2;
                q *= sqrt_2_1pz2_inv;

                q_d_z.setZero();
                q_d_z(0, 1) = siny2 * sqrt_2_1pz2_inv;
                q_d_z(0, 2) = cosy2 * sqrt_2_1pz2_inv;
                q_d_z(1, 1) = -cosy2 * sqrt_2_1pz2_inv;
                q_d_z(1, 2) = siny2 * sqrt_2_1pz2_inv;
                q_d_z(2, 1) = -q(1) * sqrt_2_1pz2_inv * sqrt_2_1pz2_inv;
                q_d_z(2, 2) = -q(2) * sqrt_2_1pz2_inv * sqrt_2_1pz2_inv;
                q_d_z(2, 0) = cosy2 * sqrt_2_1pz2_inv * 0.5;
                q_d_z(2, 3) = siny2 * sqrt_2_1pz2_inv * 0.5;

                double qxy, qxz, qxw, qyz, qyw, qzw, qxx, qyy, qzz;// qww; 
                qxy = q(1) * q(2);
                qxz = q(1) * q(3);
                qxw = q(1) * q(0);
                qyz = q(2) * q(3);
                qyw = q(2) * q(0);
                qzw = q(3) * q(0);
                qxx = q(1) * q(1);
                qyy = q(2) * q(2);
                qzz = q(3) * q(3);
                // qww = q.w() * q.w();

                W2C <<  1-2*(qyy+qzz), 2*(qxy + qzw), 2*(qxz - qyw),
                        2*(qxy - qzw), 1-2*(qxx+qzz), 2*(qyz + qxw),
                        2*(qxz + qyw), 2*(qyz - qxw), 1-2*(qxx+qyy);

                double cosy2_d_y = -siny2*0.5;
                double siny2_d_y = cosy2*0.5;
                y_d_q(0) = (1 + z(2)) * cosy2_d_y;
                y_d_q(1) = -z(1)*cosy2_d_y + z(0)*siny2_d_y;
                y_d_q(2) = z(0)*cosy2_d_y + z(1)*siny2_d_y;
                y_d_q(3) = (1 + z(2))*siny2_d_y;
                y_d_q *= sqrt_2_1pz2_inv;

                double anorm = az.norm(), anorm3 = anorm * anorm * anorm, anorm_inv = 1.0 / anorm, anorm3_inv = 1.0 / anorm3;
                double m11 =anorm_inv - az(0)*az(0)*anorm3_inv, m22 = anorm_inv - az(1)*az(1)*anorm3_inv, m33 = anorm_inv - az(2)*az(2)*anorm3_inv,
                    m12 = -az(0)*az(1)*anorm3_inv, m13 = -az(0)*az(2)*anorm3_inv, m23 = -az(1)*az(2)*anorm3_inv;
                z_d_a << m11, m12, m13,
                        m12, m22, m23, 
                        m13, m23, m33;   

                int k = coverTargets[i].cols();
                // if(k <=0 ) std::cout<<"empty cover!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"<<std::endl;
                pena = 0;
                double pen;
                if(k > 0) pen = 1.0 / k * penaltyWeight;
                bool fail_cover;

                gradA.setZero();
                gradP.setZero();

                for(int j = 0; j < k; j++){
                    fail_cover = false;
                    dps = coverTargets[i].col(j) - pos.head(3);
                    pc = W2C * (coverTargets[i].col(j) - pos.head(3));
                    int l = cameraFov.rows();
                    gradPc.setZero();
                    for(int m = 0; m < l; m++){
                        outerNormal = cameraFov.block<1, 3>(m, 0);
                        violaPc = outerNormal.dot(pc.head(3)) + cameraFov(m, 3);
                        if (smoothedL1(violaPc, smoothFactor, violaPcPena, violaPcPenaD))
                        {
                            fail_cover = true;
                            gradPc += pen * violaPcPenaD * outerNormal;
                            pena += pen * violaPcPena;
                        }
                    }

                    if(!fail_cover) continue;

                    Pc_d_q <<   2*(q(3)*dps(1) - q(2)*dps(2))             , 2*(-q(3)*dps(0) + q(1)*dps(2))               , 2*(q(2)*dps(0)-q(1)*dps(1)),
                                2*(q(2)*dps(1) + q(3)*dps(2))             , 2*(q(2)*dps(0) - 2*q(1)*dps(1) + q(0)*dps(2)), 2*(q(3)*dps(0)-q(0)*dps(1)-2*q(1)*dps(2)),
                                2*(-2*q(2)*dps(0)+q(1)*dps(1)-q(0)*dps(2)), 2*(q(1)*dps(0) + q(3)*dps(2))                , 2*(q(0)*dps(0)+q(3)*dps(1)-2*q(2)*dps(2)),
                                2*(-2*q(3)*dps(0)+q(0)*dps(1)+q(1)*dps(2)), 2*(-q(0)*dps(0) -2*q(3)*dps(1) + q(2)*dps(2)), 2*(q(1)*dps(0)+q(2)*dps(1));
                    gradQ = Pc_d_q * gradPc;
                    gradZ = q_d_z * gradQ;

                    gradYaw = gradQ.transpose() * y_d_q;

                    gradPos = -W2C.transpose() * gradPc; // checked
                    gradP.head(3) += gradPos;
                    gradP(3) += gradYaw;

                    gradA.head(3) += z_d_a * gradZ;
                }

                gradC.block<6, 4>(seg * 6, 0) += (beta0 * gradP.transpose() +
                                beta2 * gradA.transpose());
                gradT(seg) += gradP.dot(vel) + gradA.dot(jer);
                cost += pena;
            }
        }

        /**
         * @brief user define discrete cost. for inequality constraint 
         * and integral functions that are difficult to be expressed analytically 
         * 
         * @param T                     intervals
         * @param coeffs                polynomial params
         * @param hIdx                  index of corresponding polytopes
         * @param hPolys                all the polytopes
         * @param smoothFactor          the mu in smoothedL1
         * @param integralResolution    the number of discrete pieces
         * @param magnitudeBounds       user define, here [v_max, a_max,]^T 
         * @param penaltyWeights        [pos_weight, vel_weight, acc_weight]^T
         * @param cost                  objective cost
         * @param gradT                 grad of intervals
         * @param gradC                 grad of coeffs
         */
        static inline void attachPenaltyFunctional(const Eigen::VectorXd &T,
                                                const Eigen::MatrixX4d &coeffs,
                                                const Eigen::VectorXi &hIdx,
                                                const PolyhedraH &hPolys,
                                                const double &smoothFactor,
                                                const int &integralResolution,
                                                const Eigen::VectorXd &magnitudeBounds,
                                                const Eigen::VectorXd &penaltyWeights,
                                                // const Eigen::VectorXi &coverIdx,
                                                const Eigen::MatrixX4d &cameraFov,
                                                const CoverTargets &coverTargets,
                                                double &cost,
                                                Eigen::VectorXd &gradT,
                                                Eigen::MatrixX4d &gradC){
            const double velSqrMax = magnitudeBounds(0) * magnitudeBounds(0);
            const double accSqrMax = magnitudeBounds(1) * magnitudeBounds(1);
            const double jerSqrMax = magnitudeBounds(2) * magnitudeBounds(2);
            const double dyawMax = magnitudeBounds(3) * magnitudeBounds(3);
            const double ddyawMax = magnitudeBounds(4) * magnitudeBounds(4);
            const double zMin = magnitudeBounds(5);

            const double weightPos = penaltyWeights(0);
            const double weightVel = penaltyWeights(1);
            const double weightAcc = penaltyWeights(2);
            const double weightJer = penaltyWeights(3);
            const double weightDyaw = penaltyWeights(4);
            const double weightDdyaw = penaltyWeights(5);
            const double weightCover = penaltyWeights(7);
            const double weightZ = penaltyWeights(8);

            // const double weightJer = penaltyWeights(6);

            Eigen::Vector4d pos, vel, acc, jer, sna;
            Eigen::Vector4d gradPos, gradVel, gradAcc, gradJer;

            Eigen::Vector3d z, az;

            Eigen::Vector3d outerNormal;
            Eigen::Vector3d pc; //target point in camera frame
            Eigen::Vector3d dps;
            Eigen::Matrix3d W2C; // world to camera
            Eigen::Vector4d q;
            Eigen::Vector3d gradPc, gradZ, gradPosCov;
            Eigen::Vector4d gradQ, gradP, gradA;
            double gradYaw;
            double violaPc, violaPcPena, violaPcPenaD;
            Eigen::Matrix<double, 4, 3> Pc_d_q;
            Eigen::Matrix<double, 3, 4> q_d_z;
            Eigen::Vector4d y_d_q;
            Eigen::Matrix3d z_d_a;
            double qxy, qxz, qxw, qyz, qyw, qzw, qxx, qyy, qzz;// qww; 

            double step, alpha;
            double s1, s2, s3, s4, s5;
            Eigen::Matrix<double, 6, 1> beta0, beta1, beta2, beta3, beta4;
            int K, L, /*M,*/ cn;
            double node, pena;
            double violaPos, violaVel, violaAcc, violaAccZ, violaJer, violaDyaw, violaDdyaw, violaCosZ;
            double violaPosPena, violaVelPena, violaAccPena, violaAccZPena, violaJerPena, violaDyawPena, violaDdyawPena, violaCosZPena;
            double violaPosPenaD, violaVelPenaD, violaAccPenaD, violaAccZPenaD, violaJerPenaD, violaDyawPenaD, violaDdyawPenaD, violaCosZPenaD;

            const int pieceNum = T.size();
            // const int coverNum = coverIdx.size();
            const double integralFrac = 1.0 / integralResolution;
            for (int i = 0/*, m = 0*/; i < pieceNum; i++)
            {
                const Eigen::Matrix<double, 6, 4> &c = coeffs.block<6, 4>(i * 6, 0);
                step = T(i) * integralFrac;
                for (int j = 0; j <= integralResolution; j++)
                {
                    s1 = j * step;
                    s2 = s1 * s1;
                    s3 = s2 * s1;
                    s4 = s2 * s2;
                    s5 = s4 * s1;
                    beta0(0) = 1.0, beta0(1) = s1, beta0(2) = s2, beta0(3) = s3, beta0(4) = s4, beta0(5) = s5;
                    beta1(0) = 0.0, beta1(1) = 1.0, beta1(2) = 2.0 * s1, beta1(3) = 3.0 * s2, beta1(4) = 4.0 * s3, beta1(5) = 5.0 * s4;
                    beta2(0) = 0.0, beta2(1) = 0.0, beta2(2) = 2.0, beta2(3) = 6.0 * s1, beta2(4) = 12.0 * s2, beta2(5) = 20.0 * s3;
                    beta3(0) = 0.0, beta3(1) = 0.0, beta3(2) = 0.0, beta3(3) = 6.0, beta3(4) = 24.0 * s1, beta3(5) = 60.0 * s2;
                    beta4(0) = 0.0, beta4(1) = 0.0, beta4(2) = 0.0, beta4(3) = 0.0, beta4(4) = 24.0, beta4(5) = 120.0 * s1;
                    pos = c.transpose() * beta0;
                    vel = c.transpose() * beta1;
                    acc = c.transpose() * beta2;
                    jer = c.transpose() * beta3;
                    sna = c.transpose() * beta4;

                    az = acc.head(3);
                    az(2) += 9.8;
                    z = az.normalized();

                    violaVel = vel.head(3).squaredNorm() - velSqrMax;
                    violaAcc = acc.head(3).squaredNorm() - accSqrMax;
                    violaAccZ = -acc(2) - 9.81 * 0.7;

                    violaJer = jer.head(3).squaredNorm() - jerSqrMax;
                    violaDyaw = vel(3) * vel(3) - dyawMax;
                    violaDdyaw = acc(3) * acc(3) - ddyawMax;
                    violaCosZ = z(2) - zMin;
                    L = hIdx(i);
                    K = hPolys[L].rows();

                    gradPos.setZero(), gradVel.setZero(), gradAcc.setZero(), gradJer.setZero();
                    pena = 0.0;

                    for (int k = 0; k < K; k++)
                    {
                        outerNormal = hPolys[L].block<1, 3>(k, 0);
                        violaPos = outerNormal.dot(pos.head(3)) + hPolys[L](k, 3);
                        if (smoothedL1(violaPos, smoothFactor, violaPosPena, violaPosPenaD))
                        {
                            gradPos.head(3) += weightPos * violaPosPenaD * outerNormal;
                            pena += weightPos * violaPosPena;
                        }
                    }
                    if (smoothedL1(violaVel, smoothFactor, violaVelPena, violaVelPenaD))
                    {
                        gradVel.head(3) += weightVel * violaVelPenaD * 2.0 * vel.head(3);
                        pena += weightVel * violaVelPena;
                    }
                    if (smoothedL1(violaAcc, smoothFactor, violaAccPena, violaAccPenaD))
                    {
                        gradAcc.head(3) += weightAcc * violaAccPenaD * 2.0 * acc.head(3);
                        pena += weightAcc * violaAccPena;
                    }
                    if (smoothedL1(violaAccZ, smoothFactor, violaAccZPena, violaAccZPenaD))
                    {
                        gradAcc(2) -= weightAcc * violaAccZPenaD;
                        pena += weightAcc * violaAccPena;
                    }
                    if (smoothedL1(violaJer, smoothFactor, violaJerPena, violaJerPenaD))
                    {
                        gradJer.head(3) += weightJer * violaJerPenaD * 2.0 * jer.head(3);
                        pena += weightJer * violaJerPena;
                    }

                    if (smoothedL1(violaDyaw, smoothFactor, violaDyawPena, violaDyawPenaD))
                    {
                        gradVel(3) += weightDyaw * violaDyawPenaD * 2.0 * vel(3);
                        pena += weightDyaw * violaDyawPena;
                    }
                    if (smoothedL1(violaDdyaw, smoothFactor, violaDdyawPena, violaDdyawPenaD))
                    {
                        gradAcc(3) += weightDdyaw * violaDdyawPenaD * 2.0 * acc(3);
                        pena += weightDdyaw * violaDdyawPena;
                    }
                    if (smoothedL1(violaCosZ, smoothFactor, violaCosZPena, violaCosZPenaD))
                    {
                        double azsi = 1.0 / az.squaredNorm();
                        gradAcc(0) += az(0) * azsi * z(2) * violaCosZPenaD * weightZ;
                        gradAcc(1) += az(1) * azsi  * z(2) * violaCosZPenaD * weightZ;
                        gradAcc(2) -= (1.0  * az.norm() - az(2)  * azsi  * z(2)) * violaCosZPenaD * weightZ;
                        pena += weightZ * violaCosZPena;
                    }
                    node = (j == 0 || j == integralResolution) ? 0.5 : 1.0;
                    alpha = j * integralFrac;
                    gradC.block<6, 4>(i * 6, 0) += (beta0 * gradPos.transpose() +
                                                    beta1 * gradVel.transpose() +
                                                    beta2 * gradAcc.transpose() +
                                                    beta3 * gradJer.transpose()) *
                                                   node * step;
                    gradT(i) += (gradPos.dot(vel) +
                                 gradVel.dot(acc) +
                                 gradAcc.dot(jer) +
                                 gradJer.dot(sna)) *
                                    alpha * node * step +
                                node * integralFrac * pena;
                    cost += node * step * pena;
                }

                // if(m < pieceNum && i == coverIdx(m)){
                    if(i + 1 >= pieceNum) continue;
                    // if(i >= T.size()){
                    //     std::cout<<"i:"<<i<<" T:"<<T.size()<<std::endl;
                    //     getchar();
                    // }
                    s1 = T(i);
                    s2 = s1 * s1;
                    s3 = s2 * s1;
                    s4 = s2 * s2;
                    s5 = s4 * s1;
                    beta0(0) = 1.0, beta0(1) = s1, beta0(2) = s2, beta0(3) = s3, beta0(4) = s4, beta0(5) = s5;
                    beta1(0) = 0.0, beta1(1) = 1.0, beta1(2) = 2.0 * s1, beta1(3) = 3.0 * s2, beta1(4) = 4.0 * s3, beta1(5) = 5.0 * s4;
                    beta2(0) = 0.0, beta2(1) = 0.0, beta2(2) = 2.0, beta2(3) = 6.0 * s1, beta2(4) = 12.0 * s2, beta2(5) = 20.0 * s3;
                    beta3(0) = 0.0, beta3(1) = 0.0, beta3(2) = 0.0, beta3(3) = 6.0, beta3(4) = 24.0 * s1, beta3(5) = 60.0 * s2;
                    // beta4(0) = 0.0, beta4(1) = 0.0, beta4(2) = 0.0, beta4(3) = 0.0, beta4(4) = 24.0, beta4(5) = 120.0 * s1;
                    pos = c.transpose() * beta0;
                    vel = c.transpose() * beta1;
                    acc = c.transpose() * beta2;
                    jer = c.transpose() * beta3;
                    // M = i;
                    az = acc.head(3);
                    az(2) += 9.8;
                    z = az.normalized();

                    double sqrt_2_1pz2 = sqrt(2*(1 + z(2)));
                    double sqrt_2_1pz2_inv = 1.0 / sqrt_2_1pz2;
                    double yaw2 = pos(3) * 0.5;
                    double siny2 = sin(yaw2);
                    double cosy2 = cos(yaw2);
                    q(0) = (1 + z(2))*cosy2;
                    q(1) = -z(1)*cosy2 + z(0)*siny2;
                    q(2) = z(0)*cosy2 + z(1)*siny2;
                    q(3) = (1 + z(2))*siny2;
                    q *= sqrt_2_1pz2_inv;

                    q_d_z.setZero();
                    q_d_z(0, 1) = siny2 * sqrt_2_1pz2_inv;
                    q_d_z(0, 2) = cosy2 * sqrt_2_1pz2_inv;
                    q_d_z(1, 1) = -cosy2 * sqrt_2_1pz2_inv;
                    q_d_z(1, 2) = siny2 * sqrt_2_1pz2_inv;
                    q_d_z(2, 1) = -q(1) * sqrt_2_1pz2_inv * sqrt_2_1pz2_inv;
                    q_d_z(2, 2) = -q(2) * sqrt_2_1pz2_inv * sqrt_2_1pz2_inv;
                    q_d_z(2, 0) = cosy2 * sqrt_2_1pz2_inv * 0.5;
                    q_d_z(2, 3) = siny2 * sqrt_2_1pz2_inv * 0.5;

                    qxy = q(1) * q(2);
                    qxz = q(1) * q(3);
                    qxw = q(1) * q(0);
                    qyz = q(2) * q(3);
                    qyw = q(2) * q(0);
                    qzw = q(3) * q(0);
                    qxx = q(1) * q(1);
                    qyy = q(2) * q(2);
                    qzz = q(3) * q(3);

                    W2C <<  1-2*(qyy+qzz), 2*(qxy + qzw), 2*(qxz - qyw),
                            2*(qxy - qzw), 1-2*(qxx+qzz), 2*(qyz + qxw),
                            2*(qxz + qyw), 2*(qyz - qxw), 1-2*(qxx+qyy);

                    double cosy2_d_y = -siny2*0.5;
                    double siny2_d_y = cosy2*0.5;
                    y_d_q(0) = (1 + z(2)) * cosy2_d_y;
                    y_d_q(1) = -z(1)*cosy2_d_y + z(0)*siny2_d_y;
                    y_d_q(2) = z(0)*cosy2_d_y + z(1)*siny2_d_y;
                    y_d_q(3) = (1 + z(2))*siny2_d_y;
                    y_d_q *= sqrt_2_1pz2_inv;

                    double anorm = az.norm(), anorm3 = anorm * anorm * anorm, anorm_inv = 1.0 / anorm, anorm3_inv = 1.0 / anorm3;
                    double m11 =anorm_inv - az(0)*az(0)*anorm3_inv, m22 = anorm_inv - az(1)*az(1)*anorm3_inv, m33 = anorm_inv - az(2)*az(2)*anorm3_inv,
                        m12 = -az(0)*az(1)*anorm3_inv, m13 = -az(0)*az(2)*anorm3_inv, m23 = -az(1)*az(2)*anorm3_inv;
                    z_d_a << m11, m12, m13,
                            m12, m22, m23, 
                            m13, m23, m33;   
                    // if(i >= coverTargets.size()){
                    //     std::cout<<"i:"<<i<<" coverTargets:"<<coverTargets.size()<<std::endl;
                    //     getchar();
                    // }
                    cn = coverTargets[i].cols();
                    pena = 0;
                    double pen, len, len_inv;
                    if(cn > 0) pen = weightCover;
                    bool fail_cover;

                    gradA.setZero();
                    gradP.setZero();
                    for(int j = 0; j < cn; j++){
                        fail_cover = false;
                        dps = coverTargets[i].col(j) - pos.head(3);
                        len = std::max(dps.norm(), 1.0) * 0.2;
                        len_inv = 1.0 / len;
                        pc = W2C * (coverTargets[i].col(j) - pos.head(3));
                        int f = cameraFov.rows();
                        gradPc.setZero();
                        for(int n = 0; n < f; n++){
                            outerNormal = cameraFov.block<1, 3>(n, 0);
                            violaPc = outerNormal.dot(pc.head(3)) + cameraFov(n, 3);
                            if (smoothedL1(violaPc, smoothFactor, violaPcPena, violaPcPenaD))
                            {
                                fail_cover = true;
                                gradPc += pen * violaPcPenaD * outerNormal * len_inv;
                                pena += pen * violaPcPena * len_inv;
                            }
                        }

                        if(!fail_cover) continue;

                        Pc_d_q <<   2*(q(3)*dps(1) - q(2)*dps(2))             , 2*(-q(3)*dps(0) + q(1)*dps(2))               , 2*(q(2)*dps(0)-q(1)*dps(1)),
                                    2*(q(2)*dps(1) + q(3)*dps(2))             , 2*(q(2)*dps(0) - 2*q(1)*dps(1) + q(0)*dps(2)), 2*(q(3)*dps(0)-q(0)*dps(1)-2*q(1)*dps(2)),
                                    2*(-2*q(2)*dps(0)+q(1)*dps(1)-q(0)*dps(2)), 2*(q(1)*dps(0) + q(3)*dps(2))                , 2*(q(0)*dps(0)+q(3)*dps(1)-2*q(2)*dps(2)),
                                    2*(-2*q(3)*dps(0)+q(0)*dps(1)+q(1)*dps(2)), 2*(-q(0)*dps(0) -2*q(3)*dps(1) + q(2)*dps(2)), 2*(q(1)*dps(0)+q(2)*dps(1));
                        gradQ = Pc_d_q * gradPc;
                        gradZ = q_d_z * gradQ;

                        gradYaw = gradQ.transpose() * y_d_q;

                        gradPosCov = -W2C.transpose() * gradPc; // checked
                        gradP.head(3) += gradPosCov;
                        gradP(3) += gradYaw;

                        gradA.head(3) += z_d_a * gradZ;
                    }

                    gradC.block<6, 4>(i * 6, 0) += (beta0 * gradP.transpose() +
                                    beta2 * gradA.transpose());
                    gradT(i) += gradP.dot(vel) + gradA.dot(jer);
                    cost += pena;
                    // m++;
                // }
            }
            return;
        }


        // magnitudeBounds = [v_max, omg_max, theta_max, thrust_min, thrust_max]^T
        // penaltyWeights = [pos_weight, vel_weight, omg_weight, theta_weight, thrust_weight]^T
        // physicalParams = [vehicle_mass, gravitational_acceleration, horitonral_drag_coeff,
        //                   vertical_drag_coeff, parasitic_drag_coeff, speed_smooth_factor]^T
        // static inline void attachPenaltyFunctional(const Eigen::VectorXd &T,
        //                                            const Eigen::MatrixX3d &coeffs,
        //                                            const Eigen::VectorXi &hIdx,
        //                                            const PolyhedraH &hPolys,
        //                                            const double &smoothFactor,
        //                                            const int &integralResolution,
        //                                            const Eigen::VectorXd &magnitudeBounds,
        //                                            const Eigen::VectorXd &penaltyWeights,
        //                                            flatness::FlatnessMap &flatMap,
        //                                            double &cost,
        //                                            Eigen::VectorXd &gradT,
        //                                            Eigen::MatrixX3d &gradC)
        // {
        //     const double velSqrMax = magnitudeBounds(0) * magnitudeBounds(0);
        //     const double omgSqrMax = magnitudeBounds(1) * magnitudeBounds(1);
        //     const double thetaMax = magnitudeBounds(2);
        //     const double thrustMean = 0.5 * (magnitudeBounds(3) + magnitudeBounds(4));
        //     const double thrustRadi = 0.5 * fabs(magnitudeBounds(4) - magnitudeBounds(3));
        //     const double thrustSqrRadi = thrustRadi * thrustRadi;

        //     const double weightPos = penaltyWeights(0);
        //     const double weightVel = penaltyWeights(1);
        //     const double weightOmg = penaltyWeights(2);
        //     const double weightTheta = penaltyWeights(3);
        //     const double weightThrust = penaltyWeights(4);

        //     Eigen::Vector3d pos, vel, acc, jer, sna;
        //     Eigen::Vector3d totalGradPos, totalGradVel, totalGradAcc, totalGradJer;
        //     double totalGradPsi, totalGradPsiD;
        //     double thr, cos_theta;
        //     Eigen::Vector4d quat;
        //     Eigen::Vector3d omg;
        //     double gradThr;
        //     Eigen::Vector4d gradQuat;
        //     Eigen::Vector3d gradPos, gradVel, gradOmg;

        //     double step, alpha;
        //     double s1, s2, s3, s4, s5;
        //     Eigen::Matrix<double, 6, 1> beta0, beta1, beta2, beta3, beta4;
        //     Eigen::Vector3d outerNormal;
        //     int K, L;
        //     double violaPos, violaVel, violaOmg, violaTheta, violaThrust;
        //     double violaPosPenaD, violaVelPenaD, violaOmgPenaD, violaThetaPenaD, violaThrustPenaD;
        //     double violaPosPena, violaVelPena, violaOmgPena, violaThetaPena, violaThrustPena;
        //     double node, pena;

        //     const int pieceNum = T.size();
        //     const double integralFrac = 1.0 / integralResolution;
        //     for (int i = 0; i < pieceNum; i++)
        //     {
        //         const Eigen::Matrix<double, 6, 3> &c = coeffs.block<6, 3>(i * 6, 0);
        //         step = T(i) * integralFrac;
        //         for (int j = 0; j <= integralResolution; j++)
        //         {
        //             s1 = j * step;
        //             s2 = s1 * s1;
        //             s3 = s2 * s1;
        //             s4 = s2 * s2;
        //             s5 = s4 * s1;
        //             beta0(0) = 1.0, beta0(1) = s1, beta0(2) = s2, beta0(3) = s3, beta0(4) = s4, beta0(5) = s5;
        //             beta1(0) = 0.0, beta1(1) = 1.0, beta1(2) = 2.0 * s1, beta1(3) = 3.0 * s2, beta1(4) = 4.0 * s3, beta1(5) = 5.0 * s4;
        //             beta2(0) = 0.0, beta2(1) = 0.0, beta2(2) = 2.0, beta2(3) = 6.0 * s1, beta2(4) = 12.0 * s2, beta2(5) = 20.0 * s3;
        //             beta3(0) = 0.0, beta3(1) = 0.0, beta3(2) = 0.0, beta3(3) = 6.0, beta3(4) = 24.0 * s1, beta3(5) = 60.0 * s2;
        //             beta4(0) = 0.0, beta4(1) = 0.0, beta4(2) = 0.0, beta4(3) = 0.0, beta4(4) = 24.0, beta4(5) = 120.0 * s1;
        //             pos = c.transpose() * beta0;
        //             vel = c.transpose() * beta1;
        //             acc = c.transpose() * beta2;
        //             jer = c.transpose() * beta3;
        //             sna = c.transpose() * beta4;

        //             flatMap.forward(vel, acc, jer, 0.0, 0.0, thr, quat, omg);

        //             violaVel = vel.squaredNorm() - velSqrMax;
        //             violaOmg = omg.squaredNorm() - omgSqrMax;
        //             cos_theta = 1.0 - 2.0 * (quat(1) * quat(1) + quat(2) * quat(2));
        //             violaTheta = acos(cos_theta) - thetaMax;
        //             violaThrust = (thr - thrustMean) * (thr - thrustMean) - thrustSqrRadi;

        //             gradThr = 0.0;
        //             gradQuat.setZero();
        //             gradPos.setZero(), gradVel.setZero(), gradOmg.setZero();
        //             pena = 0.0;

        //             L = hIdx(i);
        //             K = hPolys[L].rows();
        //             for (int k = 0; k < K; k++)
        //             {
        //                 outerNormal = hPolys[L].block<1, 3>(k, 0);
        //                 violaPos = outerNormal.dot(pos) + hPolys[L](k, 3);
        //                 if (smoothedL1(violaPos, smoothFactor, violaPosPena, violaPosPenaD))
        //                 {
        //                     gradPos += weightPos * violaPosPenaD * outerNormal;
        //                     pena += weightPos * violaPosPena;
        //                 }
        //             }

        //             if (smoothedL1(violaVel, smoothFactor, violaVelPena, violaVelPenaD))
        //             {
        //                 gradVel += weightVel * violaVelPenaD * 2.0 * vel;
        //                 pena += weightVel * violaVelPena;
        //             }

        //             if (smoothedL1(violaOmg, smoothFactor, violaOmgPena, violaOmgPenaD))
        //             {
        //                 gradOmg += weightOmg * violaOmgPenaD * 2.0 * omg;
        //                 pena += weightOmg * violaOmgPena;
        //             }

        //             if (smoothedL1(violaTheta, smoothFactor, violaThetaPena, violaThetaPenaD))
        //             {
        //                 gradQuat += weightTheta * violaThetaPenaD /
        //                             sqrt(1.0 - cos_theta * cos_theta) * 4.0 *
        //                             Eigen::Vector4d(0.0, quat(1), quat(2), 0.0);
        //                 pena += weightTheta * violaThetaPena;
        //             }

        //             if (smoothedL1(violaThrust, smoothFactor, violaThrustPena, violaThrustPenaD))
        //             {
        //                 gradThr += weightThrust * violaThrustPenaD * 2.0 * (thr - thrustMean);
        //                 pena += weightThrust * violaThrustPena;
        //             }

        //             flatMap.backward(gradPos, gradVel, gradThr, gradQuat, gradOmg,
        //                              totalGradPos, totalGradVel, totalGradAcc, totalGradJer,
        //                              totalGradPsi, totalGradPsiD);

        //             node = (j == 0 || j == integralResolution) ? 0.5 : 1.0;
        //             alpha = j * integralFrac;
        //             gradC.block<6, 3>(i * 6, 0) += (beta0 * totalGradPos.transpose() +
        //                                             beta1 * totalGradVel.transpose() +
        //                                             beta2 * totalGradAcc.transpose() +
        //                                             beta3 * totalGradJer.transpose()) *
        //                                            node * step;
        //             gradT(i) += (totalGradPos.dot(vel) +
        //                          totalGradVel.dot(acc) +
        //                          totalGradAcc.dot(jer) +
        //                          totalGradJer.dot(sna)) *
        //                             alpha * node * step +
        //                         node * integralFrac * pena;
        //             cost += node * step * pena;
        //         }
        //     }

        //     return;
        // }

        /**
         * @brief interface of BFGS, optimize MINCO
         * 
         * @param ptr 
         * @param x 
         * @param g 
         * @return objective cost
         */
        static inline double costFunctional(void *ptr,
                                            const Eigen::VectorXd &x,
                                            Eigen::VectorXd &g)
        {
            GCOPTER_COVER_PolytopeSFC &obj = *(GCOPTER_COVER_PolytopeSFC *)ptr;
            const int dimTau = obj.temporalDim;
            const int dimXi = obj.spatialDim;
            const int dimEvi = obj.endVelDim;
            const int dimYi = obj.yawDim;

            const double weightT = obj.rho;
            // const double endyaw = obj.tailPVA(3, 0);
            // const double weightminT = obj.phi;
            // double fminT, dfminT;
            Eigen::Map<const Eigen::VectorXd> tau(x.data(), dimTau);
            Eigen::Map<const Eigen::VectorXd> xi(x.data() + dimTau, dimXi);
            Eigen::Map<const Eigen::VectorXd> evi(x.data() + dimTau + dimXi, dimEvi);
            Eigen::Map<const Eigen::VectorXd> yi(x.data() + dimTau + dimXi + dimEvi, dimYi);
            Eigen::Map<const Eigen::VectorXd> edyi(x.data() + dimTau + dimXi + dimEvi + dimYi, 2);

            Eigen::Map<Eigen::VectorXd> gradTau(g.data(), dimTau);
            Eigen::Map<Eigen::VectorXd> gradXi(g.data() + dimTau, dimXi);
            Eigen::Map<Eigen::VectorXd> gradEvi(g.data() + dimTau + dimXi, dimEvi);
            Eigen::Map<Eigen::VectorXd> gradYi(g.data() + dimTau + dimXi + dimEvi, dimYi);
            Eigen::Map<Eigen::VectorXd> gradEdyi(g.data() + dimTau + dimXi + dimEvi + dimYi, 2);

            Eigen::Vector3d endv;
            double dye;
            forwardV(obj.vEndVel, evi, obj.EndDy, edyi, endv, dye);
            forwardT(tau, obj.times);
            forwardP(xi, obj.vPolyIdx, obj.vPolytopes, obj.yawRange, yi, /*obj.fixYpIdx,*/ obj.points);
            // std::cout<<"obj.points1:"<<obj.points<<std::endl;
            // std::cout<<"endv:"<<endv.transpose()<<std::endl;
            // std::cout<<"obj.times:"<<obj.times.transpose()<<std::endl;

            double cost = 0;
            double cep = 0, cey = 0;
            Eigen::MatrixX3d gp;
            Eigen::VectorXd gy, gt;
            
            obj.minco.setEndVel(endv);
            obj.minco.setEndDy(dye);
            obj.minco.setParameters(obj.points, obj.times);
            // obj.minco.getEnergy(cost);
            // std::cout<<"cost:"<<cost<<std::endl;
            obj.minco.getEnergyPos(cep);
            obj.minco.getEnergyYaw(cey);
            obj.minco.getEnergyPartialGradByCoeffsPos(gp);
            obj.minco.getEnergyPartialGradByCoeffsYaw(gy);
            gt.resize(dimTau);
            // gt.setZero();
            obj.minco.getEnergyPosPartialGradByTimes(gt);
            obj.partialGradByTimes = gt * 0.3;
            obj.minco.getEnergyPosPartialGradByTimes(gt);
            obj.partialGradByTimes += gt * 0.00;
            obj.partialGradByCoeffs.leftCols(3) = gp * 0.3;
            obj.partialGradByCoeffs.col(3) = gy * 0.00;
            cost = cep * 0.3 + cey * 0.00;

            // obj.minco.getEnergyPartialGradByCoeffs(obj.partialGradByCoeffs);
            // obj.minco.getEnergyPartialGradByTimes(obj.partialGradByTimes);
            // cost *= 0.4;
            // obj.partialGradByCoeffs *= 0.4;
            // obj.partialGradByTimes *= 0.4;
            // std::cout<<"obj.partialGradByCoeffs0:"<<obj.partialGradByCoeffs.transpose()<<std::endl;
            // std::cout<<"obj.partialGradByTimes0:"<<obj.partialGradByTimes.transpose()<<std::endl;


            attachPenaltyFunctional(obj.times, obj.minco.getCoeffs(),
                                    obj.hPolyIdx, obj.hPolytopes,
                                    obj.smoothEps, obj.integralRes,
                                    obj.magnitudeBd, obj.penaltyWt,
                                    /*obj.fixYpIdx,*/ obj.cameraFOV, obj.targets,
                                    cost, obj.partialGradByTimes, obj.partialGradByCoeffs);
            // std::cout<<"obj.partialGradByCoeffs1:"<<obj.partialGradByCoeffs.transpose()<<std::endl;
            // std::cout<<"obj.partialGradByTimes1:"<<obj.partialGradByTimes.transpose()<<std::endl;
            // obj.minco.propogateGrad(obj.partialGradByCoeffs, obj.partialGradByTimes,
            //                         obj.gradByPoints, obj.gradByTimes);
            obj.minco.propogateGrad(obj.partialGradByCoeffs, obj.partialGradByTimes,
                                    obj.gradByPoints, obj.gradByEndVel, obj.gradByTimes);
            // std::cout<<"obj.gradByTimes:"<<obj.gradByTimes.transpose()<<std::endl;
            // std::cout<<"obj.gradByPoints:"<<obj.gradByPoints.transpose()<<std::endl;
            // std::cout<<"obj.gradByEndVel:"<<obj.gradByEndVel.transpose()<<std::endl;
            // double weiY = obj.penaltyWt(6);
            // Eigen::VectorXd Yc, Yc2;
            // Yc = obj.points.row(3).array() - endyaw;
            // Yc2 = Yc.array().square();
            // cost += Yc2.sum() * weiY;
            // obj.gradByPoints.row(3) += Yc * 2 * weiY;

            cost += weightT * obj.times.sum();
            obj.gradByTimes.array() += weightT;

            backwardGradT(tau, obj.gradByTimes, gradTau);
            // backwardGradP(xi, obj.vPolyIdx, obj.vPolytopes, obj.gradByPoints, gradXi);
            backwardGradP(xi, obj.vPolyIdx, obj.vPolytopes, yi, obj.yawRange, obj.gradByPoints, /*obj.fixYpIdx,*/ gradXi, gradYi);
            // backwardGradV(evi, obj.vEndVel, obj.gradByEndVel, gradEvi);
            backwardGradV(obj.gradByEndVel, evi, obj.vEndVel, edyi, obj.EndDy, gradEvi, gradEdyi);

            // normRetrictionLayer(xi, obj.vPolyIdx, obj.vPolytopes, cost, gradXi);
            normRetrictionLayer(xi, obj.vPolyIdx, obj.vPolytopes, yi, /*obj.fixYpIdx, */ cost, gradXi, gradYi);
            // normRetrictionLayerV(evi, cost, gradEvi);
            normRetrictionLayerV(evi, edyi, cost, gradEvi, gradEdyi);

            return cost;
        }

        /**
         * @brief interface of BFGS, shortten the path
         * 
         * @param ptr 
         * @param xi 
         * @param gradXi 
         * @return objective cost 
         */
        static inline double costDistance(void *ptr,
                                          const Eigen::VectorXd &xi,
                                          Eigen::VectorXd &gradXi)
        {
            void **dataPtrs = (void **)ptr;
            const double &dEps = *((const double *)(dataPtrs[0]));
            const Eigen::Vector3d &ini = *((const Eigen::Vector3d *)(dataPtrs[1]));
            const Eigen::Vector3d &fin = *((const Eigen::Vector3d *)(dataPtrs[2]));
            const PolyhedraV &vPolys = *((PolyhedraV *)(dataPtrs[3]));

            double cost = 0.0;
            const int overlaps = vPolys.size() / 2;

            Eigen::Matrix3Xd gradP = Eigen::Matrix3Xd::Zero(3, overlaps);
            Eigen::Vector3d a, b, d;
            Eigen::VectorXd r;
            double smoothedDistance;
            for (int i = 0, j = 0, k = 0; i <= overlaps; i++, j += k)
            {
                a = i == 0 ? ini : b;
                if (i < overlaps)
                {
                    k = vPolys[2 * i + 1].cols();
                    Eigen::Map<const Eigen::VectorXd> q(xi.data() + j, k);
                    r = q.normalized().head(k - 1);
                    b = vPolys[2 * i + 1].rightCols(k - 1) * r.cwiseProduct(r) +
                        vPolys[2 * i + 1].col(0);
                }
                else
                {
                    b = fin;
                }

                d = b - a;
                smoothedDistance = sqrt(d.squaredNorm() + dEps);
                cost += smoothedDistance;

                if (i < overlaps)
                {
                    gradP.col(i) += d / smoothedDistance;
                }
                if (i > 0)
                {
                    gradP.col(i - 1) -= d / smoothedDistance;
                }
            }

            Eigen::VectorXd unitQ;
            double sqrNormQ, invNormQ, sqrNormViolation, c, dc;
            for (int i = 0, j = 0, k; i < overlaps; i++, j += k)
            {
                k = vPolys[2 * i + 1].cols();
                Eigen::Map<const Eigen::VectorXd> q(xi.data() + j, k);
                Eigen::Map<Eigen::VectorXd> gradQ(gradXi.data() + j, k);
                sqrNormQ = q.squaredNorm();
                invNormQ = 1.0 / sqrt(sqrNormQ);
                unitQ = q * invNormQ;
                gradQ.head(k - 1) = (vPolys[2 * i + 1].rightCols(k - 1).transpose() * gradP.col(i)).array() *
                                    unitQ.head(k - 1).array() * 2.0;
                gradQ(k - 1) = 0.0;


                gradQ = (gradQ - unitQ * unitQ.dot(gradQ)).eval() * invNormQ;

                sqrNormViolation = sqrNormQ - 1.0;
                if (sqrNormViolation > 0.0)
                {
                    c = sqrNormViolation * sqrNormViolation;
                    dc = 3.0 * c;
                    c *= sqrNormViolation;
                    cost += c;
                    gradQ += dc * 2.0 * q;
                }
            }

            return cost;
        }

        static inline void YawNorm(double &yaw){
            double yawn;
            int c = yaw / M_PI / 2;
            yawn = yaw - c * M_PI * 2;
            
            if(yawn < -M_PI) yawn += M_PI * 2;
            if(yawn > M_PI) yawn -= M_PI * 2;
            yaw = yawn;
            return;
        }

        static inline double YawDiff(const double &yaw1, const double &yaw2){
            double dy = yaw1 - yaw2;
            YawNorm(dy);
            return dy;
        }

        /**
         * @brief shortten the path
         * 
         * @param ini 
         * @param fin 
         * @param vPolys 
         * @param smoothD 
         * @param path 
         */
        static inline void getShortestPath(const Eigen::Vector3d &ini,
                                           const Eigen::Vector3d &fin,
                                           const PolyhedraV &vPolys,
                                           const double &smoothD,
                                           Eigen::Matrix3Xd &path)
        {
            const int overlaps = vPolys.size() / 2;
            Eigen::VectorXi vSizes(overlaps);
            for (int i = 0; i < overlaps; i++)
            {
                vSizes(i) = vPolys[2 * i + 1].cols();
            }
            Eigen::VectorXd xi(vSizes.sum());
            for (int i = 0, j = 0; i < overlaps; i++)
            {
                xi.segment(j, vSizes(i)).setConstant(sqrt(1.0 / vSizes(i)));
                j += vSizes(i);
            }

            double minDistance;
            void *dataPtrs[4];
            dataPtrs[0] = (void *)(&smoothD);
            dataPtrs[1] = (void *)(&ini);
            dataPtrs[2] = (void *)(&fin);
            dataPtrs[3] = (void *)(&vPolys);
            lbfgs::lbfgs_parameter_t shortest_path_params;
            shortest_path_params.past = 3;
            shortest_path_params.delta = 1.0e-3;
            shortest_path_params.g_epsilon = 1.0e-5;

            lbfgs::lbfgs_optimize(xi,
                                  minDistance,
                                  &GCOPTER_COVER_PolytopeSFC::costDistance,
                                  nullptr,
                                  nullptr,
                                  dataPtrs,
                                  shortest_path_params);

            path.resize(3, overlaps + 2);
            path.leftCols<1>() = ini;
            path.rightCols<1>() = fin;
            Eigen::VectorXd r;
            for (int i = 0, j = 0, k; i < overlaps; i++, j += k)
            {
                k = vPolys[2 * i + 1].cols();
                Eigen::Map<const Eigen::VectorXd> q(xi.data() + j, k);
                r = q.normalized().head(k - 1);
                path.col(i + 1) = vPolys[2 * i + 1].rightCols(k - 1) * r.cwiseProduct(r) +
                                  vPolys[2 * i + 1].col(0);
            }

            return;
        }

        /**
         * @brief get origin and vectors of each corridor. 
         * for quick hull corridors, not used here.
         * 
         * @param hPs ieqs of polytopes
         * @param vPs corridori: [origin, dir1, dir2....]
         * @return true 
         * @return false 
         */
        static inline bool processCorridor(const PolyhedraH &hPs,
                                           PolyhedraV &vPs)
        {
            const int sizeCorridor = hPs.size() - 1;

            vPs.clear();
            vPs.reserve(2 * sizeCorridor + 1);

            int nv;
            PolyhedronH curIH;
            PolyhedronV curIV, curIOB;
            for (int i = 0; i < sizeCorridor; i++)
            {
                if (!geo_utils::enumerateVs(hPs[i], curIV))
                {
                    return false;
                }
                nv = curIV.cols();
                curIOB.resize(3, nv);
                curIOB.col(0) = curIV.col(0);
                curIOB.rightCols(nv - 1) = curIV.rightCols(nv - 1).colwise() - curIV.col(0);
                vPs.push_back(curIOB);

                curIH.resize(hPs[i].rows() + hPs[i + 1].rows(), 4);
                curIH.topRows(hPs[i].rows()) = hPs[i];
                curIH.bottomRows(hPs[i + 1].rows()) = hPs[i + 1];
                if (!geo_utils::enumerateVs(curIH, curIV))
                {
                    return false;
                }
                nv = curIV.cols();
                curIOB.resize(3, nv);
                curIOB.col(0) = curIV.col(0);
                curIOB.rightCols(nv - 1) = curIV.rightCols(nv - 1).colwise() - curIV.col(0);
                vPs.push_back(curIOB);
            }

            if (!geo_utils::enumerateVs(hPs.back(), curIV))
            {
                return false;
            }
            nv = curIV.cols();
            curIOB.resize(3, nv);
            curIOB.col(0) = curIV.col(0);
            curIOB.rightCols(nv - 1) = curIV.rightCols(nv - 1).colwise() - curIV.col(0);
            vPs.push_back(curIOB);

            return true;
        }

        /**
         * @brief set the initial params 
         * 
         * @param path          initial path
         * @param speed         for init T
         * @param intervalNs    index of corresponding polytops
         * @param innerPoints   
         * @param timeAlloc 
         */
        static inline void setInitial(const Eigen::Matrix3Xd &path,
                                      const double &speed,
                                      const Eigen::VectorXd yawPath,
                                      const double &yawSpeed,
                                      const Eigen::VectorXi &intervalNs,
                                      Eigen::Matrix4Xd &innerPoints,
                                      Eigen::VectorXd &timeAlloc)
        {
            const int sizeM = intervalNs.size();
            const int sizeN = intervalNs.sum();
            innerPoints.resize(4, sizeN - 1);
            timeAlloc.resize(sizeN);

            Eigen::Vector4d a, b, c;
            for (int i = 0, j = 0, k = 0, l; i < sizeM; i++)
            {
                l = intervalNs(i);
                a(3) = yawPath(i);
                b(3) = yawPath(i + 1);
                a.head(3) = path.col(i);
                b.head(3) = path.col(i + 1);
                c = (b - a) / l;
                // timeAlloc.segment(j, l).setConstant(c.norm() / speed);
                timeAlloc.segment(j, l).setConstant(std::max(c.head(3).norm() / speed, abs(c(3)) / yawSpeed));
                j += l;
                for (int m = 0; m < l; m++)
                {
                    if (i > 0 || m > 0)
                    {
                        innerPoints.col(k++) = a + c * m;
                    }
                }
            }
        }

    inline bool TrajFeaCheck(const Eigen::VectorXd &T,
                            const Eigen::MatrixX4d &coeffs,
                            const Eigen::VectorXi &hIdx,
                            const PolyhedraH &hPolys,
                            const double &smoothFactor,
                            const int &integralResolution,
                            const Eigen::VectorXd &magnitudeBounds){
        const double velSqrMax = (magnitudeBounds(0)) * (magnitudeBounds(0)) * 1.69;
        const double accSqrMax = (magnitudeBounds(1)) * (magnitudeBounds(1)) * 2.16;
        // const double jerSqrMax = magnitudeBounds(2) * magnitudeBounds(2);
        const double dyawMax = (magnitudeBounds(3)) * (magnitudeBounds(3)) * 1.69;
        const double ddyawMax =(magnitudeBounds(4)) * (magnitudeBounds(4)) * 2.16;

        Eigen::Vector4d pos, vel, acc, jer, sna;
        double s1, s2, s3, s4, s5;
        Eigen::Matrix<double, 6, 1> beta0, beta1, beta2, beta3, beta4;
        double violaPos, violaVel, violaAcc, violaDyaw, violaDdyaw;
        int K, L;
        Eigen::Vector3d outerNormal;

        const int pieceNum = T.size();
        double step; //alpha;
        const double integralFrac = 1.0 / integralResolution;
        for (int i = 1; i < pieceNum; i++)
            {
                const Eigen::Matrix<double, 6, 4> &c = coeffs.block<6, 4>(i * 6, 0);
                step = T(i) * integralFrac;
                for (int j = 0; j <= integralResolution; j++)
                {
                    s1 = j * step;
                    s2 = s1 * s1;
                    s3 = s2 * s1;
                    s4 = s2 * s2;
                    s5 = s4 * s1;
                    beta0(0) = 1.0, beta0(1) = s1, beta0(2) = s2, beta0(3) = s3, beta0(4) = s4, beta0(5) = s5;
                    beta1(0) = 0.0, beta1(1) = 1.0, beta1(2) = 2.0 * s1, beta1(3) = 3.0 * s2, beta1(4) = 4.0 * s3, beta1(5) = 5.0 * s4;
                    beta2(0) = 0.0, beta2(1) = 0.0, beta2(2) = 2.0, beta2(3) = 6.0 * s1, beta2(4) = 12.0 * s2, beta2(5) = 20.0 * s3;
                    beta3(0) = 0.0, beta3(1) = 0.0, beta3(2) = 0.0, beta3(3) = 6.0, beta3(4) = 24.0 * s1, beta3(5) = 60.0 * s2;
                    beta4(0) = 0.0, beta4(1) = 0.0, beta4(2) = 0.0, beta4(3) = 0.0, beta4(4) = 24.0, beta4(5) = 120.0 * s1;
                    pos = c.transpose() * beta0;
                    vel = c.transpose() * beta1;
                    acc = c.transpose() * beta2;
                    jer = c.transpose() * beta3;
                    sna = c.transpose() * beta4;

                    violaVel = vel.head(3).squaredNorm() - velSqrMax;
                    violaAcc = acc.head(3).squaredNorm() - accSqrMax;
                    violaDyaw = vel(3) * vel(3) - dyawMax;
                    violaDdyaw = acc(3) * acc(3) - ddyawMax;
                    L = hIdx(i);
                    K = hPolys[L].rows();

                    for (int k = 0; k < K; k++)
                    {
                        outerNormal = hPolys[L].block<1, 3>(k, 0);
                        violaPos = outerNormal.dot(pos.head(3)) + hPolys[L](k, 3);
                        if(violaPos > smoothFactor * 2){
                            std::cout<<"violaPos2:"<<violaPos<<std::endl;
                            return false;
                        }
                    }
                    if(violaVel > 0) {
                        std::cout<<"violaVel2:"<<violaVel<<std::endl;
                        return false;
                    }
                    if(violaAcc > 0) {
                        std::cout<<"violaAcc2:"<<violaAcc<<std::endl;
                        return false;
                    }
                    if(violaDyaw > 0) {
                        std::cout<<"violaDyaw2:"<<violaDyaw<<std::endl;
                        return false;
                    }
                    if(violaDdyaw > 0) {
                        std::cout<<"violaDdyaw2:"<<violaDdyaw<<std::endl;
                        return false;
                    }
                }
            }
            return true;
    }
    public:

        /**
         * @brief set path, corridors and optimization params
         * 
         */
        inline bool setup(const double &timeWeight,
                        //   const double &mintimeWeight,
                        //   const double &mintime,
                          const bool &useTerminalCorridor, 
                          const bool &useCorridorDir, 
                          const PolyhedronH &velCorridor,
                          const Eigen::Matrix<double, 4, 3> &initialPVA,
                          const Eigen::Matrix<double, 4, 3> &terminalPVA,
                          const PolyhedraH &safeCorridor,
                          const PolyhedraV &CorridorV,
                          const double &lengthPerPiece,
                          const double &smoothingFactor,
                          const int &integralResolution,
                          const Eigen::VectorXd &magnitudeBounds,
                          const Eigen::VectorXd &penaltyWeights,
                          const double &t_total,
                        //   const std::vector<std::pair<Eigen::Vector4d, int>> &midYPs,
                        //   const Eigen::VectorXd &midYts,
                          const std::vector<Eigen::Matrix3Xd> &coverTargets,
                          const Eigen::MatrixX4d &camerafov,
                          const std::vector<std::pair<Eigen::Vector4d, double>> &initPTs,
                          Eigen::VectorXi &hCorridorIdx,
                          Eigen::VectorXi &vCorridorIdx)
                        //   const Eigen::VectorXd &physicalParams)
        {
            // std::cout<<"set0"<<std::endl;
            rho = timeWeight * 1.05;
            // phi = mintimeWeight;
            // minT = mintime;
            targets = coverTargets;
            cameraFOV = camerafov;

            headPVA = initialPVA;
            tailPVA = terminalPVA;
            double dy = YawDiff(terminalPVA(3, 0), initPTs.back().first(3));
            tailPVA(3, 0) = initPTs.back().first(3) + dy;

            hPolytopes = safeCorridor;
            for (size_t i = 0; i < hPolytopes.size(); i++)
            {
                const Eigen::ArrayXd norms =
                    hPolytopes[i].leftCols<3>().rowwise().norm();
                hPolytopes[i].array().colwise() /= norms;
            }
            vPolytopes = CorridorV;

            polyN = hPolytopes.size();
            smoothEps = smoothingFactor;
            integralRes = integralResolution;
            magnitudeBd = magnitudeBounds;
            penaltyWt = penaltyWeights;

            int init_num = initPTs.size();
            pieceN = init_num + 1;
            // pieceN = init_num + midYPs.size() + 1;
            temporalDim = pieceN;
            yawDim = (pieceN - 1) * 2;
            spatialDim = 0;
            // std::cout<<"set3"<<std::endl;
            /* init mid yaw */
            // Eigen::VectorXi YpInsertIdx;
            // Eigen::VectorXd Tlengths, Ts;
            // Ts.resize(midYPs.size() + 2);
            // Tlengths.resize(midYPs.size() + 1);
            // Ts(0) = 0.0;
            // Ts(midYPs.size() + 1) = t_total;
            // Ts.segment(1, midYPs.size()) = midYts;
            // std::cout<<"set3.1"<<std::endl;
            // Tlengths = Ts.bottomRows(midYPs.size() + 1) - Ts.topRows(midYPs.size() + 1);

            // YpInsertIdx.resize(midYPs.size());
            // fixYpIdx.resize(midYPs.size());

            // for(int i = 0; i < midYts.size(); i++){
            //     for(int j = 0; j < initPTs.size() + 1; j++){
            //         // if(j >= Ts.size() || j + 1 >= Ts.size()){
            //         //     std::cout<<"j:"<<j<<std::endl;
            //         //     std::cout<<"Ts:"<<Ts.size()<<std::endl;
            //         // }
            //         if(j == initPTs.size()){
            //             YpInsertIdx(i) = i + j;
            //             fixYpIdx(i) = i + j;
            //             break;
            //         }
            //         else{
            //             if(initPTs[j].second > midYts(i)){
            //                 YpInsertIdx(i) = i + j;
            //                 fixYpIdx(i) = i + j;
            //                 break;
            //             }
            //         }
            //     }
            // }
            // std::cout<<"YpInsertIdx:"<<YpInsertIdx.transpose()<<std::endl;
            
            vPolyIdx.resize(pieceN - 1);
            yawRange.resize(pieceN - 1);
            hPolyIdx.resize(pieceN);

            points.resize(4, pieceN - 1);
            times.resize(pieceN);
            double last_t = 0;// last_yt = 0;
            double last_yaw = initialPVA(3, 0);
            // double dyaw = YawDiff(initPTs[0].first(3), last_yaw);

            // for(auto &c : hPolytopes){
            //     std::cout<<"corridors:"<<std::endl;
            //     std::cout<<c.transpose()<<std::endl;
            // }
            for (int i = 0; i + 1 < pieceN; i++){
                // if(j < YpInsertIdx.size() && i == YpInsertIdx(j)){
                //     // std::cout<<"set4.2"<<std::endl;
                //     points.col(i) = midYPs[j].first;
                //     // std::cout<<"fix pt i:"<<i<<std::endl;
                //     // std::cout<<"fix pt:"<<midYPs[j].first.transpose()<<std::endl;
                //     points.col(i)(3) = last_yaw + dyaw;
                //     times(i) = std::max(midYts(j) - last_t, 1e-3);
                //     last_t = midYts(j);
                //     last_yt = last_t;
                //     last_yaw = last_yaw + dyaw;
                //     yawRange[i].first = points.col(i)(3) - 1.5;
                //     yawRange[i].second = 3.0;

                //     hPolyIdx(i) = hCorridorIdx(midYPs[j].second);
                //     vPolyIdx(i) = hPolyIdx(i) * 2;
                //     Eigen::Vector3d up(-9999999.0, -9999999.0, -9999999.0), down(9999999.0, 9999999.0, 9999999.0), pt;
                //     for(int l = 0; l < vPolytopes[vPolyIdx(i)].cols(); l++){
                //         if(l != 0) pt = vPolytopes[vPolyIdx(i)].col(0) + vPolytopes[vPolyIdx(i)].col(l);
                //         else pt = vPolytopes[vPolyIdx(i)].col(0);
                //         up(0) = std::max(pt(0), up(0) - 1e-5);
                //         up(1) = std::max(pt(1), up(1) - 1e-5);
                //         up(2) = std::max(pt(2), up(2) - 1e-5);
                //         down(0) = std::min(pt(0), down(0) + 1e-5);
                //         down(1) = std::min(pt(1), down(1) + 1e-5);
                //         down(2) = std::min(pt(2), down(2) + 1e-5);
                //     }
                //     // std::cout<<"up: "<<up.transpose()<<std::endl;
                //     // std::cout<<"down: "<<down.transpose()<<std::endl;
                //     for(int dim = 0; dim < 3; dim++){
                //         points.col(i)(dim) = std::max(points.col(i)(dim), down(dim));
                //         points.col(i)(dim) = std::min(points.col(i)(dim), up(dim));
                //     }
                //     // spatialDim += vPolytopes[midYPs[j].second * 2].cols();
                //     j++;
                //     if(j != YpInsertIdx.size()){
                //         dyaw = YawDiff(midYPs[j].first(3), last_yaw);
                //     }
                //     else{
                //         dyaw = YawDiff(tailPVA(3, 0), last_yaw);
                //     }
                //     // std::cout<<"set4.3"<<std::endl;
                // }
                // else{
                    // std::cout<<"set4.4"<<std::endl;
                    // std::cout<<"last_yaw:"<<last_yaw<<" dyaw:"<<dyaw<<std::endl;
                    // std::cout<<"initPTs[k].second - last_yt:"<<initPTs[k].second - last_yt<<std::endl;
                points.col(i) = initPTs[i].first;
                points.col(i)(3) = last_yaw + YawDiff(initPTs[i].first(3),last_yaw);
                times(i) = std::max(initPTs[i].second - last_t, 1e-3);
                last_t = initPTs[i].second;
                yawRange[i].first = points.col(i)(3) - 1.5;
                yawRange[i].second = 3.0;
                hPolyIdx(i) = hCorridorIdx(i);
                vPolyIdx(i) = vCorridorIdx(i);
                spatialDim += vPolytopes[vPolyIdx(i)].cols();

                    // std::cout<<"set4.5"<<std::endl;
                // }
            }
            // std::cout<<"set4.6"<<std::endl;
            // std::cout<<"pieceN:"<<pieceN<<std::endl;
            // std::cout<<"hPolyIdx:"<<hPolyIdx.transpose()<<std::endl;
            // std::cout<<"hCorridorIdx:"<<hCorridorIdx.transpose()<<std::endl;
            times(pieceN - 1) = t_total - last_t;


            hPolyIdx(pieceN - 1) = hCorridorIdx(hCorridorIdx.size() - 1);


            endVelDim = 0;
            if(useTerminalCorridor){
                bool useRawCorridor = useCorridorDir;
                // std::cout<<"Fixsetup4.5"<<std::endl;
                if(useCorridorDir){
                    PolyhedronH velh, curIH;
                    velh.resize(6, 4);
                    velh.setZero();
                    Eigen::Matrix<double, 3, 2> bound;
                    for(int i = 0; i < 3; i++){
                        bound(i, 0) = -hPolytopes.back()(i*2, 3) - tailPVA(i, 0); // up
                        bound(i, 0) = std::max(0.002, bound(i, 0));
                        velh(i*2, i) = 1.0;
                        velh(i*2, 3) = -std::min(sqrt(2.0 * bound(i, 0) * magnitudeBounds[1] * 0.5), magnitudeBounds[0] * 0.9);
                        bound(i, 1) = hPolytopes.back()(i*2 + 1, 3) - tailPVA(i, 0); //down
                        bound(i, 1) = std::min(-0.002, bound(i, 1));
                        velh(i*2+1, i) = -1.0;
                        velh(i*2+1, 3) = -std::min(sqrt(-2.0 * bound(i, 1) * magnitudeBounds[1] * 0.5), magnitudeBounds[0] * 0.9);
                    }
                    curIH.resize(6+velCorridor.rows(), 4);
                    curIH.topRows(6) = velh;
                    curIH.bottomRows(velCorridor.rows()) = velCorridor;
                    useRawCorridor = geo_utils::enumerateVs(curIH, vEndVel);
                    if(useRawCorridor){
                        // std::cout<<"vend success===================:\n"<<vEndVel<<std::endl;
                        endVelDim = vEndVel.cols();
                        for(int i = 0; i < vEndVel.cols(); i++){
                            vEndVel.col(i) = vEndVel.col(i) - vEndVel.col(0);
                        }
                    }
                    else{
                        std::cout<<"vend failed2*****************"<<std::endl;
                    }
                }
                if(!useRawCorridor){
                    endVelDim = 8;
                    vEndVel.resize(3, 8);
                    Eigen::Matrix<double, 3, 2> bound;
                    Eigen::Vector3d vmax, vmin; 
                    for(int i = 0; i < 3; i++){
                        bound(i, 0) = -hPolytopes.back()(i*2, 3) - tailPVA(i, 0); // up
                        bound(i, 0) = std::max(0.001, bound(i, 0));
                        vmax(i) = std::min(sqrt(2.0 * bound(i, 0) * magnitudeBounds[1] * 0.5), magnitudeBounds[0] * 0.95);
                        bound(i, 1) = hPolytopes.back()(i*2 + 1, 3) - tailPVA(i, 0); //down
                        bound(i, 1) = std::min(-0.001, bound(i, 1));
                        vmin(i) = -std::min(sqrt(-2.0 * bound(i, 1) * magnitudeBounds[1] * 0.5), magnitudeBounds[0] * 0.95);
                    }

                    // std::cout<<"bound:"<<bound<<std::endl;
                    // std::cout<<"vmin:"<<vmin.transpose()<<std::endl;
                    // std::cout<<"vmax:"<<vmax.transpose()<<std::endl;
                    // std::cout<<"set5"<<std::endl;

                    for(int dim1 = 0; dim1 <= 1; dim1++){
                        for(int dim2 = 0; dim2 <= 1; dim2++){
                            for(int dim3 = 0; dim3 <= 1; dim3++){
                                vEndVel(0, 4*dim3 + 2*dim2 + dim1) = dim1 ? vmax(0) : vmin(0);
                                vEndVel(1, 4*dim3 + 2*dim2 + dim1) = dim2 ? vmax(1) : vmin(1);
                                vEndVel(2, 4*dim3 + 2*dim2 + dim1) = dim3 ? vmax(2) : vmin(2);
                            }
                        }
                    }
                    for(int j = 1; j < 8; j++){
                        vEndVel.col(j) = vEndVel.col(j) - vEndVel.col(0);
                    }
                }
            }
            else{
                endVelDim = 8;
                vEndVel.resize(3, 8);
                Eigen::Matrix<double, 3, 2> bound;
                Eigen::Vector3d vmax, vmin; 
                for(int i = 0; i < 3; i++){
                    bound(i, 0) = -hPolytopes.back()(i*2, 3) - tailPVA(i, 0); // up
                    bound(i, 0) = std::max(0.001, bound(i, 0));
                    vmax(i) = std::min(sqrt(2.0 * bound(i, 0) * magnitudeBounds[1] * 0.5), magnitudeBounds[0] * 0.001);
                    bound(i, 1) = hPolytopes.back()(i*2 + 1, 3) - tailPVA(i, 0); //down
                    bound(i, 1) = std::min(-0.001, bound(i, 1));
                    vmin(i) = -std::min(sqrt(-2.0 * bound(i, 1) * magnitudeBounds[1] * 0.5), magnitudeBounds[0] * 0.001);
                }

                // std::cout<<"bound:"<<bound<<std::endl;
                // std::cout<<"vmin:"<<vmin.transpose()<<std::endl;
                // std::cout<<"vmax:"<<vmax.transpose()<<std::endl;
                // std::cout<<"set5"<<std::endl;

                for(int dim1 = 0; dim1 <= 1; dim1++){
                    for(int dim2 = 0; dim2 <= 1; dim2++){
                        for(int dim3 = 0; dim3 <= 1; dim3++){
                            vEndVel(0, 4*dim3 + 2*dim2 + dim1) = dim1 ? vmax(0) : vmin(0);
                            vEndVel(1, 4*dim3 + 2*dim2 + dim1) = dim2 ? vmax(1) : vmin(1);
                            vEndVel(2, 4*dim3 + 2*dim2 + dim1) = dim3 ? vmax(2) : vmin(2);
                        }
                    }
                }
                for(int j = 1; j < 8; j++){
                    vEndVel.col(j) = vEndVel.col(j) - vEndVel.col(0);
                }
            }
            EndDy(0) = -magnitudeBd(3) * 0.99;
            EndDy(1) = magnitudeBd(3) * 1.98;
            // std::cout<<"vEndVel:"<<vEndVel.transpose()<<std::endl;
            // std::cout<<"set5.5"<<std::endl;

            // Setup for MINCO_S3NU, FlatnessMap, and L-BFGS solver
            minco.setConditions(headPVA, tailPVA, pieceN);
            // flatmap.reset(physicalPm(0), physicalPm(1), physicalPm(2),
            //               physicalPm(3), physicalPm(4), physicalPm(5));
            // std::cout<<"set5.6"<<std::endl;

            // Allocate temp variables

            gradByPoints.resize(4, pieceN - 1);
            gradByTimes.resize(pieceN);
            partialGradByCoeffs.resize(6 * pieceN, 4);
            partialGradByTimes.resize(pieceN);
            // std::cout<<"set6"<<std::endl;

            return true;
        }

        /**
         * @brief call after setup()
         * 
         * @param traj       the optimized traj   
         * @param relCostTol 
         * @return double 
         */
        inline double optimize(Trajectory4<5> &traj,
                                Eigen::VectorXd vep,
                                Eigen::VectorXd dyep,
                               const double &relCostTol)
        {
            Eigen::VectorXd xBest;

            Eigen::VectorXd x(temporalDim + spatialDim + endVelDim + yawDim + 2);
            Eigen::Map<Eigen::VectorXd> tau(x.data(), temporalDim);
            Eigen::Map<Eigen::VectorXd> xi(x.data() + temporalDim, spatialDim);
            Eigen::Map<Eigen::VectorXd> evi(x.data() + temporalDim + spatialDim, endVelDim);
            Eigen::Map<Eigen::VectorXd> yi(x.data() + temporalDim + spatialDim + endVelDim, yawDim);
            Eigen::Map<Eigen::VectorXd> edyi(x.data() + temporalDim + spatialDim + endVelDim + yawDim, 2);
            // std::cout<<"temporalDim:"<<temporalDim<<std::endl;
            // std::cout<<"spatialDim:"<<spatialDim<<std::endl;
            // std::cout<<"endVelDim:"<<endVelDim<<std::endl;
            // std::cout<<"yawDim:"<<yawDim<<std::endl;
            //points are downsampled points of shortPath 
            // setInitial(shortPath, allocSpeed, yawPath, allocYawSpeed, pieceIdx, points, times); //todo
            // double tsum = times.sum();
            // times = times * std::max(tsum, minT) / tsum;
            backwardT(times, tau);
            backwardP(points, vPolyIdx, vPolytopes, /*fixYpIdx,*/ xi);

            // std::cout<<"points0:\n"<<points<<std::endl;
            // std::cout<<"headPVA:\n"<<headPVA<<std::endl;
            // std::cout<<"tailPVA:\n"<<tailPVA<<std::endl;
            // evi.setOnes();

            if(evi.size() != vep.size() || dyep.size() != edyi.size()){
                std::cout<<"evi:"<<evi.size()<<" vep:"<<vep.size()<<std::endl;
                std::cout<<"edyi:"<<edyi.size()<<" dyep:"<<dyep.size()<<std::endl;
                getchar();
            }
            evi = vep;
            yi.setOnes();
            yi = yi / sqrt(2.0);
            edyi = dyep;
            // edyi(0) = 0.5;
            // edyi(1) = 0.5;

        
            Eigen::Vector3d endV;
            double dye;

            double minCostFunctional;
            lbfgs_params.mem_size = 256;
            lbfgs_params.past = 3;
            lbfgs_params.min_step = 1.0e-32;
            lbfgs_params.g_epsilon = 0.0;
            lbfgs_params.delta = relCostTol;
            lbfgs_params.max_iterations = 10;
            double t_best = 999999.0;
            int ret;

            for(int i = 0; i < 2; i++){
                ret = lbfgs::lbfgs_optimize(x,
                    minCostFunctional,
                    &GCOPTER_COVER_PolytopeSFC::costFunctional,
                    nullptr,
                    nullptr,
                    this,
                    lbfgs_params);
                forwardT(tau, times);
                forwardP(xi, vPolyIdx, vPolytopes, yawRange, yi, /*fixYpIdx,*/ points);
                forwardV(vEndVel,evi, EndDy, edyi, endV, dye);
                debugpts = points.topRows(3);
                minco.setEndDy(dye);
                minco.setEndVel(endV);
                minco.setParameters(points, times);
                if(i == 0){
                    if(TrajFeaCheck(times, minco.getCoeffs(), hPolyIdx, hPolytopes,
                            smoothEps, integralRes, magnitudeBd)){
                        xBest = x;
                        t_best = times.sum();
                    }
                }
                else{
                    if(times.sum() < t_best && TrajFeaCheck(times, minco.getCoeffs(), hPolyIdx, hPolytopes,
                            smoothEps, integralRes, magnitudeBd)){
                        xBest = x;
                        t_best = times.sum();
                    }
                }
                times *= 0.8;
                backwardT(times, tau);
            }
            if(t_best < 999998.0){
                x = xBest;
                times *= 0.8;
                backwardT(times, tau);
            }

            lbfgs_params.max_iterations = 128;
            ret = lbfgs::lbfgs_optimize(xBest,
                minCostFunctional,
                &GCOPTER_COVER_PolytopeSFC::costFunctional,
                nullptr,
                nullptr,
                this,
                lbfgs_params);

            forwardV(vEndVel,evi, EndDy, edyi, endV, dye);

            forwardT(tau, times);
            forwardP(xi, vPolyIdx, vPolytopes, yawRange, yi, /*fixYpIdx,*/ points);
            debugpts = points.topRows(3);
            minco.setEndDy(dye);
            minco.setEndVel(endV);
            minco.setParameters(points, times);

            if(times.sum() < t_best && TrajFeaCheck(times, minco.getCoeffs(), hPolyIdx, hPolytopes,
                    smoothEps, integralRes, magnitudeBd)){
                xBest = x;
                t_best = times.sum();
            }

            if(t_best < 999998.0){
                Eigen::Map<Eigen::VectorXd> tauBest(xBest.data(), temporalDim);
                Eigen::Map<Eigen::VectorXd> xiBest(xBest.data() + temporalDim, spatialDim);
                Eigen::Map<Eigen::VectorXd> eviBest(xBest.data() + temporalDim + spatialDim, endVelDim);
                Eigen::Map<Eigen::VectorXd> yiBest(xBest.data() + temporalDim + spatialDim + endVelDim, yawDim);
                Eigen::Map<Eigen::VectorXd> edyiBest(xBest.data() + temporalDim + spatialDim + endVelDim + yawDim, 2);

                forwardT(tauBest, times);
                forwardP(xiBest, vPolyIdx, vPolytopes, yawRange, yi, /*fixYpIdx,*/ points);
                forwardV(vEndVel,eviBest, EndDy, edyiBest, endV, dye);
                debugpts = points.topRows(3);
                minco.setEndDy(dye);
                minco.setEndVel(endV);
                minco.setParameters(points, times);
                minco.getTrajectory(traj);
            }
            else{

                traj.clear();
                minCostFunctional = INFINITY;
                std::cout << "Optimization Failed: "
                          << lbfgs::lbfgs_strerror(ret)
                          << std::endl;
            }
            // std::cout<<"end v:"<<endV.transpose()<<std::endl;
            // std::cout<<"end v:"<<endV.transpose()<<"  dye:"<<dye<<std::endl;

            // if (ret >= 0 || ret == lbfgs::LBFGSERR_MAXIMUMLINESEARCH || ret == lbfgs::LBFGSERR_MAXIMUMITERATION)
            // {
            //     forwardT(tau, times);
            //     forwardP(xi, vPolyIdx, vPolytopes, yawRange, yi, /*fixYpIdx,*/ points);
            //     // std::cout<<"points1:\n"<<points<<std::endl;
            //     // std::cout<<"times1:"<<times.transpose()<<std::endl;
            //     debugpts = points.topRows(3);
            //     // forwardP(xi, vPolyIdx, vPolytopes, points);
            //     minco.setEndDy(dye);
            //     minco.setEndVel(endV);
            //     minco.setParameters(points, times);
            //     if(!TrajFeaCheck(times, minco.getCoeffs(), hPolyIdx, hPolytopes,
            //                         smoothEps, integralRes, magnitudeBd)){
            //         std::cout << "Feasibility Failed2: "<<std::endl;
            //         return INFINITY;
            //     }
            //     minco.getTrajectory(traj);
            // }
            // else
            // {
            //     traj.clear();
            //     minCostFunctional = INFINITY;
            //     std::cout << "Optimization Failed: "
            //               << lbfgs::lbfgs_strerror(ret)
            //               << std::endl;
            // }
            std::cout<<"optimize6"<<std::endl;

            return minCostFunctional;
        }
    };

}

#endif
