function f(x::Float64)
   if x < 0.5
       return Int(0)
   else
       return Float64(1.0)
   end
end

function f(x::Float64)
   if x < 0.5
       y  =  1
   else
       y  =  x^2
   end
   return Float64(y)
end

function mysum(A::Array{Float64})
   rst = 0
   for i in eachindex(A)
         rst += A[i]
   end
   return rst
end

function f(x)
   if x < 0.5
       return zero(x)
   else
       return one(x)
   end
end

function mysum(A::AbstractArray)
   rst = zero(eltype(A))
   for i in eachindex(A)
         rst += A[i]
   end
   return rst
end

function get_number(x,  nbits)
   if nbits == 16
         Float16(x)
   elseif nbits == 32
         Float32(x)
   elseif nbits == 64
         Float64(x)
   elseif nbits > 64
         BigFloat(x)
   end
end



