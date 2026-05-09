occursin("world", "Hello, world.")
occursin("a", "Xylophon")
occursin('o', "Xylophon")
occursin(r"^\s*(?:#|$)", "not a comment")
occursin(r"^\s*(?:#|$)", "# a comment")

m = match(r"(a|b)(c)?(d)", "ad")
m.match
m.captures
m.offset
m.offsets



