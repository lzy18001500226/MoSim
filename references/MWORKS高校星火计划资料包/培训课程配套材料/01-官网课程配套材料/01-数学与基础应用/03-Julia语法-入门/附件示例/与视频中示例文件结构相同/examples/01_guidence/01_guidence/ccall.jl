cpath = @ccall getenv("PATH"::Cstring)::Cstring

unsafe_string(cpath)
