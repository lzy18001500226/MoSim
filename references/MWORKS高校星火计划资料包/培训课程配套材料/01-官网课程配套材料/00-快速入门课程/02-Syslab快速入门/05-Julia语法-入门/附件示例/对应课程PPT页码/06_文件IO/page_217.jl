io = IOBuffer("Welcome to Syslab.");
for c in readeach(io, Char)
    c == '\n' && break
    print(c)
end

buf = IOBuffer("  Welcome to Syslab.");
skipchars(isspace, buf);
read(buf, String)

buf = IOBuffer(" # This line is a comment.\n  Welcome to Syslab.");
skipchars(isspace, buf; linecomment='#');
read(buf, String)


