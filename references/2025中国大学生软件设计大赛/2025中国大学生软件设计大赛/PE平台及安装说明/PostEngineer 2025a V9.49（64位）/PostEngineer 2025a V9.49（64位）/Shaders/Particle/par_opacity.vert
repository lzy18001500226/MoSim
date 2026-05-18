#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in vec3 position;
layout (location = 1) in float age;
layout (location = 2) in float randVal;
layout (location = 3) in float rotation;
layout (location = 4) in vec3 velocity;
layout (location = 5) in vec2 pipePosition;
layout (location = 6) in float type;
layout (location = 7) in float monther_age;


out vec3 position0;
out float age0;
out float randVal0;
out float rotation0;
out vec3 velocity0;
out vec2 pipePosition0;
out float type0;
out float monther_age0;


void main() 
{
    
    position0 = position;
    age0 = age;
    randVal0 = randVal;
    rotation0 = rotation;
	velocity0 = velocity;
	pipePosition0 = pipePosition;
	type0 = type;
	monther_age0 = monther_age;
}


