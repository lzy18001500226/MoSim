module M
export M_member
M_member() = "Hello belong to M!"
end
Main.M

module A
module B
export hello
hello() = "Hello"
end # end of B
end # end of A
Main.A


