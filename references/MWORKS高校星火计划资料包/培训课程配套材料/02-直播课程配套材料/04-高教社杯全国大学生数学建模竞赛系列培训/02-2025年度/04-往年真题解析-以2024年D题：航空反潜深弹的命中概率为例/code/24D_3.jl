using TyStatistics
function x7()
    σ = 120
    L = 100
    R = 20
    W = 20
    H = 25
    σ_z = 40
    l1 = 120
    h0 = 150

    a = L + 2 * R
    b = W + 2 * R

    f = (x, y) -> (1 / (2 * pi * σ^2)) * exp(-(x .^ 2 + y .^ 2) / (2 * σ^2))
    Phi = x -> normcdf(x, 0, 1)
    dm = 1 / (1 - Phi((l1 - h0) / (σ_z)))
    g_z = z -> (1 / σ_z) * dm * (1 / sqrt(2 * pi)) * exp(-((z - h0) .^ 2) / (2 * σ_z^2))
    fun = (x, y, z) -> f.(x, y) .* g_z.(z)
    d = 152.5:1:165

    I21 = [0]
    I22 = [0]
    I23 = [0]
    I24 = [0]
    I31 = [0]
    I32 = [0]
    I33 = [0]
    I34 = [0]
    I41 = [0]
    I42 = [0]
    I43 = [0]
    I44 = [0]

    I511 = [0]
    I512 = [0]
    I513 = [0]
    I514 = [0]
    I521 = [0]
    I522 = [0]
    I523 = [0]
    I524 = [0]
    I531 = [0]
    I532 = [0]
    I533 = [0]
    I534 = [0]

    I61 = [0]
    I62 = [0]
    I63 = [0]
    I64 = [0]
    I71 = [0]
    I72 = [0]
    I73 = [0]
    I74 = [0]
    I81 = [0]
    I82 = [0]
    I83 = [0]
    I84 = [0]

    I11 = [0]
    I12 = [0]
    I13 = [0]
    I14 = [0]

    I1 = [0]

    for i = 1:length(d)
        I110 = ty_integral3(fun, -L / 2, L / 2, -W / 2, W / 2, l1, d[i] - R - H / 2)[1]
        I120 = ty_integral3(fun, a - L / 2, a + L / 2, b - W / 2, b + W / 2, l1, d[i] - R - H / 2)[1]
        I130 = ty_integral3(fun, -L / 2, L / 2, b - W / 2, b + W / 2, l1, d[i] - R - H / 2)[1]
        I140 = ty_integral3(fun, a - L / 2, a + L / 2, -W / 2, W / 2, l1, d[i] - R - H / 2)[1]
        I11 = [I11 I110]
        I12 = [I12 I120]
        I13 = [I13 I130]
        I14 = [I14 I140]
        I1 = I11 + I12 + I13 + I14

        dx = 1
        dy = 1
        dz = 1
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
        I21 = [I21 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> a - L / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        xmax = z -> a - L / 2
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
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
        I22 = [I22 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> -L / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        xmax = z -> -L / 2
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
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
        I23 = [I23 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> a - L / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        xmax = z -> a - L / 2
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
        I24 = [I24 sum]

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
        I31 = [I31 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = a - 0.5 * L
        xmax = a + 0.5 * L
        ymin = z -> b - W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        ymax = z -> b + W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
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
        I32 = [I32 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = -0.5 * L
        xmax = 0.5 * L
        ymin = z -> b - W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        ymax = z -> b + W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
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
        I33 = [I33 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = a - 0.5 * L
        xmax = a + 0.5 * L
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
        I34 = [I34 sum]

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
        I41 = [I41 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> a + 0.5 * L
        xmax = z -> a + 0.5 * L + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
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
        I42 = [I42 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> 0.5 * L
        xmax = z -> 0.5 * L + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
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
        I43 = [I43 sum]

        sum = 0
        zmin = d[i] - R - 0.5 * H
        zmax = d[i] - 0.5 * H
        xmin = z -> a + 0.5 * L
        xmax = z -> a + 0.5 * L + sqrt(max((R^2 - (d[i] - z - H / 2) .^ 2), 0))
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
        I44 = [I44 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> -0.5 * L - R
        xmax = z -> -0.5 * L
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I511 = [I511 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> a - 0.5 * L - R
        xmax = z -> a - 0.5 * L
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I512 = [I512 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> -0.5 * L - R
        xmax = z -> -0.5 * L
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I513 = [I513 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> a - 0.5 * L - R
        xmax = z -> a - 0.5 * L
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I514 = [I514 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> -0.5 * L
        xmax = z -> 0.5 * L
        ymin = (x, z) -> -W / 2 - R
        ymax = (x, z) -> W / 2 + R
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
        I521 = [I521 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> a - 0.5 * L
        xmax = z -> a + 0.5 * L
        ymin = (x, z) -> b - W / 2 - R
        ymax = (x, z) -> b + W / 2 + R
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
        I522 = [I522 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> -0.5 * L
        xmax = z -> 0.5 * L
        ymin = (x, z) -> b - W / 2 - R
        ymax = (x, z) -> b + W / 2 + R
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
        I523 = [I523 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> a - 0.5 * L
        xmax = z -> a + 0.5 * L
        ymin = (x, z) -> -W / 2 - R
        ymax = (x, z) -> W / 2 + R
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
        I524 = [I524 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> 0.5 * L
        xmax = z -> 0.5 * L + R
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I531 = [I531 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> a + 0.5 * L
        xmax = z -> a + 0.5 * L + R
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I532 = [I532 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> 0.5 * L
        xmax = z -> 0.5 * L + R
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I533 = [I533 sum]

        sum = 0
        zmin = d[i] - 0.5 * H
        zmax = d[i] + 0.5 * H
        xmin = z -> a + 0.5 * L
        xmax = z -> a + 0.5 * L + R
        ymin = (x, z) -> -W / 2 - sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> W / 2 + sqrt(max((R^2 - (x - L / 2) .^ 2), 0))
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
        I534 = [I534 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
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
        I61 = [I61 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> a - 0.5 * L - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        xmax = z -> a - 0.5 * L
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
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
        I62 = [I62 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> -0.5 * L - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        xmax = z -> -0.5 * L
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x + L / 2) .^ 2), 0))
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
        I63 = [I63 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> a - 0.5 * L - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        xmax = z -> a - 0.5 * L
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
        I64 = [I64 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
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
        I71 = [I71 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> a - 0.5 * L
        xmax = z -> a + 0.5 * L
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
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
        I72 = [I72 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> -0.5 * L
        xmax = z -> 0.5 * L
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
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
        I73 = [I73 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> a - 0.5 * L
        xmax = z -> a + 0.5 * L
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
        I74 = [I74 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> 0.5 * L
        xmax = z -> 0.5 * L + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
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
        I81 = [I81 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> a + 0.5 * L
        xmax = z -> a + 0.5 * L + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
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
        I82 = [I82 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> 0.5 * L
        xmax = z -> 0.5 * L + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
        ymin = (x, z) -> b - W / 2 - sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
        ymax = (x, z) -> b + W / 2 + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2 - (x - L / 2) .^ 2), 0))
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
        I83 = [I83 sum]

        sum = 0
        zmin = d[i] + 0.5 * H
        zmax = d[i] + 0.5 * H + R
        xmin = z -> a + 0.5 * L
        xmax = z -> a + 0.5 * L + sqrt(max((R^2 - (d[i] - z + H / 2) .^ 2), 0))
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
        I84 = [I84 sum]
    end
    I = @. I11 + 4 * I12 + 2 * I13 + 2 * I14 + I21 + 4 * I22 + 2 * I23 + 2 * I24 + I31 + 4 * I32 + 2 * I33 + 2 * I34 + I41 + 4 * I42 + 2 * I43 + 2 * I44 + I511 + 4 * I512 + 2 * I513 +
           2 * I514 + I521 + 4 * I522 + 2 * I523 + 2 * I524 + I531 + 4 * I532 + 2 * I533 + 2 * I534 + I61 + 4 * I62 + 2 * I63 + 2 * I64 + I71 + 4 * I72 + 2 * I73 + 2 * I74 + I81 + 4 * I82 +
           2 * I83 + 2 * I84
    return I, I1
end
I, I1 = x7()
num,index = findmax(I[1, 2:end])
d = 152.5:1:165

println("定深引爆深度为$(d[index])时，具有最大命中概率P=$(num)。")