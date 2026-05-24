io = IOBuffer();
write(io, "Welcome to Syslab.\n", "Second Line");
print(String(take!(io)))
io = IOBuffer();
write(io, "Welcome to Syslab.\n") + write(io, "Second Line")
print(String(take!(io)))



