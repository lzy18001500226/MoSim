using BenchmarkTools

A = rand(2, 2)
B = rand(2, 2)
@btime A * B;

# ---
struct Matrix22{T} <: AbstractArray{T,2}
    data::Tuple{Tuple{T,T},Tuple{T,T}}
end
function Matrix22(A::AbstractMatrix)
    @assert size(A) == (2, 2)
    return Matrix22(((A[1], A[3]), (A[2], A[4])))
end

Base.size(A::Matrix22) = (2, 2)
Base.getindex(A::Matrix22, i::Int, j::Int) = A.data[i][j]


function Base.:(*)(A::Matrix22, B::Matrix22)
    a11, a21, a12, a22 = A
    b11, b21, b12, b22 = B
    c11 = a11 * b11 + a12 * b21
    c12 = a11 * b12 + a12 * b22
    c21 = a21 * b11 + a22 * b21
    c22 = a21 * b12 + a22 * b22
    return Matrix22(((c11, c12), (c21, c22)))
end

A = [1 2; 3 4]
A * A

Matrix22(A) * Matrix22(A)

# ---

A = Matrix22(rand(2, 2));
B = Matrix22(rand(2, 2));

@btime A * B;
