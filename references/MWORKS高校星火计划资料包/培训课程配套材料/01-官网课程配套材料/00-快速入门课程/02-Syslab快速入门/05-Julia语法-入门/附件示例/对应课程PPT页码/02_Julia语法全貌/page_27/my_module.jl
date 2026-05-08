module ModuleA
export add1
add1(x) = x + 1
end

module ModuleB
import LinearAlgebra: norm
export my_hypot
my_hypot(x, y) = norm([x, y])
end



