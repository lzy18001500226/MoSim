foo() = "Hello I'm foo"
module A
export foo
foo() = "Hello I'm foo from A"
end
using .A
using .A: foo as foo1
foo1()
A.foo()


