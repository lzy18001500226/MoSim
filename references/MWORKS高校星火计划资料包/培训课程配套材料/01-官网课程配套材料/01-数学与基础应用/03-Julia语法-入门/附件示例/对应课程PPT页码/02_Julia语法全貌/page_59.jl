m = match(r"(a|b)(c)?(d)", "ad")
m.match
m.captures
m.offset
m.offsets
m = match(r"^\s*(?:#|$)", "abc")
if m === nothing
    println("not a comment")
else
    println("blank or comment")
end




