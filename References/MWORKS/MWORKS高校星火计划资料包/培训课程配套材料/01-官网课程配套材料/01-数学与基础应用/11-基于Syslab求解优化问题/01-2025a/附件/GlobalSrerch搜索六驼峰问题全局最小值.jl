using TyGlobalOptimization
using TyOptimization
using TyRandom
gs = GlobalSearch(; rng=MT19937ar(5489))
function sixmin(x)
    return (4 * x[1]^2 - 2.1 * x[1]^4 + x[1]^6 / 3 + x[1] * x[2] - 4 * x[2]^2 + 4 * x[2]^4)
end
problem = createOptimProblem(
    "fmincon";
    x0=[-1, 2],
    objective=sixmin,
    lb=[-3, -3],
    ub=[3, 3],
    options=optimoptions("fmincon"; Algorithm="sqp"),
)
x, fval = Base.run(gs, problem)

#运行结果

# GlobalSearch stopped because it analyzed all the trial points.

# All 29 local solver runs converged with a positive local solver exit flag.

# x = [-0.08984200594212277, 0.7126563939610455]
# fval = -1.0316284534898765
