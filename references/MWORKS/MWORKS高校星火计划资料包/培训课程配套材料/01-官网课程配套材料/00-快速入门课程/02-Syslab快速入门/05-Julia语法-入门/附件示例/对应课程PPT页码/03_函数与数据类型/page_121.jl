"abracadabra" < "xylophone"
"abracadabra" == "xylophone"

"Hello, world." != "Goodbye, world."
"1 + 2 = 3" == "1 + 2 = $(1 + 2)"

findfirst(isequal('o'), "xylophone")
findlast(isequal('o'), "xylophone")
findfirst(isequal('z'), "xylophone")

findnext(isequal('o'), "xylophone", 1)
findnext(isequal('o'), "xylophone", 5)
findprev(isequal('o'), "xylophone", 5)
findnext(isequal('o'), "xylophone", 8)



