function create_log_file()
    log_file = joinpath(dirname(@__FILE__), "logfile.txt")
    open(log_file, "w") do file
        write(file, "Log entry")
    end
    println("Log file created at: ", log_file)
end

create_log_file()



