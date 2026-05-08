
A=rand(64,64)
function mysum(A)
    rst = zero(eltype(A))
@simd for i in eachindex(A)
    rst += A[i]
end
return rst
end

function mysum_mf64(A::Matrix{Float64})
rst = zero(eltype(A))
@simd for i in eachindex(A)
    rst += A[i]
end
return rst

end


