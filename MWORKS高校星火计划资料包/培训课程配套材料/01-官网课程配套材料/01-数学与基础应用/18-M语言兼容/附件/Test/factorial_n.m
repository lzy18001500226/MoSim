%% 分节符
function result = factorial_n(n)
    result = 1
    for i = 1:n
        result = result * i 
    end 
end
%% 
Age = [38;43;38;40;49];
Smoker = logical([1;0;1;0;1]);
Weight = [71;69;64;67;64];
Height = [176;163;131;133;119];
BloodPressure = [124 93; 109 77; 125 83; 117 75; 122 80];
T = table(Age,Smoker,Weight,Height,BloodPressure)
T1=T{:,:}