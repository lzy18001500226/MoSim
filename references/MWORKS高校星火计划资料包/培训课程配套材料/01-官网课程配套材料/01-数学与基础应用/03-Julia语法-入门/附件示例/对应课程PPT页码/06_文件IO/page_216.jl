io = IOBuffer("Welcome to Syslab.");
array = Vector{UInt8}(undef, 5);
read!(io, array)
let
    array = Vector{UInt8}(undef, 5)
    read!("example.txt", array)
end



