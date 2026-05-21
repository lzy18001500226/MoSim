a=-1
class(a) % 'double'

% ok
2^a

% 报错
a=int64(-1)
2^a
% Error using .^ 
% Integers can only be raised to positive integral powers.



