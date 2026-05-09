#情形5
using TyStatistics
function x2()

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
    d = 152.5:1:180

    I1 = [0]
    I2 = [0]
    I3 = [0]
    I4 = [0]
    I5 = [0]
    I6 = [0]
    I7 = [0]
    I8 = [0]
    I = []


    for i = 1:length(d)
        I11 = ty_integral3(fun, -L / 2, L / 2, -W / 2, W / 2, l1, d[i] - R - H / 2)[1]
        I51 = 0.083734 * integral(g_z, d[i] - H / 2, d[i] + H / 2)[1]
        I1 = [I1 I11]
        I5 = [I5 I51]
        dx = 0.5
        dy = 0.5
        dz = 0.5
        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> -L / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        xmax = z -> -L / 2
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
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
        I2 = [I2 sum]


        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = -0.5 * L
        xmax = 0.5 * L
        ymin = z -> -W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        ymax = z -> W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        for z = zmin:dz:zmax
            xl = xmin
            xu = xmax
            for x = xl:dx:xu
                yl = ymin(z)
                yu = ymax(z)
                for y = yl:dy:yu
                    sum = sum + fun(x, y, z) * dx * dy * dz
                end
            end
        end
        I3 = [I3 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> 0.5 * L
        xmax = z -> 0.5 * L + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
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
        I4 = [I4 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
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
        zmin = d[i] + 0.5 * H
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
        zmin = d[i] + 0.5 * H
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

    return I1, I2, I3, I4, I5, I6, I7, I8
end
# I0 = x2()
# I = sum(x2())
# d = 152.5:1:180
# plot(d, I[1, 2:end])