function load_data_file()
    data_file = joinpath(@__DIR__, "data.txt")
    open(data_file, "r") do file
        for line in eachline(file)
            println(line)
        end
    end
end

load_data_file()



