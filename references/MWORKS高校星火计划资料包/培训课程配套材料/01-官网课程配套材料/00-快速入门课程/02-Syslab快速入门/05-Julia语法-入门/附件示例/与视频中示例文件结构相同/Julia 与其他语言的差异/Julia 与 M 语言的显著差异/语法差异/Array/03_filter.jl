x = [1 3 5 7 9]

x[x.>3]
# [5, 7, 9]

x = x[x.<=3]
# x = [1, 3]

x = [1 3 5 7 9]
y = filter(i->i>3, x)

arr = [1,2,3,4,5]
filter(x->x%2==0, arr)