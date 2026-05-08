re = r"^\s*(?:#|$)"
typeof(re)
occursin(r"^\s*(?:#|$)", "not a comment")
occursin(r"^\s*(?:#|$)", "# a comment")


