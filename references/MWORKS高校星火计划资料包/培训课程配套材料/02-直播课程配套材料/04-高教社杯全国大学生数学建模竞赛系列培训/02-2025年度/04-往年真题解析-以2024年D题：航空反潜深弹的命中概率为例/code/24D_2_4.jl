#情形2
using TyStatistics
function x5()

    σ = 120
    L = 100
    R = 20
    W = 20
    H = 25
    σ_z = 40
    l1 = 120
    h0 = 150

    f = (x, y) -> (1 / (2 * pi * σ^2)) * exp(-(x .^ 2 + y .^ 2) / (2 * σ^2))
    Phi = x -> normcdf(x, 0, 1)
    dm = 1 / (1 - Phi((l1 - h0) / (σ_z)))
    g_z = z -> (1 / σ_z) * dm * (1 / sqrt(2 * pi)) * exp(-((z - h0) .^ 2) / (2 * σ_z^2))
    fun = (x, y, z) -> f.(x, y) .* g_z.(z)
    d = 87.5:1:100

    I6 = [0]
    I7 = [0]
    I8 = [0]


    for i = 1:length(d)
        dx = 0.5
        dy = 0.5
        dz = 0.5
        sum = 0
        zmin = l1
        zmax = d[i] + R + 0.5 * H
        xmin = z -> -0.5 * L - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        xmax = z -> -0.5 * L
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
        for z = zmin:dz:zmax
            xl = xmin(z)
            xu = xmax(z)
            for x = xl:dx:xu
                yl = ymin(x, z)
                yu = ymax(x, z)
                for y = yl:dy:yu
                    sum = sum + fun(x, y, z) * dx * dy * dz
                end
            end
        end
        I6 = [I6 sum]

        sum = 0
        zmin = l1
        zmax = d[i] + R + 0.5 * H
        xmin = z -> -0.5 * L
        xmax = z -> 0.5 * L
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        for z = zmin:dz:zmax
            xl = xmin(z)
            xu = xmax(z)
            for x = xl:dx:xu
                yl = ymin(x, z)
                yu = ymax(x, z)
                for y = yl:dy:yu
                    sum = sum + fun(x, y, z) * dx * dy * dz
                end
            end
        end
        I7 = [I7 sum]

        sum = 0
        zmin = l1
        zmax = d[i] + R + 0.5 * H
        xmin = z -> 0.5 * L
        xmax = z -> 0.5 * L + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))####这个位置论文中给错了########
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
        for z = zmin:dz:zmax
            xl = xmin(z)
            xu = xmax(z)
            for x = xl:dx:xu
                yl = ymin(x, z)
                yu = ymax(x, z)
                for y = yl:dy:yu
                    sum = sum + fun(x, y, z) * dx * dy * dz
                end
            end
        end
        I8 = [I8 sum]



    end

    return I6, I7, I8
end
# I0 = x5()
# I = sum(x5())
# d = 87.5:1:100
# plot(d, I[1, 2:end])