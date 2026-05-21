# 关键词参数在 ; 之后
function mul(; x, y, kwargs...)
  z = 0
  if haskey(kwargs, :z)
    z = kwargs[:z]
  end
  return x + 2 * y + z
end
mul(y=2, x=1, z=1)
mul(y=2, x=1, z=1)
# 1 + 2*2 + 1 = 6







