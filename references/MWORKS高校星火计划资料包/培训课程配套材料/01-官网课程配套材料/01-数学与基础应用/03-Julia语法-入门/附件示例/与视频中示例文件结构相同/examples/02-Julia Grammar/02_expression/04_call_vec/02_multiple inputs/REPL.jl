include("stat.jl")
values = [12.7, 45.4, 98.9, 26.6, 53.1];
ave, stdev = stat(values)
ave
stdev

R = stat(values)

_, stdev = stat(values)
