macro showarg(x)
    show(x)
    # ... remainder of macro, returning an expression
end
@showarg(a)
@showarg(1 + 1)
@showarg 6
@showarg(println("Yo!"))


