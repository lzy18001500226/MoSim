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

add(x, y) = x + y

function f(x, y)
    nbits = rand((16, 32, 64, 128))
    x = get_number(x, nbits)
    y = get_number(y, nbits)
    return add(x, y)
end

methodinstances(add) 
f(1, 2)
methodinstances(add) 
f(1, 2)
methodinstances(add) 
f(1, 2)
methodinstances(add)

