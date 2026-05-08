#include <vector>
#include <numeric>
double kurtosis(const std::vector<double>& X) {
    double mu = std::accumulate(X.begin(), X.end(), 0.0) / X.size();
    double E = 0.0, S = 0.0;
    for (auto x : X) {
        double x2 = (x - mu) * (x - mu);
        double x4 = x2 * x2;
        E += x4;
        S += x2;
    }
    E /= X.size();
    S /= X.size();
    return E / (S * S);
}


