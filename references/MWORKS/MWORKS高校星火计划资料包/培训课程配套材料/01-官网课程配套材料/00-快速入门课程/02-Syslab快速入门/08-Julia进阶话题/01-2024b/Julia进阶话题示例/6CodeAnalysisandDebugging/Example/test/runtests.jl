using Test
using Example

@testset "Example" begin
    @test greet() == "Hello, World!"
end