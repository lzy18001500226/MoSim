a = -1
typeof(a) # Int64
# 报错
2^a
#=
ERROR: DomainError with -1:
Cannot raise an integer x to a negative power -1.
=#
# ok
2^float(a)




