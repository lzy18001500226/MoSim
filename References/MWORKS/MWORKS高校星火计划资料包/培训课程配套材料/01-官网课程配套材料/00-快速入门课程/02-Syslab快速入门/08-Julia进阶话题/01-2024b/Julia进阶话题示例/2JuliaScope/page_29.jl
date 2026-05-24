module Amod
x = 1
foo() = x
end
import .Amod
x = -1
println(Amod.foo())
## 1
