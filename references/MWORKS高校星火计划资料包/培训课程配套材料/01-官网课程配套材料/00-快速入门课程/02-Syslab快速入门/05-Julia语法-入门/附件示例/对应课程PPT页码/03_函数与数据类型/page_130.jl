Base.@kwdef struct Person
  name::String = "Tom"
  age::Int = 30
  gender::String = "Unknown"
end

p = Person();

println("Name: ", p.name, "\nAge: ", p.age, "\nGender: ", p.gender)
p = Person(name="Alice", age=18);

println("Name: ", p.name, "\nAge: ", p.age, "\nGender: ", p.gender)


